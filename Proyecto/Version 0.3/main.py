import pygame
import sys
import random

SCREEN_WITDH = 1280
SCREEN_HEIGHT = 960

BALL_WIDTH = 30
BALL_HEIGHT = 30

PADDEL_WIDTH = 10
PADELL_HEIGHT = 140


def ball_restart():
    global ball_speed_x, ball_speed_y
    ball.center = (SCREEN_WITDH / 2, SCREEN_HEIGHT / 2)
    ball_speed_x *= random.choice((-1, 1))
    ball_speed_y *= random.choice((-1, 1))


def ball_animation():
    global ball_speed_x, ball_speed_y

    ball.x += ball_speed_x
    ball.y += ball_speed_y

    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_speed_y *= -1

    if ball.left <= 0 or ball.right >= SCREEN_WITDH:
        ball_restart()

    if ball.colliderect(player_1) or ball.colliderect(player_2):
        ball_speed_x *= -1


def player_1_animation():
    player_1.y += player_1_speed

    if player_1.top <= 0:
        player_1.top = 0
    if player_1.bottom >= SCREEN_HEIGHT:
        player_1.bottom = SCREEN_HEIGHT


def player_2_ai():
    if player_2.top < ball.y:
        player_2.top += player_2_speed
    if player_2.bottom > ball.y:
        player_2.bottom -= player_2_speed

    if player_2.top <= 0:
        player_2.top = 0
    if player_2.bottom >= SCREEN_HEIGHT:
        player_2.bottom = SCREEN_HEIGHT


pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WITDH, SCREEN_HEIGHT))
pygame.display.set_caption('Intelligent Pong')

ball = pygame.Rect((SCREEN_WITDH / 2) - (BALL_WIDTH / 2),
                   (SCREEN_HEIGHT / 2) - (BALL_HEIGHT / 2), BALL_WIDTH, BALL_HEIGHT)

player_1 = pygame.Rect(10, (SCREEN_HEIGHT / 2) -
                       (PADELL_HEIGHT / 2), PADDEL_WIDTH, PADELL_HEIGHT)

player_2 = pygame.Rect(SCREEN_WITDH - 20,  (SCREEN_HEIGHT / 2) -
                       (PADELL_HEIGHT / 2),  PADDEL_WIDTH, PADELL_HEIGHT)

bg_color = pygame.Color('grey12')
light_grey = (200, 200, 200)

ball_speed_x = 7
ball_speed_y = 7
player_1_speed = 0

# default AI comportation
player_2_speed = 7

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player_1_speed += 7
            if event.key == pygame.K_UP:
                player_1_speed -= 7
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player_1_speed -= 7
            if event.key == pygame.K_UP:
                player_1_speed += 7

    ball_animation()
    player_1_animation()
    player_2_ai()

    screen.fill(bg_color)
    pygame.draw.rect(screen, light_grey, player_1)
    pygame.draw.rect(screen, light_grey, player_2)
    pygame.draw.ellipse(screen, light_grey, ball)
    pygame.draw.aaline(screen, light_grey, (SCREEN_WITDH/2,
                       0), (SCREEN_WITDH/2, SCREEN_HEIGHT))

    pygame.display.flip()
    clock.tick(60)
