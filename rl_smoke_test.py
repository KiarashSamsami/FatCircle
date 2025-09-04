from food_manager import FoodManager
from rl_env import FatCircleRLEnv, EnvConfig
from circle_game import BoxDomain, Player

import numpy as np

from single_engine import Engine

# Build your engine
domain = BoxDomain()
food_manager = FoodManager(width=domain.width)
food_manager.create_food(grid_size=40, offset=150.0)

player = Player(domain=domain, start_point=(110, 110), radius=100, color="red")
engine = Engine(domain=domain, player=player, food_manager=food_manager)

# Wrap with RL env
env = FatCircleRLEnv(engine=engine, config=EnvConfig())

obs, info = env.reset(seed=0)
done = False
while not done:
    action = env.action_space.sample()   # random Δθ in [-turn_max, turn_max]
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    print(obs, reward, info)
