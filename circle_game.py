import pygame
import sys
import math
import random
import numpy as np

# Compute the random walk per time-step:
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


class Player:
    def __init__(self, color, x, y, radius, game):
        self.game = game
        self.y0 = None
        self.x0 = None
        self.trajLength = None
        self.tet_dir = None
        self.lastPwasInters = None
        self.lastIntersWallInd = None
        self.totalEatenIndices = []
        self.color = color
        self.x = x
        self.y = y
        self.radius = radius
        self.totalDistance = 0
        self.tet = []

        self.wall_start_coordinates = [self.game.WALL_START_X, self.game.WALL_START_Y]
        self.wall_end_coordinates = [self.game.WALL_END_X, self.game.WALL_END_Y]
        self.wall_directions = [self.game.WALL_DIRECTIONS_X, self.game.WALL_DIRECTIONS_Y]

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.line(screen, [0, 255, 0], (int(self.x), int(self.y)), (int(self.x0), int(self.y0)), 1)
        pygame.draw.circle(screen, [0, 255, 0], (int(self.x), int(self.y)), 1)
        pygame.draw.circle(screen, [0, 255, 0], (int(self.x0), int(self.y0)), 1)

    def player_move(self, p, ANGLE_MIN, ANGLE_MAX):



        length = random.randint(self.game.WINDOW_WIDTH // 20, self.game.WINDOW_WIDTH // 10)
        self.totalDistance += length 
        self.tet.append(random.randint(ANGLE_MIN, ANGLE_MAX) * math.pi / 180)
        if len(p) * len(p[0]) > 2:
            if self.lastPwasInters == 1:
                i = self.lastIntersWallInd
                this_wall_direction = [self.wall_directions[0][i], self.wall_directions[1][i]]
                d = [math.cos(self.tet_dir), math.sin(self.tet_dir)]
                V1 = d[0] * this_wall_direction[0] + d[1] * this_wall_direction[1]
                V1 = [this_wall_direction[0] * V1, this_wall_direction[1] * V1]
                V2 = [d[0] - V1[0], d[1] - V1[1]]
                V2 = [-V2[0], -V2[1]]
                d = [V1[0] + V2[0], V1[1] + V2[1]]
                self.tet_dir = math.atan2(d[1], d[0])
            else:
                d = [math.cos(self.tet_dir), math.sin(self.tet_dir)]
                d = [math.cos(self.tet[-1]) * d[0] - math.sin(self.tet[-1]) * d[1],
                     math.sin(self.tet[-1]) * d[0] + math.cos(self.tet[-1]) * d[1]]
                self.tet_dir = math.atan2(d[1], d[0])
        else:
            d = [math.cos(self.tet[-1]), math.sin(self.tet[-1])]
            self.tet_dir = math.atan2(d[1], d[0])

        p_new = (p[-1][0] + length * d[0], p[-1][1] + length * d[1])

        intersection_flag = 0
        for i in range(4):
            print("iteration:", i)
            wall_start = [self.wall_start_coordinates[0][i], self.wall_start_coordinates[1][i]]
            wall_end = [self.wall_end_coordinates[0][i], self.wall_end_coordinates[1][i]]
            intersection_point = get_intersect(p[-1], p_new, wall_start, wall_end)
            if intersection_point:
                print("wow! intersection Point!", intersection_point)

                p_new = intersection_point
                t = np.linalg.norm([p_new[0] - p[-1][0], p_new[1] - p[-1][1]])
                t = t - 1e-5
                p_new = (p[-1][0] + t * d[0], p[-1][1] + t * d[1])
                p.append((p_new[0], p_new[1]))
                self.x, self.y = p[-1]
                intersection_flag = 1
                self.lastPwasInters = 1
                self.lastIntersWallInd = i
                break

        if intersection_flag == 0:
            p.append((p_new[0], p_new[1]))
            self.lastPwasInters = 0

        self.x, self.y = p[-1]
        self.x0, self.y0 = p[-2]
        self.trajLength = len(p)

        traj_norm = np.linalg.norm([p[-1][0]-p[-2][0],p[-1][1]-p[-2][1]])
        traj_hat = [(p[-1][0]-p[-2][0])/traj_norm,(p[-1][1]-p[-2][1])/traj_norm]
        traj_hat_normal = [-traj_hat[1], traj_hat[0]]
        traj_rect_1 = [p[-2][0]-traj_hat_normal[0],p[-2][1]-traj_hat_normal[1]]
        traj_rect_2 = [p[-2][0]+traj_hat_normal[0],p[-2][1]+traj_hat_normal[1]]
        traj_rect_3 = [p[-1][0]+traj_hat_normal[0],p[-1][1]+traj_hat_normal[1]]
        traj_rect_4 = [p[-1][0]-traj_hat_normal[0],p[-1][1]-traj_hat_normal[1]]
        traj_rect_start_coords = [
            [traj_rect_1[0],traj_rect_2[0],traj_rect_3[0],traj_rect_4[0]],
            [traj_rect_1[1],traj_rect_2[1],traj_rect_3[1],traj_rect_4[1]]
        ]
        traj_rect_end_coords = [
            [traj_rect_2[0],traj_rect_3[0],traj_rect_4[0],traj_rect_1[0]],
            [traj_rect_2[1],traj_rect_3[1],traj_rect_4[1],traj_rect_1[1]]
        ]

    def eat(self, p, food_pos_tot, food_pos_tot_flag, traj_rect_start_coords, traj_rect_end_coords):
        print(" len food is: ", len(food_pos_tot))
        foodExists = False
        eatenIndices = []
        
        for i in range(len(food_pos_tot)):
            if food_pos_tot_flag[i] == 1:
                dist = np.linalg.norm([food_pos_tot[i][0] - p[-1][0], food_pos_tot[i][1] - p[-1][1]])
                if dist < self.radius:
                    eatenIndices.append(i)
                    food_pos_tot_flag[i] = -1
        self.totalEatenIndices.append(eatenIndices)

        for i in range(len(food_pos_tot)):
            if food_pos_tot_flag[i] == 1:
                pygame.draw.circle(self.game.screen, [0, 0, 255], (int(food_pos_tot[i][0]), int(food_pos_tot[i][1])), 2)
                foodExists = True
        return foodExists

class Game:
    def __init__(self, player_radius):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 15)
        self.WIDTH, self.HEIGHT = 620, 620
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Circle Game")

        self.WINDOW_WIDTH = 600
        self.WINDOW_HEIGHT = 600
        self.player_radius = player_radius

        self.WALL_START_X = [player_radius, self.WINDOW_WIDTH, self.WINDOW_WIDTH, player_radius]
        self.WALL_START_Y = [player_radius, player_radius, self.WINDOW_HEIGHT, self.WINDOW_HEIGHT]
        self.WALL_END_X = [self.WINDOW_WIDTH, self.WINDOW_WIDTH, player_radius, player_radius]
        self.WALL_END_Y = [player_radius, self.WINDOW_HEIGHT, self.WINDOW_HEIGHT, player_radius]
        self.WALL_DIRECTIONS_X = [1, 0, -1, 0]
        self.WALL_DIRECTIONS_Y = [0, 1, 0, -1]



    def create_player(self):
        RED = (255,0,0)
        player_radius = int(input("radius:"))
        p1_start = (input("first X location "), input("first y location"))
        player1 = Player(RED, *p1_start, player_radius)
        #p2 = [(550, 300)]
        #player2 = Player(BLUE, 550, 300, 20)
        return player1, [p1_start], player_radius

    def create_food(self):
        FOOD_GRID_SIZE = int(input("Enter number of food per row/column (e.g. 40): "))
        FOOD_AREA_MARGIN = 50
        FOOD_AREA_SIZE = self.WIDTH - 2 * FOOD_AREA_MARGIN
        FOOD_SPACING = FOOD_AREA_SIZE / FOOD_GRID_SIZE

        food_pos_tot = []
        food_pos_tot_flag = [1] * (FOOD_GRID_SIZE ** 2)
        totalEatenIndices = []

        for i in range(FOOD_GRID_SIZE):
            for j in range(FOOD_GRID_SIZE):
                x = FOOD_AREA_MARGIN + (i * FOOD_SPACING)
                y = FOOD_AREA_MARGIN + (j * FOOD_SPACING)
                food_pos_tot.append((x, y))
        return food_pos_tot, food_pos_tot_flag

    def game_loop(self, player1, first_pos, food_pos_tot, food_pos_tot_flag, ANGLE_MIN, ANGLE_MAX):
        traj_rect_end_coords = [[0]*4, [0]*4]
        traj_rect_start_coords = [[0]*4, [0]*4]
        BLACK = (0, 0, 0)
        FPS = 30
        running = True 
        p1=[first_pos]
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.screen.fill(BLACK)

            player1.player_move(p1, ANGLE_MIN, ANGLE_MAX)
            # player2.player_move(p2)

            foodExists = player1.eat(p1, food_pos_tot, food_pos_tot_flag, traj_rect_start_coords, traj_rect_end_coords)
            # player2.eat(p2, food_pos_tot, food_pos_tot_flag)

            player1.draw(self.screen)
            # player2.draw(screen)

            distance_text = self.font.render(f"Total Distance: {int(player1.totalDistance)}", True, (255, 255, 255))
            self.screen.blit(distance_text, (10, 10))

            pygame.display.flip()

            pygame.time.Clock().tick(FPS)

            if not foodExists:
                print("🎉 All food eaten! Game over.")
                pygame.quit()
                running = False


def main():
    ANGLE_MIN = int(input("Enter minimum angle in degrees (e.g. -30): "))
    ANGLE_MAX = int(input("Enter maximum angle in degrees (e.g. 30): "))

    RED = (255, 0, 0)
    player_radius = int(input("Player radius: "))
    game = Game(player_radius)
    food_pos_tot, food_pos_tot_flag = game.create_food()

    p1_start = (int(input("Start X: ")), int(input("Start Y: ")))
    player1 = Player(RED, *p1_start, player_radius, game)

    game.game_loop(player1, p1_start, food_pos_tot, food_pos_tot_flag, ANGLE_MIN, ANGLE_MAX)
    sys.exit()


if __name__ == "__main__":
    main()