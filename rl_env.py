"""
Gymnasium-compatible RL wrapper for the FatCircle engine.

How to use:
    from rl_env import FatCircleRLEnv
    from fatcircle.core import Engine  # your deterministic engine (see protocol below)

    env = FatCircleRLEnv(engine=Engine(...), fixed_step_len=40.0)
    obs, info = env.reset()
    obs, reward, terminated, truncated, info = env.step(action)

Engine requirements (minimal protocol):
    The provided `engine` object must expose the following attributes/methods:
        # Scalar room geometry (floats)
        engine.W: float   # width  of the domain
        engine.H: float   # height of the domain

        # Agent pose (floats)
        engine.x: float
        engine.y: float
        engine.theta: float   # radians, any real value; engine maintains wrapping

        # Reset state. If start_pose is None and random_start=True, engine may randomize.
        def reset(self, *, start_pose: tuple[float, float, float] | None = None, rng=None) -> None: ...

        # Step dynamics. Must update (x, y, theta) internally and handle reflections + eating.
        # Returns a dict with at least keys: {"eaten": int, "collided": bool}
        def step(self, delta_theta: float, step_len: float) -> dict: ...

        # Number of remaining (uneaten) food points. Used to early-terminate.
        def foods_remaining(self) -> int: ...

Notes:
    • Reward = foods eaten this step − step_cost.
    • No termination on wall hit; the engine is expected to reflect inside the room.
    • Observations include: normalized position, heading (sin/cos), normalized wall distances, last turn, and time-left.
    • Action is continuous Δθ in [−turn_max, +turn_max]. Step length is fixed for Phase 1.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:  # fallback to classic gym if needed
    import gym  # type: ignore
    from gym import spaces  # type: ignore


@dataclass
class EnvConfig:
    max_steps: int = 2000
    fixed_step_len: float = 40.0
    turn_max: float = 0.5  # radians (action range will be [-turn_max, +turn_max])
    step_cost: float = 1e-3
    random_start: bool = True
    include_last_turn: bool = True
    include_time_left: bool = True


class FatCircleRLEnv(gym.Env):
    """Thin RL wrapper around a deterministic FatCircle engine.

    Observation vector (dtype=float32):
        [ x/W, y/H, sin(theta), cos(theta),
          dL_norm, dR_norm, dB_norm, dT_norm,
          (last_turn), (time_left) ]
        where wall distances are normalized by W or H respectively:
            dL = x / W, dR = (W - x) / W, dB = y / H, dT = (H - y) / H
        Optional fields (last_turn, time_left) are included depending on config.

    Action space:
        Box(low=[-turn_max], high=[+turn_max])  — continuous Δθ per step.
    """

    metadata = {"render_modes": ["human"], "name": "FatCircleRLEnv"}

    def __init__(self, engine, config: EnvConfig | None = None):
        super().__init__()
        if config is None:
            config = EnvConfig()
        self.cfg = config
        self.engine = engine

        # Build observation space shape dynamically based on config
        base_obs_dim = 4 + 4  # pos(2) + heading(2) + wall distances(4)
        extra = int(self.cfg.include_last_turn) + int(self.cfg.include_time_left)
        self._obs_dim = base_obs_dim + extra

        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(self._obs_dim,),
            dtype=np.float32,
        )

        self.action_space = spaces.Box(
            low=np.array([-self.cfg.turn_max], dtype=np.float32),
            high=np.array([+self.cfg.turn_max], dtype=np.float32),
            dtype=np.float32,
        )

        # Episode bookkeeping
        self._t = 0
        self._last_turn = 0.0
        self._rng: Optional[np.random.Generator] = None

    # ---------------- Gym API ---------------- #
    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        elif self._rng is None:
            self._rng = np.random.default_rng()

        start_pose: Optional[Tuple[float, float, float]] = None
        if options and "start_pose" in options:
            start_pose = tuple(options["start_pose"])  # (x, y, theta)

        # Delegate to engine to set initial state (randomized if desired)
        if self.cfg.random_start and start_pose is None:
            # Let engine randomize internally if it supports RNG; else we randomize here
            try:
                self.engine.reset(start_pose=None, rng=self._rng)
            except TypeError:
                # Fallback: randomize pose here if engine.reset doesn't accept rng
                x = float(self._rng.uniform(0.1 * self.engine.W, 0.9 * self.engine.W))
                y = float(self._rng.uniform(0.1 * self.engine.H, 0.9 * self.engine.H))
                theta = float(self._rng.uniform(-np.pi, np.pi))
                self.engine.reset(start_pose=(x, y, theta))
        else:
            self.engine.reset(start_pose=start_pose, rng=self._rng)

        self._t = 0
        self._last_turn = 0.0

        obs = self._make_obs()
        info = {"foods_remaining": int(self.engine.foods_remaining())}
        return obs, info

    def step(self, action):
        # Clip and unpack action (Δθ only; step length is fixed in Phase 1)
        a = float(np.clip(action[0], -self.cfg.turn_max, self.cfg.turn_max))
        res = self.engine.step(delta_theta=a, step_len=self.cfg.fixed_step_len)

        eaten = int(res.get("eaten", 0))
        collided = bool(res.get("collided", False))

        # Reward: foods eaten − small per-step cost (no explicit wall penalty since engine reflects)
        reward = float(eaten) - self.cfg.step_cost

        self._t += 1
        self._last_turn = a

        # Termination criteria
        terminated = False
        if hasattr(self.engine, "foods_remaining") and self.engine.foods_remaining() == 0:
            terminated = True

        truncated = self._t >= self.cfg.max_steps

        obs = self._make_obs()
        info = {
            "eaten": eaten,
            "collided": collided,
            "foods_remaining": int(self.engine.foods_remaining()),
            "t": self._t,
        }
        return obs, reward, terminated, truncated, info

    # -------------- Helpers -------------- #
    def _make_obs(self) -> np.ndarray:
        # Normalize position
        x_n = np.float32(self.engine.x / max(self.engine.W, 1e-6))
        y_n = np.float32(self.engine.y / max(self.engine.H, 1e-6))

        # Heading as sin/cos
        s = np.float32(np.sin(self.engine.theta))
        c = np.float32(np.cos(self.engine.theta))

        # Wall distances normalized per-axis
        dL = np.float32(self.engine.x / max(self.engine.W, 1e-6))
        dR = np.float32((self.engine.W - self.engine.x) / max(self.engine.W, 1e-6))
        dB = np.float32(self.engine.y / max(self.engine.H, 1e-6))
        dT = np.float32((self.engine.H - self.engine.y) / max(self.engine.H, 1e-6))

        vec = [x_n, y_n, s, c, dL, dR, dB, dT]

        if self.cfg.include_last_turn:
            # scale last_turn into [-1,1] by dividing by turn_max
            vec.append(np.float32(self._last_turn / max(self.cfg.turn_max, 1e-6)))
        if self.cfg.include_time_left:
            time_left = 1.0 - (self._t / max(self.cfg.max_steps, 1))
            vec.append(np.float32(time_left))

        return np.asarray(vec, dtype=np.float32)

    # -------------- Rendering stubs -------------- #
    def render(self):
        # Intentionally minimal — hook your pygame drawer here if desired.
        pass

    def close(self):
        pass
