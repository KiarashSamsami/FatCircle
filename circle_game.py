import pygame
import sys
import math
import random


class Player:
    def __init__(self, color, x, y, radius):
        self.color = color
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def playermove(self, p):
        length = random.randint(WIDTH // 100, WIDTH // 20)
        tet = random.randint(0, 360) * math.pi / 180
        p.append((p[-1][0] + length * math.cos(tet), p[-1][1] + length * math.sin(tet)))
        self.x, self.y = p[-1]
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            tet = math.pi - tet
            newx = p[-1][0] + length * math.cos(tet)
            newy = p[-1][1] + length * math.sin(tet)
            p.append((newx, newy))
            self.x, self.y = newx, newy
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            tet = -tet
            newx = p[-1][0] + length * math.cos(tet)
            newy = p[-1][1] + length * math.sin(tet)
            p.append((newx, newy))
            self.x, self.y = newx, newy


pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle Game")

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

    player1.playermove(p1)
    player2.playermove(p2)

    player1.draw(screen)
    player2.draw(screen)

    pygame.display.flip()

    pygame.time.Clock().tick(100)

pygame.quit()
sys.exit()
