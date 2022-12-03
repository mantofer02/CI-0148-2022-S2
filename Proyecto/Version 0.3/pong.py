import pygame
import sys
import random
from button import Button

SCREEN_WITDH = 1280
SCREEN_HEIGHT = 960

BALL_WIDTH = 30
BALL_HEIGHT = 30

PADEL_WIDTH = 10
PADEL_HEIGHT = 140

HUMAN = 1
AI = -1

UP = 1
DOWN = -1


class Pong:
    def __init__(self) -> None:
        pygame.init()

        self.player_1_user = None
        self.player_2_user = None

        self.light_grey = (200, 200, 200)
        self.bg_color = pygame.Color(0, 0, 0)

        self.ball_speed_x = 7
        self.ball_speed_y = 7

        self.player_1_speed = 0
        # default AI comportation
        # self.player_2_speed = 7

        self.player_2_speed = 0

        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((SCREEN_WITDH, SCREEN_HEIGHT))
        pygame.display.set_caption('Intelligent Pong')

        self.ball = pygame.Rect((SCREEN_WITDH / 2) - (BALL_WIDTH / 2),
                                (SCREEN_HEIGHT / 2) - (BALL_HEIGHT / 2), BALL_WIDTH, BALL_HEIGHT)

        self.player_1 = pygame.Rect(10, (SCREEN_HEIGHT / 2) -
                                    (PADEL_HEIGHT / 2), PADEL_WIDTH, PADEL_HEIGHT)

        self.player_2 = pygame.Rect(SCREEN_WITDH - 20, (SCREEN_HEIGHT / 2) -
                                    (PADEL_HEIGHT / 2), PADEL_WIDTH, PADEL_HEIGHT)

        # text variables
        self.player_1_score = 0
        self.player_2_score = 0
        self.game_font = pygame.font.Font("freesansbold.ttf", 32)

        # score timer

        self.game_paused = True
        self.score_time = True

        self.pvp_img = pygame.image.load("images/button_player-vs-player.png")
        self.pvCPU_img = pygame.image.load("images/button_player-vs-cpu.png")
        self.CPUvCPU_img = pygame.image.load("images/button_cpu-vs-cpu.png")

        self.render_game()

    def display_menu(self):
        self.screen.fill(self.bg_color)

        pvp_button = Button(SCREEN_WITDH / 2 - 170,
                            SCREEN_HEIGHT / 2 - 200, self.pvp_img, 1)

        pvCPU_button = Button(SCREEN_WITDH / 2 - 143,
                              SCREEN_HEIGHT / 2 - 100, self.pvCPU_img, 1)

        CPUvCPU_button = Button(SCREEN_WITDH / 2 - 118,
                                SCREEN_HEIGHT / 2, self.CPUvCPU_img, 1)

        pvp_button.draw(self.screen)
        pvCPU_button.draw(self.screen)
        CPUvCPU_button.draw(self.screen)
        pygame.display.flip()

    def menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.game_paused = False
                self.player_1_user = self.player_2_user = HUMAN
                self.score_time = pygame.time.get_ticks()

            elif event.key == pygame.K_2:
                self.game_paused = False
                self.player_1_user = HUMAN
                self.player_2_user = AI
                self.player_2_speed = 7
                self.score_time = pygame.time.get_ticks()

    def display_pong(self):
        self.ball_animation()

        if self.player_1_user == HUMAN:
            self.player_1_animation()

        if self.player_2_user == HUMAN:
            self.player_2_animation()
        elif self.player_2_user == AI:
            # self.player_2_ai()
            self.perform_action(UP)

        self.screen.fill(self.bg_color)
        pygame.draw.rect(self.screen, self.light_grey, self.player_1)
        pygame.draw.rect(self.screen, self.light_grey, self.player_2)
        pygame.draw.ellipse(self.screen, self.light_grey, self.ball)
        pygame.draw.aaline(self.screen, self.light_grey, (SCREEN_WITDH / 2,
                                                          0), (SCREEN_WITDH / 2, SCREEN_HEIGHT))

        if self.score_time:
            self.ball_restart()

        player_1_text = self.game_font.render(
            f"{self.player_1_score}", False, self.light_grey)

        player_2_text = self.game_font.render(
            f"{self.player_2_score}", False, self.light_grey)

        self.screen.blit(player_1_text, (600, 20))
        self.screen.blit(player_2_text, (660, 20))

        pygame.display.flip()
        self.clock.tick(60)

    def player_1_human(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.player_1_speed += 7
            elif event.key == pygame.K_UP:
                self.player_1_speed -= 7

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self.player_1_speed -= 7
            elif event.key == pygame.K_UP:
                self.player_1_speed += 7

    def player_2_human(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                self.player_2_speed += 7
            elif event.key == pygame.K_w:
                self.player_2_speed -= 7

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                self.player_2_speed -= 7
            elif event.key == pygame.K_w:
                self.player_2_speed += 7

    def render_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.game_paused:
                    self.menu_input(event)

                if self.player_1_user == HUMAN:
                    self.player_1_human(event)

                if self.player_2_user == HUMAN:
                    self.player_2_human(event)

            if self.game_paused:
                self.display_menu()
            else:
                # print(self.get_player_1_state())
                # print(self.get_player_2_state())
                # input()
                self.display_pong()

    def ball_restart(self):
        number_render = None
        current_time = pygame.time.get_ticks()

        self.ball.center = (SCREEN_WITDH / 2, SCREEN_HEIGHT / 2)

        if current_time - self.score_time < 500:
            number_render = self.game_font.render("3", False, self.light_grey)
            self.screen.blit(number_render, (SCREEN_WITDH /
                             2 - 10, SCREEN_HEIGHT / 2 - 60))
        elif 500 <= current_time - self.score_time < 1000:
            number_render = self.game_font.render("2", False, self.light_grey)
            self.screen.blit(number_render, (SCREEN_WITDH /
                             2 - 10, SCREEN_HEIGHT / 2 - 60))
        elif 1000 <= current_time - self.score_time < 1500:
            number_render = self.game_font.render("1", False, self.light_grey)
            self.screen.blit(number_render, (SCREEN_WITDH /
                             2 - 10, SCREEN_HEIGHT / 2 - 60))

        if current_time - self.score_time < 1500:
            self.ball_speed_x, self.ball_speed_y = 0, 0
        else:
            self.ball_speed_x = 7 * random.choice((-1, 1))
            self.ball_speed_y = 7 * random.choice((-1, 1))
            self.score_time = None

    def player_1_scores(self):
        self.score_time = pygame.time.get_ticks()
        self.player_1_score += 1

    def player_2_scores(self):
        self.score_time = pygame.time.get_ticks()
        self.player_2_score += 1

    def ball_animation(self):

        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y

        if self.ball.top <= 0 or self.ball.bottom >= SCREEN_HEIGHT:
            self.ball_speed_y *= -1

        if self.ball.left <= 0:
            self.player_2_scores()

        if self.ball.right >= SCREEN_WITDH:
            self.player_1_scores()

        if self.ball.colliderect(self.player_1):
            self.ball_speed_x *= -1

        if self.ball.colliderect(self.player_2):
            self.ball_speed_x *= -1

    def player_1_animation(self):
        self.player_1.y += self.player_1_speed

        if self.player_1.top <= 0:
            self.player_1.top = 0

        if self.player_1.bottom >= SCREEN_HEIGHT:
            self.player_1.bottom = SCREEN_HEIGHT

    def player_2_animation(self):
        self.player_2.y += self.player_2_speed

        if self.player_2.top <= 0:
            self.player_2.top = 0

        if self.player_2.bottom >= SCREEN_HEIGHT:
            self.player_2.bottom = SCREEN_HEIGHT

    def get_player_1_state(self):
        return abs((self.ball.x + (BALL_WIDTH / 2)) - (self.player_1.x + (PADEL_WIDTH / 2))), abs((self.ball.y + (BALL_WIDTH / 2)) - (self.player_1.y + (PADEL_HEIGHT / 2)))

    def get_player_2_state(self):
        return abs((self.ball.x + (BALL_WIDTH / 2)) - (self.player_2.x + (PADEL_WIDTH / 2))), abs((self.ball.y + (BALL_WIDTH / 2)) - (self.player_2.y + (PADEL_HEIGHT / 2)))

    def player_2_ai(self):
        if self.player_2.top < self.ball.y:
            self.player_2.top += self.player_2_speed

        if self.player_2.bottom > self.ball.y:
            self.player_2.bottom -= self.player_2_speed

        if self.player_2.top <= 0:
            self.player_2.top = 0

        if self.player_2.bottom >= SCREEN_HEIGHT:
            self.player_2.bottom = SCREEN_HEIGHT

    def perform_action(self, action):
        if action == DOWN:
            self.player_2.top += self.player_2_speed
        elif action == UP:
            self.player_2.bottom -= self.player_2_speed

        if self.player_2.top <= 0:
            self.player_2.top = 0

        if self.player_2.bottom >= SCREEN_HEIGHT:
            self.player_2.bottom = SCREEN_HEIGHT
