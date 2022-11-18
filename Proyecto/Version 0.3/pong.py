import pygame
import sys
import random

SCREEN_WITDH = 1280
SCREEN_HEIGHT = 960

BALL_WIDTH = 30
BALL_HEIGHT = 30

PADDEL_WIDTH = 10
PADELL_HEIGHT = 140


class Pong:
    def __init__(self) -> None:
        pygame.init()

        self.light_grey = (200, 200, 200)
        self.bg_color = pygame.Color('grey12')

        self.ball_speed_x = 7
        self.ball_speed_y = 7

        self.player_1_speed = 0
        # default AI comportation
        self.player_2_speed = 7
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((SCREEN_WITDH, SCREEN_HEIGHT))
        pygame.display.set_caption('Intelligent Pong')

        self.ball = pygame.Rect((SCREEN_WITDH / 2) - (BALL_WIDTH / 2),
                                (SCREEN_HEIGHT / 2) - (BALL_HEIGHT / 2), BALL_WIDTH, BALL_HEIGHT)

        self.player_1 = pygame.Rect(10, (SCREEN_HEIGHT / 2) -
                                    (PADELL_HEIGHT / 2), PADDEL_WIDTH, PADELL_HEIGHT)

        self.player_2 = pygame.Rect(SCREEN_WITDH - 20,  (SCREEN_HEIGHT / 2) -
                                    (PADELL_HEIGHT / 2),  PADDEL_WIDTH, PADELL_HEIGHT)

        self.render_game()

    def render_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.player_1_speed += 7
                    if event.key == pygame.K_UP:
                        self.player_1_speed -= 7
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.player_1_speed -= 7
                    if event.key == pygame.K_UP:
                        self.player_1_speed += 7

            self.ball_animation()
            self.player_1_animation()
            self.player_2_ai()

            self.screen.fill(self.bg_color)
            pygame.draw.rect(self.screen, self.light_grey, self.player_1)
            pygame.draw.rect(self.screen, self.light_grey, self.player_2)
            pygame.draw.ellipse(self.screen, self.light_grey, self.ball)
            pygame.draw.aaline(self.screen, self.light_grey, (SCREEN_WITDH/2,
                                                              0), (SCREEN_WITDH/2, SCREEN_HEIGHT))

            pygame.display.flip()
            self.clock.tick(60)

    def ball_restart(self):
        self.ball.center = (SCREEN_WITDH / 2, SCREEN_HEIGHT / 2)
        self.ball_speed_x *= random.choice((-1, 1))
        self.ball_speed_y *= random.choice((-1, 1))

    def ball_animation(self):

        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y

        if self.ball.top <= 0 or self.ball.bottom >= SCREEN_HEIGHT:
            self.ball_speed_y *= -1

        if self.ball.left <= 0 or self.ball.right >= SCREEN_WITDH:
            self.ball_restart()

        if self.ball.colliderect(self.player_1) or self.ball.colliderect(self.player_2):
            self.ball_speed_x *= -1

    def player_1_animation(self):
        self.player_1.y += self.player_1_speed

        if self.player_1.top <= 0:
            self.player_1.top = 0
        if self.player_1.bottom >= SCREEN_HEIGHT:
            self.player_1.bottom = SCREEN_HEIGHT

    def player_2_ai(self):
        if self.player_2.top < self.ball.y:
            self.player_2.top += self.player_2_speed
        if self.player_2.bottom > self.ball.y:
            self.player_2.bottom -= self.player_2_speed

        if self.player_2.top <= 0:
            self.player_2.top = 0
        if self.player_2.bottom >= SCREEN_HEIGHT:
            self.player_2.bottom = SCREEN_HEIGHT
