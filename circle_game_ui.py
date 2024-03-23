#! "D:\python projects\project 1\myenv\Scripts\python.exe"
import pygame
import sys
import math
import numpy as np


def get_intersect(seg1_start, seg1_end, seg2_start, seg2_end):
    print("wall is:")
    print(seg2_start, seg2_end)
    print("path is:")
    print(seg1_start, seg1_end)
    print("point of intersect is:")
    if abs(seg1_end[0] - seg1_start[0]) < 1e-9 and abs(seg2_start[0] - seg2_end[0]) < 1e-9:
        return None
    elif abs(seg1_end[0] - seg1_start[0]) < 1e-9:
        m2 = (seg2_end[1] - seg2_start[1]) / (seg2_end[0] - seg2_start[0])
        b2 = seg2_start[1] - m2 * seg2_start[0]
        point = [seg1_end[0], m2 * seg1_end[0] + b2]
    elif abs(seg2_start[0] - seg2_end[0]) < 1e-9:
        m1 = (seg1_end[1] - seg1_start[1]) / (seg1_end[0] - seg1_start[0])
        b1 = seg1_end[1] - m1 * seg1_end[0]
        point = [seg2_start[0], m1 * seg2_start[0] + b1]
    else:
        m2 = (seg2_end[1] - seg2_start[1]) / (seg2_end[0] - seg2_start[0])
        b2 = seg2_start[1] - m2 * seg2_start[0]
        m1 = (seg1_end[1] - seg1_start[1]) / (seg1_end[0] - seg1_start[0])
        b1 = seg1_end[1] - m1 * seg1_end[0]
        if abs(m1 - m2) < 1e-9:
            return None
        else:
            point_x = (b2 - b1) / (m1 - m2)
            point_y = m1 * point_x + b1
            point = [point_x, point_y]

    print(point)

    if (
            min(seg1_start[0], seg1_end[0]) - 1e-9 <= point[0] <= max(seg1_start[0], seg1_end[0]) + 1e-9
            and min(seg1_start[1], seg1_end[1]) - 1e-9 <= point[1] <= max(seg1_start[1], seg1_end[1]) + 1e-9
            and min(seg2_start[0], seg2_end[0]) - 1e-9 <= point[0] <= max(seg2_start[0], seg2_end[0]) + 1e-9
            and min(seg2_start[1], seg2_end[1]) - 1e-9 <= point[1] <= max(seg2_start[1], seg2_end[1]) + 1e-9
    ):
        return point
    else:
        return []


def distance_cal(start_x, start_y, end_x, end_y):
    return math.sqrt((start_x - end_x) ** 2 + (start_y - end_y) ** 2)


class Player:
    def __init__(self, color, x, y, radius):
        self.angle_to_mouse = None
        self.new_tet_dir = self.angle_to_mouse
        self.lastPwasInters = None
        self.lastIntersWallInd = None
        self.totalEatenIndices = []
        self.color = color
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = 1
        self.mouse_pos = pygame.mouse.get_pos()
        self.time_to_bounce = None

    def mouse_position(self):
        self.mouse_pos = pygame.mouse.get_pos()
        delta = pygame.Vector2(self.mouse_pos) - pygame.Vector2(self.x, self.y)
        self.angle_to_mouse = math.atan2(delta.y, delta.x)
        pygame.draw.line(screen, RED, (self.x, self.y), self.mouse_pos)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def player_move(self, p):
        wall_start_coordinates = [
            [0, 600, 600, 0],
            [0, 0, 600, 600]
        ]
        wall_end_coordinates = [
            [600, 600, 0, 0],
            [0, 600, 600, 0]
        ]

        wall_directions = [
            [1, 0, -1, 0],
            [0, 1, 0, -1]
        ]
        if self.lastPwasInters:
            if distance_cal(self.x, self.y, self.intersection_point[0], self.intersection_point[1]) < 1:
                self.time_to_bounce = 1
            end_point_x = self.intersection_point[0] + WIDTH * math.cos(self.new_tet_dir)
            end_point_y = self.intersection_point[1] + HEIGHT * math.sin(self.new_tet_dir)
            pygame.draw.line(screen, RED, self.intersection_point, (end_point_x, end_point_y))
        
        main_distance = distance_cal(self.x,self.y,self.mouse_pos[0],self.mouse_pos[1])
        if not self.time_to_bounce:
            self.speed = main_distance/10
            dx = math.cos(self.angle_to_mouse) * self.speed
            dy = math.sin(self.angle_to_mouse) * self.speed
            self.x += dx
            self.y += dy
        else:
            dx = math.cos(self.new_tet_dir) * self.speed
            dy = math.sin(self.new_tet_dir) * self.speed
            self.x += dx
            self.y += dy
            self.speed = main_distance/10
            if self.lastPwasInters:
                distance = distance_cal(self.x, self.y, self.intersection_point[0],self.intersection_point[1])
                length2traj = distance_cal(self.intersection_point[0],self.intersection_point[1],end_point_x,end_point_y)
                if length2traj-distance <= self.radius:
                    self.time_to_bounce = 0
                
            if not self.lastPwasInters:
                self.time_to_bounce = 0
        

        for i in range(4):
            print("iteration:", i)
            self.lastIntersWallInd = i
            wall_start = [wall_start_coordinates[0][i], wall_start_coordinates[1][i]]
            wall_end = [wall_end_coordinates[0][i], wall_end_coordinates[1][i]]
            print(wall_start, wall_end)
            self.intersection_point = get_intersect((self.x, self.y), self.mouse_pos, wall_start, wall_end)
            if self.intersection_point:
                print("wow! intersection Point!", self.intersection_point)
                self.lastPwasInters = 1
                self.lastIntersWallInd = i
                if not self.time_to_bounce:
                    this_wall_direction = [wall_directions[0][i], wall_directions[1][i]]
                    d = [math.cos(self.angle_to_mouse), math.sin(self.angle_to_mouse)]
                    V1 = d[0] * this_wall_direction[0] + d[1] * this_wall_direction[1]
                    V1 = [this_wall_direction[0] * V1, this_wall_direction[1] * V1]
                    V2 = [d[0] - V1[0], d[1] - V1[1]]
                    V2 = [-V2[0], -V2[1]]
                    d = [V1[0] + V2[0], V1[1] + V2[1]]
                    self.new_tet_dir = math.atan2(d[1], d[0])

                break
            else:
                self.lastPwasInters = 0


    def eat(self, p, food_pos_tot, food_pos_tot_flag):
        print(" len food is: ", len(food_pos_tot))
        eatenIndices = []
        for k in range(len(food_pos_tot)):
            dist = np.linalg.norm([food_pos_tot[k][0] - self.x, food_pos_tot[k][1] - self.y])
            if dist < 20:
                eatenIndices.append(k)
                food_pos_tot_flag[k] = -1
        self.totalEatenIndices.append(eatenIndices)
        for k in range(len(food_pos_tot)):
            if food_pos_tot_flag[k] == 1:
                pygame.draw.circle(screen, [0, 0, 255], (int(food_pos_tot[k][0]), int(food_pos_tot[k][1])), 2)


pygame.init()

WIDTH, HEIGHT = 601, 601
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle Game")

BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

player1 = Player(RED, 50, 300, 20)
# player2 = Player(BLUE, 550, 300, 20)

p1 = [(50, 300)]
# p2 = [(550, 300)]

food_pos_tot = []
food_pos_tot_flag = [1]*1600
totalEatenIndices = []
for i in range(40):
    for j in range(40):
        food_pos = (50 + (i * 500 / 40), 50 + (j * 500 / 40))
        food_pos_tot.append((food_pos[0], food_pos[1]))

player1.mouse_position()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    player1.player_move(p1)
    # player2.player_move(p2)
    player1.mouse_position()

    player1.eat(p1, food_pos_tot, food_pos_tot_flag)
    # player2.eat(p2, food_pos_tot, food_pos_tot_flag)

    player1.draw(screen)
    # player2.draw(screen)
    pygame.display.flip()

    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
