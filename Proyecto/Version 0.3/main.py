import pygame
import sys

SCREEN_WITDH = 1280
SCREEN_HEIGHT = 960

BALL_WIDTH = 30
BALL_HEIGHT = 30

PADDEL_WIDTH = 10
PADELL_HEIGHT = 140

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WITDH, SCREEN_HEIGHT))
pygame.display.set_caption('Intelligent Pong')

ball = pygame.Rect((SCREEN_WITDH / 2) - (BALL_WIDTH / 2),
                   (SCREEN_HEIGHT / 2) - (BALL_HEIGHT / 2), BALL_WIDTH, BALL_HEIGHT)

player_1 = pygame.Rect(SCREEN_WITDH - 20,  (SCREEN_HEIGHT / 2) -
                       (PADELL_HEIGHT / 2),  PADDEL_WIDTH, PADELL_HEIGHT)

player_2 = pygame.Rect(10, (SCREEN_HEIGHT / 2) -
                       (PADELL_HEIGHT / 2), PADDEL_WIDTH, PADELL_HEIGHT)

bg_color = pygame.Color('grey12')
light_grey = (200, 200, 200)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(bg_color)
    pygame.draw.rect(screen, light_grey, player_1)
    pygame.draw.rect(screen, light_grey, player_2)
    pygame.draw.ellipse(screen, light_grey, ball)
    pygame.draw.aaline(screen, light_grey, (SCREEN_WITDH/2,
                       0), (SCREEN_WITDH/2, SCREEN_HEIGHT))

    pygame.display.flip()
    clock.tick(60)
