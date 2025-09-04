# make_video_inline.py
# ------------------------------------------------------------
# Create an MP4 of a trained FatCircle policy rolling out.
# Requires:
#   pip install "stable-baselines3" imageio imageio-ffmpeg pygame
# ------------------------------------------------------------
import sys
import numpy as np
import imageio.v2 as imageio
import pygame
from stable_baselines3 import PPO

# === Import your sim pieces ===
from circle_game import BoxDomain, Player
from food_manager import FoodManager
from rl_env import FatCircleRLEnv, EnvConfig
from single_engine import Engine


def make_env():
    domain = BoxDomain()
    fm = FoodManager(width=domain.width)
    fm.create_food(grid_size=40, offset=150.0)  # same setup you trained with

    player = Player(domain=domain, start_point=(110, 110), radius=100, color="red")
    eng = Engine(domain=domain, player=player, food_manager=fm)
    # IMPORTANT: env.render() must NOT call close() every frame
    return FatCircleRLEnv(engine=eng, config=EnvConfig())


def main(model_path="ppo_fatcircle.zip", out="rollout.mp4", fps=30, seed=0, deterministic=True):
    print("[video] loading model:", model_path); sys.stdout.flush()
    model = PPO.load(model_path, device="cpu")

    print("[video] creating env…"); sys.stdout.flush()
    env = make_env()

    print("[video] reset env…"); sys.stdout.flush()
    obs, info = env.reset(seed=seed)

    # Initialize viewer by drawing once
    env.render()

    print("[video] opening writer:", out); sys.stdout.flush()
    writer = imageio.get_writer(out, fps=fps)

    done = False
    steps = 0
    print("[video] rolling out…"); sys.stdout.flush()
    while not done:
        action, _ = model.predict(obs, deterministic=deterministic)
        obs, reward, terminated, truncated, info = env.step(action)

        # draw to pygame window
        env.render()

        # capture the current frame from pygame
        surf = env._viewer.screen                     # created by your _PygameRenderer
        frame = pygame.surfarray.array3d(surf)        # (W, H, 3)
        frame = frame.swapaxes(0, 1).astype(np.uint8) # -> (H, W, 3)
        writer.append_data(frame)

        done = terminated or truncated
        steps += 1
        if steps % 50 == 0:
            print(f"[video] frames written: {steps}"); sys.stdout.flush()

    writer.close()
    env.close()
    print(f"[video] saved: {out} ({steps} frames)")


if __name__ == "__main__":
    # run with:  python -u make_video_inline.py
    main()
