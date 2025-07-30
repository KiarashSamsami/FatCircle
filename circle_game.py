import pygame
import sys
import math
import random
import numpy as np

from geometry_utils import get_intersect, make_vector_from_tet, rotate_2d_vector




class Player:
    def __init__(self, color, x, y, radius, game):
        self.game = game
        self.y0 = None
        self.x0 = None
        self.trajLength = None
        self.lastPwasInters = None
        self.lastIntersWallInd = None
        self.totalEatenIndices = []
        self.color = color
        self.x = x
        self.y = y
        self.radius = radius
        self.total_run_length = 0
        self.current_tet = 0

        self.wall_start_coordinates = [self.game.WALL_START_X, self.game.WALL_START_Y]
        self.wall_end_coordinates = [self.game.WALL_END_X, self.game.WALL_END_Y]
        self.wall_directions = [self.game.WALL_DIRECTIONS_X, self.game.WALL_DIRECTIONS_Y]

 
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.line(screen, [0, 255, 0], (int(self.x), int(self.y)), (int(self.x0), int(self.y0)), 1)
        pygame.draw.circle(screen, [0, 255, 0], (int(self.x), int(self.y)), 1)
        pygame.draw.circle(screen, [0, 255, 0], (int(self.x0), int(self.y0)), 1)

    
    def obtain_new_dir(self, current_dir, turning_angle):

        
        if self.lastPwasInters:
            # If during the last run it had hit the wall, disregard the new turning angle and reflect from the wall:
            i = self.lastIntersWallInd
            this_wall_direction = [self.wall_directions[0][i], self.wall_directions[1][i]]
            V1 = current_dir[0] * this_wall_direction[0] + current_dir[1] * this_wall_direction[1]
            V1 = [this_wall_direction[0] * V1, this_wall_direction[1] * V1]
            V2 = [current_dir[0] - V1[0], current_dir[1] - V1[1]]
            V2 = [-V2[0], -V2[1]]
            new_dir = [V1[0] + V2[0], V1[1] + V2[1]]
        else:
            new_dir = rotate_2d_vector( alpha = turning_angle, d = current_dir)
        
        return new_dir


    def player_move(self, 
                    p: list, 
                    turn_angle_min: float, 
                    turn_angle_max: float,
                    run_dist_min: float,
                    run_dist_max: float):
        """
        Given a starting point, propagates the trajectory of a player given min/max values of turning angles and run lengths and 
        assuming Gaussian distributions for these parameters.
        """

        # Obtain new turning angle and run length:
        self.turning_tet = random.randint(int(turn_angle_min*180/np.pi), int(turn_angle_max*180/np.pi)) * np.pi/180
        run_length = random.randint(run_dist_min, run_dist_max)
        
        # Obtain new position:
        current_dir = make_vector_from_tet(self.current_tet)
        new_dir = self.obtain_new_dir(current_dir, self.turning_tet)
        self.current_tet = np.atan2(new_dir[1], new_dir[0]) # Update based on new dir
        p_new = (p[-1][0] + run_length * new_dir[0], p[-1][1] + run_length * new_dir[1])
        

        # Correct new position if goes beyond the domain:
        self.lastPwasInters = False
        for i in range(4):
            wall_start = [self.wall_start_coordinates[0][i], self.wall_start_coordinates[1][i]]
            wall_end = [self.wall_end_coordinates[0][i], self.wall_end_coordinates[1][i]]
            intersection_point = get_intersect(p[-1], p_new, wall_start, wall_end)
            if intersection_point:
                backoff = 1e-5
                p_new = (intersection_point[0] - new_dir[0]*backoff, intersection_point[1] - new_dir[1]*backoff)
                self.lastPwasInters = True
                self.lastIntersWallInd = i
                break



        # Update p, total run length, x, y, x0, y0:
        self.x0, self.y0 = p[-1]
        p.append((p_new[0], p_new[1]))
        self.x, self.y = p[-1]
        self.total_run_length += np.linalg.norm([ self.x0 - self.x, self.y0 -self.y]) 


    
    def eat(self, p, food_pos_tot, food_pos_tot_flag):
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
    def __init__(self, 
                 player_radius,
                 domain_length_x: float = 620,
                 domain_length_y: float = 620):
        """
        Initializes the Game class. 
        Args:
            Player_radius: Radius of the circle. 
            domain_length_x: Length of domain in the X direction.
            domain_length_y: Length of domain in the Y direction.
        """
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 15)
        self.WIDTH, self.HEIGHT = domain_length_x, domain_length_y
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.player_radius = player_radius
        pygame.display.set_caption("Circle Game")

        self.WINDOW_WIDTH = self.WIDTH - self.player_radius
        self.WINDOW_HEIGHT = self.HEIGHT - self.player_radius
        

        # Coordinates of the 4 wall corners, (bottom left, bottom right, top right, top left)
        self.WALL_START_X = [player_radius, self.WINDOW_WIDTH, self.WINDOW_WIDTH, player_radius]
        self.WALL_START_Y = [player_radius, player_radius, self.WINDOW_HEIGHT, self.WINDOW_HEIGHT]
        self.WALL_END_X = [self.WINDOW_WIDTH, self.WINDOW_WIDTH, player_radius, player_radius]
        self.WALL_END_Y = [player_radius, self.WINDOW_HEIGHT, self.WINDOW_HEIGHT, player_radius]
        self.WALL_DIRECTIONS_X = [1, 0, -1, 0]
        self.WALL_DIRECTIONS_Y = [0, 1, 0, -1]


    def create_player(self):
        RED = (255, 0, 0)
        player_radius = int(input("radius:"))
        p1_start = (input("first X location "), input("first y location"))
        player1 = Player(RED, *p1_start, player_radius)
        return player1, [p1_start], player_radius

    def create_food(self, 
                    food_grid_num_x: float = 40,
                    food_area_offset: float = 10 ):
        """
        Creates a food grid, returns positions of food, and the total food count.
        """
        food_region_length = self.WIDTH - 2 * food_area_offset
        food_spacing = food_region_length / food_grid_num_x
        food_pos_tot = []
        total_food_count = [1] * (food_grid_num_x ** 2)

        for i in range(food_grid_num_x):
            for j in range(food_grid_num_x):
                x = food_area_offset + (i * food_spacing)
                y = food_area_offset + (j * food_spacing)
                food_pos_tot.append((x, y))
        return food_pos_tot, total_food_count

    def game_loop(self, player1, first_pos, food_pos_tot, food_pos_tot_flag, ANGLE_MIN, ANGLE_MAX, run_min, run_max):
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

            player1.player_move(p1, ANGLE_MIN, ANGLE_MAX, run_min, run_max)

            foodExists = player1.eat(p1, food_pos_tot, food_pos_tot_flag)

            player1.draw(self.screen)

            distance_text = self.font.render(f"Total Distance: {int(player1.total_run_length)}", True, (255, 255, 255))
            self.screen.blit(distance_text, (10, 10))

            pygame.display.flip()

            pygame.time.Clock().tick(FPS)

            if not foodExists:
                print("All food eaten! Game over.")
                pygame.quit()
                running = False


def main():
    ANGLE_MIN = -30 * np.pi/180
    ANGLE_MAX = 30 * np.pi/180
    run_min = 30
    run_max = 60
    RED = (255, 0, 0)
    player_radius = 15
    game = Game(player_radius)
    food_pos_tot, food_pos_tot_flag = game.create_food(food_grid_num_x= 40, food_area_offset= 10)

    p1_start = (20, 20)
    player1 = Player(RED, *p1_start, player_radius, game)

    game.game_loop(player1, p1_start, food_pos_tot, food_pos_tot_flag, ANGLE_MIN, ANGLE_MAX, run_min, run_max)
    sys.exit()


if __name__ == "__main__":
    main()