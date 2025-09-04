from stable_baselines3 import PPO

from circle_game import BoxDomain, Player
from food_manager import FoodManager
from rl_env import FatCircleRLEnv, EnvConfig
from single_engine import Engine


def make_env():
    domain = BoxDomain()
    food_manager = FoodManager(width=domain.width)
    food_manager.create_food(grid_size=40, offset=150.0)

    player = Player(domain=domain, start_point=(110, 110), radius=100, color="red")
    engine = Engine(domain=domain, player=player, food_manager=food_manager)
    return FatCircleRLEnv(engine=engine, config=EnvConfig())

env = make_env()

model = PPO("MlpPolicy", env, verbose=0)
model.learn(total_timesteps=int(1e9))

# Save and test
model.save("ppo_fatcircle")
obs, info = env.reset()

done = False
while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, _, terminated, truncated, _ = env.step(action)
    env.render()  # should draw the current player + foods
    done = terminated or truncated


env.close()   # <-- close once at the end
