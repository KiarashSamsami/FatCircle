import pygame
import sys
import math
import random


def get_intersect(seg1_start, seg1_end, wall_vector):
    # Unpack coordinates from tuples
    x1, y1 = seg1_start
    x2, y2 = seg1_end
    dx, dy = wall_vector[0]*600,wall_vector[1]*600

    # Calculate vectors for the line segment and wall
    seg_vec = (x2 - x1, y2 - y1)
    wall_vec = (dx, dy)

    # Calculate the cross product
    cross_product = seg_vec[0] * wall_vec[1] - seg_vec[1] * wall_vec[0]

    # Check if the line segment and wall are parallel or coincident
    if abs(cross_product) < 1e-6:  # Use a small tolerance for floating-point comparisons
        return None  # No intersection

    # Calculate the parameter for the line intersection
    t = cross_product / (seg_vec[0] * wall_vec[1] - seg_vec[1] * wall_vec[0])

    # Check if the intersection point is within the line segment and the wall
    if t >= 0 and t <= 1:
        # Calculate the intersection point coordinates
        x_int = x1 + t * seg_vec[0]
        y_int = y1 + t * seg_vec[1]
        return x_int, y_int  # Return the intersection point
    else:
        return None  # No intersection


class Player:
    def __init__(self, color, x, y, radius):
        self.color = color
        self.x = x
        self.y = y
        self.radius = radius
        self.tet = []

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def player_move(self, p):
        if len(self.tet) == 0:
            self.tet.append(0)

        length = random.randint(WIDTH // 20, WIDTH // 5)
        self.tet.append(random.randint(0, 360) * math.pi / 180)
        d = [math.cos(self.tet[-1]), math.sin(self.tet[-1])]
        p.append((p[-1][0] + length * math.cos(self.tet[-1]), p[-1][1] + length * math.sin(self.tet[-1])))
        self.x, self.y = p[-1]

        wall_collisions = [
            (left_wall, self.handle_left_wall_collision),
            (right_wall, self.handle_right_wall_collision),
            (top_wall, self.handle_top_wall_collision),
            (bottom_wall, self.handle_bottom_wall_collision)
        ]

        for wall, collision_handler in wall_collisions:
            intersection_point = get_intersect(p[-2], p[-1], wall)
            if intersection_point:
                self.x, self.y = intersection_point
                self.draw(screen)
                collision_handler(intersection_point, d, length)
                return

    def handle_left_wall_collision(self, intersection_point,d , length):
        p0 = intersection_point
        V1 = d[0] * left_wall[0] + d[1] * left_wall[1]
        V1 = [left_wall[0] * V1, left_wall[1] * V1]
        V2 = [d[0] - V1[0], d[1] - V1[1]]
        V2 = [-V2[0], -V2[1]]
        dnew = [V1[0] + V2[0], V1[1] + V2[1]]
        self.x, self.y = length*dnew[0] + p0[0], length*dnew[1] + p0[1]

    def handle_right_wall_collision(self,  intersection_point, d,length):
        p0 = intersection_point
        V1 = d[0] * right_wall[0] + d[1] * right_wall[1]
        V1 = [right_wall[0] * V1, right_wall[1] * V1]
        V2 = [d[0] - V1[0], d[1] - V1[1]]
        V2 = [-V2[0], -V2[1]]
        dnew = [V1[0] + V2[0], V1[1] + V2[1]]
        self.x, self.y = length*dnew[0] + p0[0], length*dnew[1] + p0[1]

    def handle_top_wall_collision(self,  intersection_point, d,length):
        p0 = intersection_point
        V1 = d[0] * top_wall[0] + d[1] * top_wall[1]
        V1 = [top_wall[0] * V1, top_wall[1] * V1]
        V2 = [d[0] - V1[0], d[1] - V1[1]]
        V2 = [-V2[0], -V2[1]]
        dnew = [V1[0] + V2[0], V1[1] + V2[1]]
        self.x, self.y = length*dnew[0] + p0[0], length*dnew[1] + p0[1]

    def handle_bottom_wall_collision(self,  intersection_point, d,length):
        p0 = intersection_point
        V1 = d[0] * bottom_wall[0] + d[1] * bottom_wall[1]
        V1 = [bottom_wall[0] * V1, bottom_wall[1] * V1]
        V2 = [d[0] - V1[0], d[1] - V1[1]]
        V2 = [-V2[0], -V2[1]]
        dnew = [V1[0] + V2[0], V1[1] + V2[1]]
        self.x, self.y = length*dnew[0] + p0[0], length*dnew[1] + p0[1]


pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle Game")

right_wall = (0, 1)
top_wall = (-1, 0)
left_wall = (0, -1)
bottom_wall = (1, 0)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

player1 = Player(RED, 50, HEIGHT // 2, 20)
player2 = Player(BLUE, WIDTH - 50, HEIGHT // 2, 20)

p1 = [(50, HEIGHT // 2)]
p2 = [(WIDTH - 50, HEIGHT // 2)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    player1.player_move(p1)
    player2.player_move(p2)

    player1.draw(screen)
    player2.draw(screen)

    pygame.display.flip()

    pygame.time.Clock().tick(1)

pygame.quit()
sys.exit()
