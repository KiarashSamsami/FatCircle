import numpy as np
import pygame
from scipy.spatial import cKDTree


class FoodManager:
    def __init__(self, width: float):
        self.width = width
        self.food_positions = None
        self.eaten_flags = None
        self.kdtree = None
        self.total_food_counts = None
        self.remaining_count = None

    def create_food(self, grid_size: int =40, offset: float = 250.0):
        region = self.width - 2 * offset
        spacing = region / grid_size
        coords = [
            (offset + i * spacing, offset + j * spacing)
            for i in range(grid_size)
            for j in range(grid_size)
        ]
        self.food_positions = np.array(coords)  # (N, 2)
        self.total_food_counts = self.food_positions.shape[0]
        self.remaining_count = self.total_food_counts
        self.eaten_flags = np.zeros(len(coords), dtype=bool)
        self.kdtree = cKDTree(self.food_positions)

    def eat_in_swept_region(self, start: tuple[float, float],
                                   end: tuple[float, float],
                                   radius: float):
        """
        Marks food as eaten within the swept region formed between start and end positions
        with given radius.
        """
        start = np.array(start)
        end = np.array(end)
        center = (start + end) / 2
        step_len = np.linalg.norm(end - start)

        # Query candidates in bounding circle
        candidates_idx = self.kdtree.query_ball_point(center, r=step_len / 2 + radius)

        eaten_now = []

        for idx in candidates_idx:
            if self.eaten_flags[idx]:
                continue  # Already eaten

            pos = self.food_positions[idx]
            if self._point_in_swept_region(pos, start, end, radius):
                self.eaten_flags[idx] = True
                self.remaining_count -= 1
                eaten_now.append(idx)

        return eaten_now  # Optionally return list of indices eaten

    @staticmethod
    def _point_in_swept_region(p: np.ndarray,
                               start: np.ndarray,
                               end: np.ndarray,
                               radius: float) -> bool:
        """
        Check if point p lies within the swept region:
        - Circle at start
        - Circle at end
        - Rectangle swept by moving a circle of radius between start and end
        """
        # Check start and end circles
        if np.linalg.norm(p - start) <= radius:
            return True
        if np.linalg.norm(p - end) <= radius:
            return True

        # Vector from start to end
        v = end - start
        len_v = np.linalg.norm(v)
        if len_v == 0:
            return False  # Degenerate case

        # Vector from start to point
        w = p - start

        # Project w onto v to find closest point on segment
        t = np.dot(w, v) / len_v**2
        if not (0 <= t <= 1):
            return False  # Closest point lies outside segment

        closest = start + t * v
        return np.linalg.norm(p - closest) <= radius

    def draw_food(self, screen):
        for pos, eaten in zip(self.food_positions, self.eaten_flags):
            color = (100, 100, 100) if eaten else (0, 100, 255)
            size = 1 if eaten else 3
            pygame.draw.circle(screen, color, pos.astype(int), radius=size)
