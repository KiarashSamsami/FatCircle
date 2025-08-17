from dataclasses import dataclass

@dataclass(frozen=True)
class EnvConfig:
    """
    A dataclass representing an environment configuration.

    """
    width: float = 620.0
    height: float = 620.0
    agent_radius: float = 15.0
    max_steps: int = 10000  # safety cap
    reflect_backoff: float = 1e-6  # prevent re-collision

@dataclass(frozen=True)
class AgentConfig:
    turn_min: float = -30.0 * 3.141592653589793 / 180.0
    turn_max: float =  30.0 * 3.141592653589793 / 180.0
    step_min: float = 30.0
    step_max: float = 60.0
    start_x: float = 20.0
    start_y: float = 20.0
    start_heading: float = 0.0  # radians

@dataclass(frozen=True)
class FoodConfig:
    grid_nx: int = 40
    margin: float = 10.0
