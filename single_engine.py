import numpy as np

from circle_game import BoxDomain, Player
from food_manager import FoodManager
from geometry_utils import get_intersect

class Engine:
    """
    Minimal adapter to make your sim Gym-compatible for FatCircleRLEnv.
    It assumes a single controllable Player and a FoodManager.
    """
    def __init__(self, domain: BoxDomain, player: Player, food_manager: FoodManager):
        self.domain = domain
        self.player = player
        self.food_manager = food_manager

        # expose required scalars
        self.W = float(domain.W)
        self.H = float(domain.H)

        # internal bookkeeping
        self._collided_last = False

    # --- required scalar attributes (read via properties for live values) ---
    @property
    def x(self) -> float:
        return self.player.x

    @property
    def y(self) -> float:
        return self.player.y

    @property
    def theta(self) -> float:
        return self.player.theta

    # --- required protocol methods ---
    def reset(self, *, start_pose: tuple[float, float, float] | None = None, rng=None) -> None:
        if start_pose is None:
            # randomized start if requested by the RL env
            rng = rng or np.random.default_rng()
            r = float(self.player.radius)
            x = float(rng.uniform(r, self.W - r))
            y = float(rng.uniform(r, self.H - r))
            theta = float(rng.uniform(-np.pi, np.pi))
        else:
            x, y, theta = map(float, start_pose)

        self.player.set_pose(x, y, theta)
        self._collided_last = False

        # If you recreate food each episode, do it here:
        #TODO: Foodmanger gets initiated with values rather than these being reqrd by createa_food() (below)
        self.food_manager.create_food(grid_size=40, offset=150.0)
        # Otherwise ensure remaining_count reflects a fresh episode.

    def step(self, delta_theta: float, step_len: float) -> dict:
        """
        Deterministic step controlled by RL:
          - rotate current heading by delta_theta
          - move by step_len
          - reflect off walls if needed (your Player already supports reflection)
          - eat foods swept along the motion segment
        """
        # current heading → direction vector
        cur_theta = self.player.theta
        cur_dir = np.array([np.cos(cur_theta), np.sin(cur_theta)], dtype=float)

        # obtain new direction (respecting "reflect-next" logic if last move intersected)
        new_dir = self.player.obtain_new_dir(current_dir=cur_dir, turning_angle=float(delta_theta))
        new_dir = np.asarray(new_dir, dtype=float)
        new_dir /= (np.linalg.norm(new_dir) + 1e-12)

        p_old = (self.player.x, self.player.y)
        p_try = (p_old[0] + step_len * new_dir[0], p_old[1] + step_len * new_dir[1])

        # Check intersection against buffered walls (your code already does this)
        collided = False
        self.player.lastPwasInters = False
        for i in range(4):
            wall_start = [self.player.wall_start_coordinates[0][i], self.player.wall_start_coordinates[1][i]]
            wall_end   = [self.player.wall_end_coordinates[0][i],   self.player.wall_end_coordinates[1][i]]
            inter = get_intersect(p_old, p_try, wall_start, wall_end)
            if inter:
                # move just before the wall, mark collision so obtain_new_dir() reflects next step
                backoff = 1e-5
                p_new = (inter[0] - new_dir[0]*backoff, inter[1] - new_dir[1]*backoff)
                self.player.lastPwasInters = True
                self.player.lastIntersWallInd = i
                collided = True
                break
        else:
            p_new = p_try

        # Update pose (+ wrap theta like a real engine would)
        self.player.trajectory.append(p_new)
        self.player.current_tet = float(np.arctan2(new_dir[1], new_dir[0]))
        # theta can be any real; if you want wrapping, keep accumulating and rely on sin/cos in obs,
        # or normalize here (both are fine). Example wrap:
        # self.player.current_tet = float((self.player.current_tet + np.pi) % (2*np.pi) - np.pi)

        # Eat food swept by the segment
        eaten_idx = self.food_manager.eat_in_swept_region(p_old, p_new, self.player.radius)
        eaten = len(eaten_idx)

        self._collided_last = collided
        return {"eaten": eaten, "collided": collided}

    def foods_remaining(self) -> int:
        return int(self.food_manager.remaining_count)

def main():
    domain = BoxDomain()
    food_manager = FoodManager(width=domain.width)
    food_manager.create_food(grid_size=40, offset=150.0)

    p1_start = (110, 110)
    player = Player(
        color="red",
        start_point=p1_start,
        radius=100,
        run_dist_min=50.0,   # not used by RL step
        run_dist_max=60.0,   # not used by RL step
        domain=domain,
    )

    engine = Engine(domain=domain, player=player, food_manager=food_manager)

    # RL env from the wrapper you pasted
    from rl_env import FatCircleRLEnv, EnvConfig
    env = FatCircleRLEnv(engine=engine, config=EnvConfig(
        max_steps=2000,
        fixed_step_len=40.0,
        turn_max=0.5,
        step_cost=1e-3,
        random_start=True,
        include_last_turn=True,
        include_time_left=True,
    ))

    obs, info = env.reset(seed=42)
    for _ in range(100):
        # sample a random action for a smoke test
        a = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(a)
        if terminated or truncated:
            break


if __name__ == "__main__":
    main()