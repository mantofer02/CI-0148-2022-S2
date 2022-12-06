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

SKIP_BUTTON_WIDTH = 140
SKIP_BUTTON_HEIGHT = 40

BALL_WIDTH = 30
BALL_HEIGHT = 30

PADEL_WIDTH = 10
PADEL_HEIGHT = 140

MAX_REWARD = 200
POINT_LOST = -100

BEST_POINT = 3

HUMAN = 1
AI = -1

UP = 1
DOWN = -1

PLAYER_1 = 1
PLAYER_2 = 2

# IA variables
MEMORY_CAPACITY = 10000
BATCH_SIZE = 50
C_ITERS = 30
LEARNING_RATE = 1e-5
DISCOUNT_FACTOR = 1e-3
EPS_GREEDY = 0.65
DECAY = 1e-8
IA_TRAINING_TICKS = 60
PALETTE_PENALIZATION_FACTOR = 1

global_player_1_score = 0
global_player_2_score = 0


class Action(enum.IntEnum):
    UP = 0
    DOWN = 1


class Pong:
    '''
        Clase que se encarga de la lógica del juego, asimismo
        como de el pase a atributos a la red neuronal
    '''

    def __init__(self) -> None:
        pygame.init()

        self.epoch = 0
        self.player_1_user = None
        self.player_2_user = None
        self.run_train = True
        self.threaning_thread = None

        self.game_started = False
        self.is_learning_center = False

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

        self.input_button = pygame.Rect(
            (SCREEN_WITDH / 2) - (SKIP_BUTTON_WIDTH / 2), 200, SKIP_BUTTON_WIDTH, SKIP_BUTTON_HEIGHT)

        # Learning Center
        self.input_button_text = ''
        self.n_simultations = 0

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
        self.load_model_img = pygame.image.load("images/button_load-model.png")
        self.download_model_img = pygame.image.load(
            "images/button_download-model.png")

        # IA
        self.agent_1 = agent.Agent(PLAYER_1, MEMORY_CAPACITY, BATCH_SIZE,
                                   C_ITERS, LEARNING_RATE, DISCOUNT_FACTOR, EPS_GREEDY, DECAY, 2)
        self.agent_2 = agent.Agent(PLAYER_2, MEMORY_CAPACITY, BATCH_SIZE,
                                   C_ITERS, LEARNING_RATE, DISCOUNT_FACTOR, EPS_GREEDY, DECAY, 2)
        self.run_ia_threads = False

        self.render_game()

    def display_menu(self):
        '''
            Método que se encarga de pintar el menú principal en la pantalla.
            También carga las imagenes.
        '''

        self.screen.fill(self.bg_color)

        pvp_button = Button(SCREEN_WITDH / 2 - 170,
                            SCREEN_HEIGHT / 2 - 300, self.pvp_img, 1)

        pvCPU_button = Button(SCREEN_WITDH / 2 - 143,
                              SCREEN_HEIGHT / 2 - 200, self.pvCPU_img, 1)

        CPUvCPU_button = Button(SCREEN_WITDH / 2 - 118,
                                SCREEN_HEIGHT / 2 - 100, self.CPUvCPU_img, 1)

        training_button = Button(SCREEN_WITDH / 2 - 180,
                                 SCREEN_HEIGHT / 2 + 0, self.training_img, 1)

        load_button = Button(SCREEN_WITDH / 2 - 118,
                             SCREEN_HEIGHT / 2 + 100, self.load_model_img, 1)

        download_button = Button(SCREEN_WITDH / 2 - 160,
                                 SCREEN_HEIGHT / 2 + 200, self.download_model_img, 1)

        pvp_button.draw(self.screen)
        pvCPU_button.draw(self.screen)
        CPUvCPU_button.draw(self.screen)
        training_button.draw(self.screen)
        load_button.draw(self.screen)
        download_button.draw(self.screen)
        pygame.display.flip()

    def menu_input(self, event):
        '''
            Escucha por un evento por el usuario y decide que opción del menú ejecutar

            Parameters:
            event (Any): Un evento que es equivalente a una accion del usuario.
        '''

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.game_paused = False
                self.is_learning_center = False
                self.player_1_user = HUMAN
                self.player_2_user = HUMAN
                self.player_1_speed = 0
                self.player_2_speed = 0
                self.score_time = pygame.time.get_ticks()

            elif event.key == pygame.K_2:
                self.game_paused = False
                self.is_learning_center = False
                self.player_1_user = HUMAN
                self.player_1_speed = 0
                self.player_2_user = AI
                self.player_2_speed = 9
                self.score_time = pygame.time.get_ticks()

            elif event.key == pygame.K_3:
                self.game_paused = False
                self.is_learning_center = False
                self.player_1_user = AI
                self.player_1_speed = 9
                self.player_2_user = AI
                self.player_2_speed = 9
                self.score_time = pygame.time.get_ticks()

            elif event.key == pygame.K_4:  # training button
                self.game_paused = False
                self.is_learning_center = True
                self.player_1_user = AI
                self.player_1_speed = 9
                self.player_2_user = AI
                self.player_2_speed = 9
                self.score_time = pygame.time.get_ticks()

            elif event.key == pygame.K_5:  # load button
                self.is_learning_center = False
                self.agent_1.load_model()
                self.agent_2.load_model()

            elif event.key == pygame.K_6:  # download button
                self.is_learning_center = False
                if global_player_1_score > global_player_2_score:
                    self.agent_1.download_model()
                else:
                    self.agent_2.download_model()
                print(global_player_1_score, global_player_2_score)

    def display_skip_button(self):
        '''
            Método que se encarga de pintar el boton de simulaciones en la pantalla.
        '''

        color = pygame.Color('darkorange3')

        pygame.draw.rect(self.screen, color, self.input_button)

        text_surface = self.game_font.render(
            self.input_button_text, False, self.light_grey)

        instruction_text = self.game_font.render(
            "Type amount of simulations then click on box", False, self.light_grey)

        self.input_button.w = max(
            SKIP_BUTTON_WIDTH, text_surface.get_width() + 10)

        self.screen.blit(
            text_surface, (self.input_button.x + 5, self.input_button.y + 5))

        self.screen.blit(instruction_text,
                         (self.input_button.x - 230, self.input_button.y - 50))

        if self.n_simultations > 0:
            simulation_text = self.game_font.render(
                "Simulations remaining: " + str(self.n_simultations), False, self.light_grey)

            self.screen.blit(simulation_text,
                             (self.input_button.x - 180, self.input_button.y + 50))

    def skip_button_input(self, event):
        '''
            Escucha por un evento por el usuario y lo toma como input para el 
            realizar simulaciones.

            Parameters:
            event (Any): Un evento que es equivalente a una accion del usuario.
        '''

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_button.collidepoint(event.pos):
                if len(self.input_button_text) > 0:
                    self.n_simultations = int(self.input_button_text)
                    self.input_button_text = ''
                    print(self.n_simultations)

                    if self.n_simultations > 0:
                        self.threaning_thread = Thread(
                            target=self.make_skip, args=(self.n_simultations,))
                        self.threaning_thread.start()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_button_text = self.input_button_text[:-1]
            else:
                try:
                    int(event.unicode)
                    self.input_button_text += event.unicode
                except:
                    print("Must add int")

    def display_pong(self):
        '''
            Método que se encarga de pintar las herramientas de pong 
            en la pantalla.
        '''

        self.ball_animation()
        ticks = 60
        if self.player_1_user == HUMAN:
            self.player_1_animation()

        if self.player_2_user == HUMAN:
            self.player_2_animation()
        elif self.player_2_user == AI and self.player_1_user == AI and not self.is_learning_center:
            if not self.run_ia_threads:
                self.run_ia_threads = True
                self.agent_1_thread = Thread(target=self.run_ia, args=(1,))
                self.agent_2_thread = Thread(target=self.run_ia, args=(2,))
                self.agent_1_thread.start()
                self.agent_2_thread = Thread(target=self.run_ia, args=(2,))
                self.agent_2_thread.start()
        elif self.player_2_user == AI and self.player_1_user == AI and self.is_learning_center:
            ticks = IA_TRAINING_TICKS
        elif self.player_2_user == AI and self.player_1_user == HUMAN:
            if not self.run_ia_threads:
                self.run_ia_threads = True
                self.agent_2_thread = Thread(target=self.run_ia, args=(2,))
                self.agent_2_thread.start()

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

        if self.is_learning_center:
            self.display_skip_button()

        self.screen.blit(player_1_text, (600, 20))
        self.screen.blit(player_2_text, (660, 20))

        pygame.display.flip()

        self.clock.tick(ticks)

    def player_1_human(self, event):
        '''
            Escucha por un evento del usuario y lo toma como input para mover
            la paleta del jugador 1.

            Parameters:
            event (Any): Un evento que es equivalente a una accion del usuario.
        '''

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.player_1_speed += 9
            elif event.key == pygame.K_UP:
                self.player_1_speed -= 9

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self.player_1_speed -= 9
            elif event.key == pygame.K_UP:
                self.player_1_speed += 9

    def player_2_human(self, event):
        '''
            Escucha por un evento del usuario y lo toma como input para mover
            la paleta del jugador 2.

            Parameters:
            event (Any): Un evento que es equivalente a una accion del usuario.
        '''

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                self.player_2_speed += 9
            elif event.key == pygame.K_w:
                self.player_2_speed -= 9

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                self.player_2_speed -= 9
            elif event.key == pygame.K_w:
                self.player_2_speed += 9

    def render_game(self):
        '''
            Se encarga de la logica de actualizar la pantalla 
            cada frame.
        '''

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Menu Trigger
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_paused = True
                        self.set_state_as_terminal()
                        self.display_menu()

                if self.is_learning_center and not self.game_paused:
                    self.skip_button_input(event)

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
        '''
            Resetea la posición de la bola
            al centro de la pantalla.
        '''
        number_render = None
        current_time = pygame.time.get_ticks()

        self.ball.center = (SCREEN_WITDH / 2, SCREEN_HEIGHT / 2)

        if self.score_time == None:
            self.score_time = 0

        if not self.is_learning_center:
            if current_time - self.score_time < 500:
                number_render = self.game_font.render(
                    "3", False, self.light_grey)
                self.screen.blit(number_render, (SCREEN_WITDH /
                                                 2 - 10, SCREEN_HEIGHT / 2 - 60))
            elif 500 <= current_time - self.score_time < 1000:
                number_render = self.game_font.render(
                    "2", False, self.light_grey)
                self.screen.blit(number_render, (SCREEN_WITDH /
                                                 2 - 10, SCREEN_HEIGHT / 2 - 60))
            elif 1000 <= current_time - self.score_time < 1500:
                number_render = self.game_font.render(
                    "1", False, self.light_grey)
                self.screen.blit(number_render, (SCREEN_WITDH /
                                                 2 - 10, SCREEN_HEIGHT / 2 - 60))

            if current_time - self.score_time < 1500:
                self.ball_speed_x, self.ball_speed_y = 0, 0
            else:
                self.ball_speed_x = 7 * random.choice((-1, 1))
                self.ball_speed_y = 7 * random.choice((-1, 1))
                self.score_time = None

        else:
            self.ball_speed_x = 7 * random.choice((-1, 1))
            self.ball_speed_y = 7 * random.choice((-1, 1))
            self.score_time = None

    def player_1_scores(self):
        '''
            Incrementa el puntaje del jugador 1.
        '''

        self.score_time = pygame.time.get_ticks()
        self.player_1_score += 1
        self.game_started = True

    def player_2_scores(self):
        '''
            Incrementa el puntaje del jugador 2.
        '''

        self.score_time = pygame.time.get_ticks()
        self.player_2_score += 1
        self.game_started = True

    def is_terminal_state(self):
        '''
            Pregunta si es un estado terminal.

            Returns:
            bool: True si es un estado terminal, si no devuelve False
        '''

        if self.player_1_score == BEST_POINT or self.player_2_score == BEST_POINT:
            return True
        else:
            return False

    def ball_animation(self):
        '''
            Se encarga de la logica de animación para la bola.
        '''

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
        '''
            Se encarga de la logica de animación para la paleta del jugador uno.
        '''
        self.player_1.y += self.player_1_speed

        if self.player_1.top <= 0:
            self.player_1.top = 0

        if self.player_1.bottom >= SCREEN_HEIGHT:
            self.player_1.bottom = SCREEN_HEIGHT

    def player_2_animation(self):
        '''
            Se encarga de la logica de animación para la paleta del jugador dos.
        '''
        self.player_2.y += self.player_2_speed

        if self.player_2.top <= 0:
            self.player_2.top = 0

        if self.player_2.bottom >= SCREEN_HEIGHT:
            self.player_2.bottom = SCREEN_HEIGHT

    def perform_action(self, action, id=None):
        '''
            Realiza una acción a un jugador especifico.
            La acción puede ser arriba o abajo

            Parameters:
            action (int): Enum para definir el tipo de acción
            id (int): Id para definir si es jugador 1 o 2.
        '''
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
        '''
            Obtiene el estado del jugador 1

            Parameters:
            state(int): (y distance to ball, y my position, y p2 position)
        '''

        return abs((self.ball.y + (BALL_WIDTH / 2)) - (self.player_1.y + (PADEL_HEIGHT / 2))), (self.player_1.y + (PADEL_HEIGHT / 2))

    def get_player_2_state(self):
        '''
            Obtiene el estado del jugador 2

            Parameters:
            state(int): (y distance to ball, y my position, y p1 position)
        '''
        return abs((self.ball.y + (BALL_WIDTH / 2)) - (self.player_2.y + (PADEL_HEIGHT / 2))), (self.player_2.y + (PADEL_HEIGHT / 2))

    def get_state(self, id=None):
        '''
            Obtiene el estado de un jugador en especifico

            Parameters:
            id(int): id del estado del jugador que quiere obtener
        '''

        if id == PLAYER_1:
            return self.get_player_1_state()
        else:
            return self.get_player_2_state()

    def get_y_distance_to_ball(self, id):
        '''
            Obtiene la distancia y de la paleta de un jugador hacia la bola

            Parameters:
            distance(int): distancia absoluta.
        '''
        player_y_pos = self.player_1.y if id == 1 else self.player_2.y
        return abs((self.ball.y + (BALL_WIDTH / 2)) - (player_y_pos + (PADEL_HEIGHT / 2)))

    def get_player_1_reward(self):
        '''
            Obtiene la recompensa del jugador 1 en un momento dado.

            Returns:
            reward(int): Valor de la recompensa (variables definidas con macros).
        '''
        global global_player_1_score

        actual_state = list(self.get_player_1_state())
        distance_to_ball = actual_state[0]
        touch_reward = 0
        penalty = 0

        if self.get_y_distance_to_ball(1) < PADEL_HEIGHT / 2 and self.ball.left <= self.player_1.right + PADEL_WIDTH:
            touch_reward = MAX_REWARD / 2
            # print('1-Entra al tocar')
        elif self.get_y_distance_to_ball(1) > PADEL_HEIGHT:
            penalty = POINT_LOST

        score = ((MAX_REWARD - PALETTE_PENALIZATION_FACTOR *
                 distance_to_ball) + touch_reward + penalty)
        if self.is_learning_center:
            global_player_1_score += score/100000

        return score

    def get_player_2_reward(self):
        '''
            Obtiene la recompensa del jugador 2 en un momento dado.

            Returns:
            reward(int): Valor de la recompensa (variables definidas con macros).
        '''
        global global_player_2_score
        actual_state = list(self.get_player_2_state())
        distance_to_ball = actual_state[0]

        touch_reward = 0
        penalty = 0

        if self.get_y_distance_to_ball(2) < PADEL_HEIGHT / 2 and self.ball.right >= self.player_2.left - PADEL_WIDTH:
            touch_reward = MAX_REWARD / 2
            # print('2 Entra al tocar')
        elif self.get_y_distance_to_ball(2) > PADEL_HEIGHT:
            penalty = POINT_LOST

        score = ((MAX_REWARD - PALETTE_PENALIZATION_FACTOR *
                 distance_to_ball) + touch_reward + penalty)
        if self.is_learning_center:
            global_player_2_score += score/100000

        return score

    def get_reward(self, id=None):
        '''
            Obtiene la recompensa de un jugador en un momento dadro

            Parameters:
            id(int): id del jugador que desea obtener la recompensa.

            Returns:
            reward(int): Valor de la recompensa (variables definidas con macros).
        '''
        if id == PLAYER_1:
            return self.get_player_1_reward()
        else:
            return self.get_player_2_reward()

    def reset(self):
        '''
            Resetea las posiciones y puntos de los jugadores.
        '''
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
            print('skip:', sim, "/", simulations,
                  ' elapsed time: ', time.time() - start_time)
            self.n_simultations -= 1

            if not self.is_learning_center:
                break

        self.reset()

    def run_ia(self, id_agent):
        agent = self.agent_1 if id_agent == 1 else self.agent_2
        self.reset()
        while not self.is_terminal_state():
            agent.step(self, learn=False)
            # time.sleep(0.1)

        if id_agent == 1:
            self.agent_2_thread.join()
            self.run_ia_threads = False

    def set_state_as_terminal(self):
        '''
            Define al estado como terminal.
        '''
        self.player_1_score = BEST_POINT
        self.player_2_score = BEST_POINT
        self.is_learning_center = False
