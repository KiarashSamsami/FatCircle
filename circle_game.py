
import pygame
import sys
import random
import numpy as np
import numpy.typing as npt
from food_manager import FoodManager
from geometry_utils import get_intersect, make_vector_from_tet, rotate_2d_vector, get_total_distance


class BoxDomain:
    """
    A class to define the size of the domain.

    """
    def __init__(self,
                 width: float = 1000.0,
                 height: float = 1000.0,
                 ):
        self.width = width
        self.height= height

        self.WINDOW_HEIGHT = self.height

        # Coordinates of the 4 wall corners, (bottom left, bottom right, top right, top left)
        self.WALL_START_X = [0 , width , width , 0 ]
        self.WALL_START_Y = [0 , 0 , height , height ]
        self.WALL_END_X = [width , width ,  0 , 0 ]
        self.WALL_END_Y = [0 , height , height , 0 ]
        self.WALL_DIRECTIONS_X = [1, 0, -1, 0]
        self.WALL_DIRECTIONS_Y = [0, 1, 0, -1]
        self.food_pos_tot = []
        self.total_food_count = 0

        #TODO: make walls be a dict with normal, start and end points for each wall (FOr future more complicated geometries)
        # wall_normals = np.array([[1,0], [0, 1], [-1, 0], [0, -1]])





class Player:
    def __init__(self,
                 domain: BoxDomain,
                 color,
                 start_point: tuple[float, float],
                 radius,
                 turn_angle_min: float = -0.5, #radians
                 turn_angle_max: float = 0.5,
                 run_dist_min: float = 10.0,
                 run_dist_max: float = 60.0,
                 ):

        self.radius = radius

        self.trajLength = None
        self.lastPwasInters = None
        self.lastIntersWallInd = None
        self.totalEatenIndices = []
        self.color = color
        self.trajectory = [start_point]
        self.current_tet = 0

        self.turn_angle_min = turn_angle_min
        self.turn_angle_max = turn_angle_max
        self.run_dist_min = run_dist_min
        self.run_dist_max = run_dist_max

        self.eaten_count = 0

        #TODO: Add invisible wall stuff here: (Seems like working good without?!)
        self.wall_start_coordinates = [domain.WALL_START_X, domain.WALL_START_Y]
        self.wall_end_coordinates = [domain.WALL_END_X, domain.WALL_END_Y]
        self.wall_directions = [domain.WALL_DIRECTIONS_X, domain.WALL_DIRECTIONS_Y]

 
    def draw(self, screen):
        current_pos = self.trajectory[-1]
        old_pos = self.trajectory[-2] if len(self.trajectory) > 1 else current_pos
        pygame.draw.circle(screen, self.color, current_pos, self.radius)
        pygame.draw.line(screen, [0, 255, 0], old_pos, current_pos, 3)
        pygame.draw.circle(screen, [0, 255, 0], old_pos, 2)


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


    def player_move(self):
        """
        Given a starting point, propagates the trajectory of a player given min/max values of turning angles and run lengths and 
        assuming Gaussian distributions for these parameters.
        """

        # Obtain new turning angle and run length:
        turning_angle = random.uniform(self.turn_angle_min, self.turn_angle_max)
        run_length = random.uniform(self.run_dist_min, self.run_dist_max)
        
        # Obtain new position:
        current_dir = make_vector_from_tet(self.current_tet)
        new_dir = self.obtain_new_dir(current_dir, turning_angle)
        self.current_tet = np.atan2(new_dir[1], new_dir[0]) # Update based on new dir
        p_new = (self.trajectory[-1][0] + run_length * new_dir[0], self.trajectory[-1][1] + run_length * new_dir[1])
        

        # Correct new position if goes beyond the domain:
        self.lastPwasInters = False
        for i in range(4):
            wall_start = [self.wall_start_coordinates[0][i], self.wall_start_coordinates[1][i]]
            wall_end = [self.wall_end_coordinates[0][i], self.wall_end_coordinates[1][i]]
            intersection_point = get_intersect(self.trajectory[-1], p_new, wall_start, wall_end)
            if intersection_point:
                backoff = 1e-5
                p_new = (intersection_point[0] - new_dir[0]*backoff, intersection_point[1] - new_dir[1]*backoff)
                self.lastPwasInters = True
                self.lastIntersWallInd = i
                break

        # Update trajectory:
        self.trajectory.append(p_new)


class Game:
    def __init__(self,
                 domain: BoxDomain,
                 show_gui: bool,
                 fps: int = 60,
                 ):
        """
        Initializes the Game class. 
        Args:

        """
        domain_width, domain_height = domain.width, domain.height
        self.show_gui = show_gui
        if self.show_gui:
                self.fps = fps
                pygame.init()
                pygame.font.init()
                self.font = pygame.font.SysFont(None, 15)
                self.screen = pygame.display.set_mode((domain.width, domain.height))
                pygame.display.set_caption("Circle Game")


    def game_loop(self, player1: Player, food_manager: FoodManager):


        running = True
        food_remains = food_manager.remaining_count > 0
        simulation_steps: int = 0
        while running and food_remains:
            if self.show_gui:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                self.screen.fill("black")
                player1.draw(self.screen)
                food_manager.draw_food(self.screen)
                pygame.display.flip()
                pygame.time.Clock().tick(self.fps)

            player1.player_move()
            eaten_now = food_manager.eat_in_swept_region(player1.trajectory[-2], player1.trajectory[-1], player1.radius)
            player1.eaten_count += len(eaten_now)
            food_remains = food_manager.remaining_count > 0
            simulation_steps += 1

            if not food_remains:
                print("All food eaten! Game over.")


        pygame.quit()
        return simulation_steps

def main():

    domain = BoxDomain()
    food_manager = FoodManager(width=domain.width)
    food_manager.create_food(grid_size=40, offset=10.0)
    game = Game(show_gui=True, domain=domain, fps=60)

    p1_start = (20, 20)
    player1 = Player(color = "red",
                     start_point=p1_start,
                     radius = 100,
                     run_dist_min = 50.0,
                     run_dist_max = 60.0,
                     domain=domain)

    final_step_count = game.game_loop(player1, food_manager)



    total_distance = get_total_distance(np.array(player1.trajectory))
    sys.exit()


if __name__ == "__main__":
    main()