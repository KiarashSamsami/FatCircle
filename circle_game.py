import pygame
import sys
import math
import random
import numpy as np



def get_intersect(seg1_start, seg1_end, seg2_start, seg2_end):

    print("wall is:")
    print(seg2_start,seg2_end)
    print("path is:")
    print(seg1_start,seg1_end)
    print("point of intersect is:")
    if abs(seg1_end[0] - seg1_start[0]) < 1e-9 and abs(seg2_start[0]-seg2_end[0])<1e-9:
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
        if abs(m1-m2)<1e-9:
            return None
        else:
            point_x = (b2 - b1) / (m1 - m2)
            point_y = m1 * point_x + b1
            point = [point_x, point_y]

    

    print(point)

    if (
        min(seg1_start[0], seg1_end[0])-1e-9 <= point[0] <= max(seg1_start[0], seg1_end[0])+1e-9
        and min(seg1_start[1], seg1_end[1])-1e-9 <= point[1] <= max(seg1_start[1], seg1_end[1])+1e-9
        and min(seg2_start[0], seg2_end[0])-1e-9 <= point[0] <= max(seg2_start[0], seg2_end[0])+1e-9
        and min(seg2_start[1], seg2_end[1])-1e-9 <= point[1] <= max(seg2_start[1], seg2_end[1])+1e-9
    ):
        return point
    else:
        return []
        



class Player:
    def __init__(self, color, x, y, radius):
        self.color = color
        self.x = x
        self.y = y
        self.radius = radius
        self.tet = []

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.line(screen, [0,255,0], (int(self.x), int(self.y)) , (int(self.x0), int(self.y0)),1 )
        pygame.draw.circle(screen, [0,255,0], (int(self.x), int(self.y)), 6)
        pygame.draw.circle(screen, [0,255,0], (int(self.x0), int(self.y0)), 4)

    def player_move(self, p):
        if len(self.tet) == 0:
            self.tet.append(0)
        wall_start_coordinates = [
            [0,600,600,0],
            [0,0,600,600]
        ]
        wall_end_coordinates = [
            [600,600,0,0],
            [0,600,600,0]
        ]

        wall_directions = [
            [1,0,-1,0],
            [0,1,0,-1]
        ]

        length = random.randint(WIDTH // 20, WIDTH // 10)
        self.tet.append(random.randint(-30, 30) * math.pi / 180)
        # self.tet.append(0)
        if len(p)*len(p[0])>2:
            if self.lastPwasInters==1:
                i = self.lastIntersWallInd
                this_wall_direction = [wall_directions[0][i],wall_directions[1][i]]
                d = [math.cos(self.tet_dir), math.sin(self.tet_dir)]
                V1 = d[0] * this_wall_direction[0] + d[1] * this_wall_direction[1]
                V1 = [this_wall_direction[0] * V1, this_wall_direction[1] * V1]
                V2 = [d[0] - V1[0], d[1] - V1[1]]
                V2 = [-V2[0], -V2[1]]
                d = [V1[0] + V2[0], V1[1] + V2[1]]
                # p_new = length*dnew[0] + p[-1][0], length*dnew[1] + p[-1][1]
                # p.append((p_new[0],p_new[1]))
                self.tet_dir = math.atan2(d[1],d[0])
            else:
                d = [math.cos(self.tet_dir), math.sin(self.tet_dir)]
                d = [math.cos(self.tet[-1])*d[0]-math.sin(self.tet[-1])*d[1],math.sin(self.tet[-1])*d[0]+math.cos(self.tet[-1])*d[1]]
                self.tet_dir = math.atan2(d[1],d[0])
        else:
            d = [math.cos(self.tet[-1]), math.sin(self.tet[-1])]
            self.tet_dir = math.atan2(d[1],d[0])

        p_new = (p[-1][0] + length*d[0] , p[-1][1] + length*d[1])

        intersection_flag = 0 ; 
        for i in range(4):
            print("iteration:",i)
            wall_start = [wall_start_coordinates[0][i],wall_start_coordinates[1][i]]
            wall_end = [wall_end_coordinates[0][i],wall_end_coordinates[1][i]]
            print(wall_start,wall_end)
            intersection_point = get_intersect(p[-1],p_new,wall_start,wall_end)
            if intersection_point:
                print("wow! intersection Point!",intersection_point)

                p_new = intersection_point
                t = np.linalg.norm([p_new[0]-p[-1][0],p_new[1]-p[-1][1]])
                t = t-1e-5
                p_new = (p[-1][0] + t*d[0] , p[-1][1] + t*d[1])
                p.append((p_new[0],p_new[1]))
                self.x, self.y = p[-1]
                intersection_flag = 1
                self.lastPwasInters = 1 
                self.lastIntersWallInd = i
                break

        if intersection_flag==0:
            p.append((p_new[0],p_new[1]))
            self.lastPwasInters = 0 

        self.x, self.y = p[-1]
        self.x0, self.y0 = p[-2]
        self.trajLength = len(p)

    #     wall_collisions = [
    #         (left_wall, self.handle_left_wall_collision),
    #         (right_wall, self.handle_right_wall_collision),
    #         (top_wall, self.handle_top_wall_collision),
    #         (bottom_wall, self.handle_bottom_wall_collision)
    #     ]

    #     for wall, collision_handler in wall_collisions:
    #         intersection_point = get_intersect(p[-2], p[-1], wall)
    #         if intersection_point:
    #             self.x, self.y = intersection_point
    #             self.draw(screen)
    #             collision_handler(intersection_point, d, length)
    #             return

    # def handle_left_wall_collision(self, intersection_point,d , length):
    #     p0 = intersection_point
    #     V1 = d[0] * left_wall[0] + d[1] * left_wall[1]
    #     V1 = [left_wall[0] * V1, left_wall[1] * V1]
    #     V2 = [d[0] - V1[0], d[1] - V1[1]]
    #     V2 = [-V2[0], -V2[1]]
    #     dnew = [V1[0] + V2[0], V1[1] + V2[1]]
    #     self.x, self.y = length*dnew[0] + p0[0], length*dnew[1] + p0[1]

    # def handle_right_wall_collision(self,  intersection_point, d,length):
    #     p0 = intersection_point
    #     V1 = d[0] * right_wall[0] + d[1] * right_wall[1]
    #     V1 = [right_wall[0] * V1, right_wall[1] * V1]
    #     V2 = [d[0] - V1[0], d[1] - V1[1]]
    #     V2 = [-V2[0], -V2[1]]
    #     dnew = [V1[0] + V2[0], V1[1] + V2[1]]
    #     self.x, self.y = length*dnew[0] + p0[0], length*dnew[1] + p0[1]

    # def handle_top_wall_collision(self,  intersection_point, d,length):
    #     p0 = intersection_point
    #     V1 = d[0] * top_wall[0] + d[1] * top_wall[1]
    #     V1 = [top_wall[0] * V1, top_wall[1] * V1]
    #     V2 = [d[0] - V1[0], d[1] - V1[1]]
    #     V2 = [-V2[0], -V2[1]]
    #     dnew = [V1[0] + V2[0], V1[1] + V2[1]]
    #     self.x, self.y = length*dnew[0] + p0[0], length*dnew[1] + p0[1]

    # def handle_bottom_wall_collision(self,  intersection_point, d,length):
    #     p0 = intersection_point
    #     V1 = d[0] * bottom_wall[0] + d[1] * bottom_wall[1]
    #     V1 = [bottom_wall[0] * V1, bottom_wall[1] * V1]
    #     V2 = [d[0] - V1[0], d[1] - V1[1]]
    #     V2 = [-V2[0], -V2[1]]
    #     dnew = [V1[0] + V2[0], V1[1] + V2[1]]
    #     self.x, self.y = length*dnew[0] + p0[0], length*dnew[1] + p0[1]


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
# player2 = Player(BLUE, WIDTH - 50, HEIGHT // 2, 20)

p1 = [(50, HEIGHT // 2)]
# p2 = [(WIDTH - 50, HEIGHT // 2)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    player1.player_move(p1)
    # player2.player_move(p2)

    player1.draw(screen)
    # player2.draw(screen)
    if player1.x>600 or player1.x<0 or player1.y>600 or player1.y<0:
        print(player1.trajLength)
        pygame.quit()
        


    pygame.display.flip()

    pygame.time.Clock().tick(1)

pygame.quit()
sys.exit()
