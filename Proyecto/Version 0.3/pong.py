import pygame
import sys
import random
from button import Button
import agent
from threading import Thread, Lock
import enum
import time
SCREEN_WITDH = 1280
SCREEN_HEIGHT = 960

BALL_WIDTH = 30
BALL_HEIGHT = 30

PADEL_WIDTH = 10
PADEL_HEIGHT = 140

MAX_REWARD = 100
POINT_LOST = -500

BEST_POINT = 3

HUMAN = 1
AI = -1

UP = 1
DOWN = -1

PLAYER_1 = 1
PLAYER_2 = 2

# IA variables
MEMORY_CAPACITY = 10000
BATCH_SIZE = 100
C_ITERS = 10
LEARNING_RATE = 1e-7
DISCOUNT_FACTOR = 1e-4
EPS_GREEDY = 0.65
DECAY = 1e-9
IA_TRAINING_TICKS = 60
PALETTE_PENALIZATION_FACTOR = 1

class Action(enum.IntEnum):
    UP = 0
    DOWN = 1


class Pong:
    def __init__(self) -> None:
        pygame.init()

        self.epoch = 0
        self.player_1_user = None
        self.player_2_user = None
        self.run_train = True
        self.threaning_thread = None

        self.game_started = False

        self.mutex = Lock()

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
        self.training_img = pygame.image.load("images/button_training.png")

        # IA
        self.agent_1 = agent.Agent(PLAYER_1, MEMORY_CAPACITY, BATCH_SIZE,
                                   C_ITERS, LEARNING_RATE, DISCOUNT_FACTOR, EPS_GREEDY, DECAY, 3)
        self.agent_2 = agent.Agent(PLAYER_2, MEMORY_CAPACITY, BATCH_SIZE,
                                   C_ITERS, LEARNING_RATE, DISCOUNT_FACTOR, EPS_GREEDY, DECAY, 3)

        self.render_game()

    def display_menu(self):
        self.screen.fill(self.bg_color)

        pvp_button = Button(SCREEN_WITDH / 2 - 170,
                            SCREEN_HEIGHT / 2 - 200, self.pvp_img, 1)

        pvCPU_button = Button(SCREEN_WITDH / 2 - 143,
                              SCREEN_HEIGHT / 2 - 100, self.pvCPU_img, 1)

        CPUvCPU_button = Button(SCREEN_WITDH / 2 - 118,
                                SCREEN_HEIGHT / 2, self.CPUvCPU_img, 1)
        training_button = Button(SCREEN_WITDH / 2 - 118,
                                 SCREEN_HEIGHT / 2 + 50, self.training_img, 0.2)
        pvp_button.draw(self.screen)
        pvCPU_button.draw(self.screen)
        CPUvCPU_button.draw(self.screen)
        training_button.draw(self.screen)
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
                self.player_2_speed = 9
                self.score_time = pygame.time.get_ticks()

            elif event.key == pygame.K_4:  # trainig button
                self.game_paused = False
                self.player_1_user = AI
                self.player_1_speed = 9
                self.player_2_user = AI
                self.player_2_speed = 9
                self.score_time = pygame.time.get_ticks()

    def display_pong(self):
        self.ball_animation()
        ticks = 60
        if self.player_1_user == HUMAN:
            self.player_1_animation()

        if self.player_2_user == HUMAN:
            self.player_2_animation()
        elif self.player_2_user == AI and self.player_1_user == AI:
            ticks = IA_TRAINING_TICKS
            # self.player_2_ai()
            # self.perform_action(UP)

        self.screen.fill(self.bg_color)
        pygame.draw.rect(self.screen, self.light_grey, self.player_1)
        pygame.draw.rect(self.screen, self.light_grey, self.player_2)
        pygame.draw.ellipse(self.screen, self.light_grey, self.ball)
        pygame.draw.aaline(self.screen, self.light_grey, (SCREEN_WITDH / 2,
                                                          0), (SCREEN_WITDH / 2, SCREEN_HEIGHT))

        player_1_text = self.game_font.render(
            f"{self.player_1_score}", False, self.light_grey)

        player_2_text = self.game_font.render(
            f"{self.player_2_score}", False, self.light_grey)

        self.screen.blit(player_1_text, (600, 20))
        self.screen.blit(player_2_text, (660, 20))

        pygame.display.flip()
        if self.run_train:
            self.threaning_thread = Thread(target=self.make_skip, args=(1000,))
            self.threaning_thread.start()
            self.run_train = False
        self.clock.tick(ticks)

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

                # Menu Trigger
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_paused = True
                        self.display_menu()

                if self.game_paused:
                    self.menu_input(event)

                if self.player_1_user == HUMAN:
                    self.player_1_human(event)

                if self.player_2_user == HUMAN:
                    self.player_2_human(event)

            if self.game_paused:
                self.display_menu()
            else:
                self.display_pong()
                self.is_terminal_state()
                if self.score_time:
                    self.ball_restart()

    def ball_restart(self):
        number_render = None
        current_time = pygame.time.get_ticks()

        self.ball.center = (SCREEN_WITDH / 2, SCREEN_HEIGHT / 2)

        # TODO: quitar esto y preguntar
        if self.score_time == None:
            self.score_time = 0

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
        self.game_started = True

    def player_2_scores(self):
        self.score_time = pygame.time.get_ticks()
        self.player_2_score += 1
        self.game_started = True

    def is_terminal_state(self):
        if self.player_1_score == BEST_POINT or self.player_2_score == BEST_POINT:
            return True
        else:
            return False

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

    def player_2_ai(self):
        if self.player_2.top < self.ball.y:
            self.player_2.top += self.player_2_speed

        if self.player_2.bottom > self.ball.y:
            self.player_2.bottom -= self.player_2_speed

        if self.player_2.top <= 0:
            self.player_2.top = 0

        if self.player_2.bottom >= SCREEN_HEIGHT:
            self.player_2.bottom = SCREEN_HEIGHT

    def perform_action(self, action, id=None):
        # print('Perform', Action.DOWN, action, action == Action.DOWN.name)
        if id == PLAYER_1:

            if action == Action.DOWN.name:
                self.player_1.top += self.player_1_speed
                # print('1 Entra en down')
            elif action == Action.UP.name:
                self.player_1.bottom -= self.player_1_speed

            if self.player_1.top <= 0:
                self.player_1.top = 0

            if self.player_1.bottom >= SCREEN_HEIGHT:
                self.player_1.bottom = SCREEN_HEIGHT

            return self.get_reward(id=id), self.get_player_1_state()
        else:

            if action == Action.DOWN.name:
                self.player_2.top += self.player_2_speed
                # print('2 Entra en down')
            elif action == Action.UP.name:
                self.player_2.bottom -= self.player_2_speed

            if self.player_2.top <= 0:
                self.player_2.top = 0

            if self.player_2.bottom >= SCREEN_HEIGHT:
                self.player_2.bottom = SCREEN_HEIGHT

            return self.get_reward(id=id), self.get_player_2_state()

    def get_player_1_state(self):
        # (x distance to ball, y distance to ball), (0, y my position), (0, y p2 position) (abs((self.ball.x + (BALL_WIDTH / 2)) - (self.player_1.x + (PADEL_WIDTH / 2)))
        return abs((self.ball.y + (BALL_WIDTH / 2)) - (self.player_1.y + (PADEL_HEIGHT / 2))), (self.player_1.y + (PADEL_HEIGHT / 2)), (self.player_2.y + (PADEL_HEIGHT / 2))

    def get_player_2_state(self):
        # (x distance to ball, y distance to ball), (0, y my position), (0, y p1 position) (abs((self.ball.x + (BALL_WIDTH / 2)) - (self.player_2.x + (PADEL_WIDTH / 2))),
        return abs((self.ball.y + (BALL_WIDTH / 2)) - (self.player_2.y + (PADEL_HEIGHT / 2))), (self.player_2.y + (PADEL_HEIGHT / 2)), (self.player_1.y + (PADEL_HEIGHT / 2))

    def get_state(self, id=None):
        if id == PLAYER_1:
            return self.get_player_1_state()
        else:
            return self.get_player_2_state()

    def get_player_1_reward(self):
        actual_state = list(self.get_player_1_state())
        distance_to_ball = actual_state[0]

        touch_reward = 0
        penalty = 0

        if self.ball.left == self.player_1.right:
            touch_reward = MAX_REWARD / 2

        if self.ball.left >= 0:
            penalty = POINT_LOST

        # print('Player 1: ', (MAX_REWARD - distance_to_ball), ' distance to ball', distance_to_ball)
        return ((MAX_REWARD - PALETTE_PENALIZATION_FACTOR * distance_to_ball) + touch_reward + penalty)

    def get_player_2_reward(self):
        actual_state = list(self.get_player_2_state())
        distance_to_ball = actual_state[0]
        # print('Player 2: ', (MAX_REWARD - distance_to_ball), ' distance to ball', distance_to_ball)
        touch_reward = 0
        penalty = 0

        if self.ball.right >= SCREEN_WITDH:
            penalty = POINT_LOST

        if self.ball.right == self.player_2.left:
            touch_reward = MAX_REWARD / 2

        return ((MAX_REWARD - PALETTE_PENALIZATION_FACTOR * distance_to_ball) + touch_reward + penalty)

    def get_reward(self, id=None):
        if id == PLAYER_1:
            return self.get_player_1_reward()
        else:
            return self.get_player_2_reward()

    def reset(self):
        self.player_1_score = 0
        self.player_2_score = 0
        self.player_1.y = (SCREEN_HEIGHT / 2) - (PADEL_HEIGHT / 2)
        self.player_2.y = (SCREEN_HEIGHT / 2) - (PADEL_HEIGHT / 2)
        # self.ball_restart()

    def make_step(self, lr=True):
        self.epoch += 1
        agent_1_thread = Thread(target=self.agent_1.simulation, args=(self, ))
        agent_1_thread.start()
        self.agent_2.simulation(self)
        agent_1_thread.join()

    def make_skip(self, simulations=1):
        start_time = time.time()
        for sim in range(simulations):
            start_time = time.time()
            self.make_step()
            print('skip:', sim, "/", simulations, ' elapsed time: ',time.time() - start_time)
        # TODO: este cambio en la variable lo hace el boton skip
        self.run_train = True
