# rl_config.py

import numpy as np
import itertools
import pickle
import random
import os

# ---- ACTION SPACE ----
angle_min_deg = -30
angle_max_deg = 30
length_min = 10
length_max = 70

ANGLES = [np.deg2rad(a) for a in range(angle_min_deg, angle_max_deg)]  # -30 to 29 deg
LENGTHS = list(range(length_min, length_max, 10))  # 10, 20, ..., 60

ALL_ACTIONS = list(itertools.product(ANGLES, LENGTHS))  # (angle_rad, length)

QTABLE_FILE = "q_table.pkl"

def load_q_table():
    if os.path.exists(QTABLE_FILE):
        with open(QTABLE_FILE, "rb") as f:
            return pickle.load(f)
    else:
        return {}  # Empty dict if not found

def save_q_table(q_table):
    with open(QTABLE_FILE, "wb") as f:
        pickle.dump(q_table, f)


# ---- STATE DEFINITION ----
def get_state(x, y, domain_width, domain_height, food_flags, grid_size=10):
    x_bin = int(x // grid_size)
    y_bin = int(y // grid_size)
    food_remaining = sum(1 for flag in food_flags if flag == 1)

    if food_remaining > 80:
        food_bin = 4
    elif food_remaining > 60:
        food_bin = 3
    elif food_remaining > 40:
        food_bin = 2
    elif food_remaining > 20:
        food_bin = 1
    else:
        food_bin = 0

    return (x_bin, y_bin, food_bin)

# ---- EPSILON-GREEDY POLICY ----
def choose_action(q_table, state, epsilon):
    if random.random() < epsilon:
        return random.choice(ALL_ACTIONS)
    
    # Exploitation: pick best action
    action_values = [q_table.get((state, action), 0) for action in ALL_ACTIONS]
    best_index = np.argmax(action_values)
    return ALL_ACTIONS[best_index]

