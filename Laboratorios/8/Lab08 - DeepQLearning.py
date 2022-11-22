# -*- coding: utf-8 -*-
"""
@author: Blopa
"""


import collections
import enum
import numpy as np
from PIL import Image, ImageTk
import random
import time
import torch
from torch import nn, tensor
import tkinter.simpledialog
from torch.utils.data import Dataset, DataLoader
import copy
import matplotlib.pyplot as plt

try:
    import tkinter as tk
except ImportError:
    try:
        import Tkinter as tk
    except ImportError:
        print("Missing library: Tkinter, please install")

RANDOM_SEED = 21
SNAKE_SEED = 31337
WIDTH = 16
HEIGHT = 24
INIT_LENGTH = 3
INIT_MOVES = 256
INIT_DIRECTION = 0
EXTRA_MOVES = 128

# TODO: CUSTOMIZE THE REWARDS
EMPTY_REWARD = 20
APPLE_REWARD = 100
WALL_REWARD = 0
SELF_REWARD = 0

# UI related
FPS = 24
APS = 8

DEVICE = torch.device("cuda:0")

colors = {
    0: (0, 0, 0),
    1: (255, 255, 128),
    2: (0, 255, 0),
    3: (255, 0, 0)
}


class Dset(torch.utils.data.Dataset):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.n_samples = x.shape[0]

    def __getitem__(self, index):
        return self.x[index], self.y[index]

    def __len__(self):
        return self.n_samples


class MemoryElement():
    def __init__(self, state, action, new_state, reward):
        self.state = state
        self.action = action
        self.new_state = new_state
        self.reward = reward

# TODO: Setear los parámetros


class DQL_NN(torch.nn.Module):
    def __init__(self, actions_number):
        super().__init__()
        # Primera convolución
        # Entra una imagen 3x24x16
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=10, kernel_size=(
            5, 5), stride=1, padding='same')
        # Sale una imagen de 10x24x16
        self.relu1 = nn.ReLU()
        self.maxpool1 = nn.MaxPool2d(2)
        # Imagen de 10x12x8

        # Segunda convolución
        # Entra una imagen de 10x12x8
        self.conv2 = nn.Conv2d(in_channels=10, out_channels=30, kernel_size=(
            5, 5), stride=1, padding='same')
        # Sale una imagen de 30x12x8
        self.relu2 = nn.ReLU()
        self.maxpool2 = nn.MaxPool2d(2)
        # Sale una imagen de 30x6x4 => vector de 720

        # Red neuronal
        self.fc1 = nn.Linear(720, 500)
        self.act1 = nn.ReLU()
        self.fc2 = nn.Linear(500, actions_number)
        # Se utiliza sigmoide porque CrossEntropy realiza una acción similar a la softmax, además, da mejores resultados
        self.act2 = nn.Tanh()

    def forward(self, x):
        ''' Sobre escritura del método de forward propagation, aplicando las capas convolucionales
            y luego las capas densas de la red neuronal'''
        # aplicación de la primera convolución
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.maxpool1(x)

        # aplicación de la segunda convolución
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.maxpool2(x)

        # aplanamiento de los datos
        x = torch.flatten(x, 1)

        # Ejecución en la red neuroral
        h = self.act1(self.fc1(x))
        out = self.act2(self.fc2(h))

        return out

# TODO: CUSTOMIZE AGENT


class Agent():
    # Initializes the training model
    # Input states for the model depend on the get_state method, which can be modified
    def __init__(self, memory_capacity, batch_size, c_iters, learning_rate, discount_factor, eps_greedy, decay):
        self.prng = random.Random()
        self.prng.seed(RANDOM_SEED)
        self.memory_capacity = memory_capacity
        self.batch_size = batch_size
        self.c_iters = c_iters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.eps_greedy = eps_greedy
        self.decay = decay
        self.samples = np.array([])
        self.actions = [_.value for _ in Action]

        # Redes neuronales
        self.target_nn = DQL_NN(len(self.actions)).to(DEVICE)
        self.policy_nn = DQL_NN(len(self.actions)).to(DEVICE)
        self.opt = torch.optim.Adam(
            self.policy_nn.parameters(), lr=learning_rate)
        self.loss_func = torch.nn.MSELoss()
        self.losses = []

    # Performs a complete simulation by the agent, then samples "batch" memories from memory and learns, afterwards updates the decay
    def simulation(self, env):
        env.reset()  # se resetea el ambiente
        steps = 0

        while(not env.is_terminal_state()):  # Mientras no se esté en un estado terminal
            steps += 1
            self.step(env, True)
            if steps % self.c_iters:
                # actualizar pesos en la red target
                self.target_nn = copy.deepcopy(self.policy_nn)
        self.eps_greedy = self.eps_greedy/(1 + self.decay)

    # Performs a single step of the simulation by the agent, if learn=False memories are not stored
    def step(self, env='Snake', learn=True):
        action = 0
        # Elegir inicialmente la mejor acción conocida
        random = self.prng.random()
        state = env.get_state()
        reward = 0
        target = 0
        if learn and random < self.eps_greedy:
            # elegir una acción al azar
            action = self.prng.choice(self.actions)
            state = env.get_state()
            reward, new_state = env.perform_action(action)
            if env.is_terminal_state():
                target = reward
                new_state = None
            else:
                new_state = new_state.to(DEVICE)
                target = reward + self.discount_factor * \
                    torch.max(self.target_nn(
                        new_state[None, :]))  # target = R(s’) + γ · maxa’ Q(s’,a’)
                new_state = new_state.cpu()
            # Para la red se transforman los valores a valores entre [-1, 1]
            reward = reward/100
            target = target/100

            if len(self.samples) > self.memory_capacity:
                self.samples = self.samples[: (len(self.samples) - 1)]

            self.samples = np.append(self.samples, MemoryElement(
                state, action, new_state, reward))
            # Aquí se ejecuta el aprendizaje al aproximar los valores de la salida
            x_train, y_train = self.get_train_dset()  # .to(DEVICE)
            # train_loader = DataLoader(dataset= train_dset, batch_size= self.batch_size if len(self.samples) > self.batch_size else len(self.samples), shuffle= True)

            self.policy_nn.train()

            y_pred = self.policy_nn(x_train.to(DEVICE))
            loss = self.loss_func(y_pred, y_train.detach().to(DEVICE))

            self.opt.zero_grad()
            loss.backward()
            self.opt.step()
            self.losses.append(loss.item())

        else:  # seleccionar la mejor acción conocida
            actions = self.target_nn(env.get_state()[None, :].to(DEVICE))
            action = torch.argmax(actions)
            reward, new_state = env.perform_action(action.item())

        if reward < 0:  # Entra a celda color negro
            return True

        return False
        # TODO: Implement single step, if learn=False no updates are performed and the best action is always taken

    def get_train_dset(self):

        memory_set = []
        size = self.batch_size - \
            1 if len(self.samples) > self.batch_size else len(self.samples)
        if len(self.samples) > 0:
            index = np.random.randint(0, len(self.samples), size)
            memory_set = self.samples[index]

        x_memory = tensor([])
        y_memory = tensor([])
        for _tuple in memory_set:

            y_true = tensor(_tuple.reward) if _tuple.new_state == None else _tuple.reward + self.discount_factor * torch.max(
                self.target_nn(_tuple.new_state[None, :].to(DEVICE)))  # target = reward else target = R(s’) + γ · maxa’ Q(s’,a’)
            y_true_tuple = self.target_nn(_tuple.state[None, :].to(DEVICE))
            y_true_tuple[0][_tuple.action] = (y_true.item()/100)

            x_memory = torch.cat((x_memory, _tuple.state))
            y_memory = torch.cat((y_memory, y_true_tuple.cpu()))

        return x_memory.reshape(len(self.samples), 3, 24, 16), y_memory

    def print_losses(self):
        # Impresión de gráficos y resultados del modelo
        len_ = len(self.losses)
        xpoints = np.linspace(0, len_, num=len_)
        plt.plot(xpoints, self.losses)
        plt.xlabel("Epochs")
        plt.ylabel("Loss")
        plt.title(("Pérdida DQL"))
        plt.show()


class Action(enum.IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Snake():
    def __init__(self, seed=SNAKE_SEED):
        self.prng = random.Random()
        self.seed = seed
        self.reset()

    def get_score(self):
        return self.score

    # Resets the environment
    def reset(self):
        self.prng.seed(self.seed)
        self.board = np.zeros((HEIGHT, WIDTH))
        self.valid_positions = set((i, j)
                                   for i in range(HEIGHT) for j in range(WIDTH))
        self.positions = collections.deque([])
        for i in range(INIT_LENGTH):
            self.positions.append(((HEIGHT//2)+i, WIDTH//2))
            self.board[self.positions[-1]] = 1 + int(i == 0)
        self.direction = 0  # 0 = UP, 1 = RIGHT, 2 = DOWN, 3 = LEFT
        self.moves_left = INIT_MOVES
        self.dead = False
        self.score = 0
        self.__add_apple()

    def __add_apple(self):
        options = list(self.valid_positions - set(self.positions))
        if not options:
            return False
        apple = self.prng.choice(options)
        self.board[apple] = 3
        self.apple_position = apple
        return True

    # Returns action list
    def get_actions(self):
        return [a.value for a in Action]

    # TODO(OPTIONAL): CAN BE MODIFIED; CURRENTLY RETURNS TENSOR OF SHAPE (3, WIDTH, HEIGHT)
    def get_state(self):
        snake = torch.zeros((HEIGHT, WIDTH), dtype=torch.float32)
        head = torch.zeros((HEIGHT, WIDTH), dtype=torch.float32)
        apple = torch.zeros((HEIGHT, WIDTH), dtype=torch.float32)
        for pos in self.positions:
            snake[pos] = 1
        head[self.positions[-1]] = 1
        apple[self.apple_position] = 1
        state = torch.stack((snake, head, apple))
        return state

    # Returns whether current state is terminal
    def is_terminal_state(self):
        return self.dead or self.moves_left <= 0

    # Performs an action and returns its reward and the new state
    def perform_action(self, action):
        reward = EMPTY_REWARD
        if abs(self.direction - action) != 2:
            self.direction = action
        tail = self.positions.pop()
        self.board[tail] = 0
        if self.direction % 2 == 0:
            head = (
                self.positions[0][0] + (-1 if self.direction == 0 else 1), self.positions[0][1])
            if head[0] < 0 or head[0] >= HEIGHT:
                self.dead = True
                reward = WALL_REWARD
        else:
            head = (self.positions[0][0], self.positions[0]
                    [1] + (-1 if self.direction == 3 else 1))
            if head[1] < 0 or head[1] >= WIDTH:
                self.dead = True
                reward = WALL_REWARD
        if not self.dead:
            self.board[self.positions[0]] = 1
            self.positions.appendleft(head)
            value = self.board[head]
            self.board[head] = 2
            if value < 3 and value > 0:
                self.dead = True
                reward = SELF_REWARD
            if value == 3:
                self.board[tail] = 1
                self.positions.append(tail)
                if not self.__add_apple():
                    self.dead = True
                self.score += 1
                reward = APPLE_REWARD
        return reward, self.get_state()


class mainWindow():
    def __init__(self, agentCls=Agent):
        self.snake = Snake()
        self.agentCls = agentCls
        # Control
        self.redraw = False
        self.playing_user = False
        self.playing_agent = False
        self.last_direction = 0
        self.last_action = 0
        self.epoch = 0
        self.score = 0
        self.highscore = 0
        self.memory_capacity = 10000
        self.batch_size = 1000
        self.c_iters = 10
        self.learning_rate = 0.001
        self.discount = 0.25
        self.greedy = 0.25
        self.decay = 1e-7
        self.agent = agentCls(self.memory_capacity, self.batch_size, self.c_iters,
                              self.learning_rate, self.discount, self.greedy, self.decay)
        # Interface
        self.root = tk.Tk()
        self.root.title("Snake AI")
        self.root.bind("<Configure>", self.resizing_event)
        self.root.bind("<Key>", self.key_press_event)
        self.frame = tk.Frame(self.root, width=650, height=550)
        self.frame.pack()
        self.canvas = tk.Canvas(self.frame, width=1, height=1)
        # Control buttons
        self.buttonReset = tk.Button(
            self.frame, text="Reset", command=self.buttonReset_press, bg="indian red")
        self.buttonStep = tk.Button(
            self.frame, text="Step", command=self.buttonStep_press, bg="sea green")
        self.buttonSkip = tk.Button(
            self.frame, text="Skip", command=self.buttonSkip_press, bg="sea green")
        self.buttonPlayAgent = tk.Button(
            self.frame, text="Simulation", command=self.buttonPlayagent_press, bg="forest green")
        self.buttonPlayUser = tk.Button(
            self.frame, text="Play", command=self.buttonPlayuser_press, bg="forest green")
        self.epochString = tk.StringVar(value="Episodes: 0")
        self.scoreString = tk.StringVar(value="Score/Best: 0/0")
        self.epochLabel = tk.Label(
            self.frame, textvariable=self.epochString, relief=tk.RIDGE, padx=5, pady=2)
        self.scoreLabel = tk.Label(
            self.frame, textvariable=self.scoreString, relief=tk.RIDGE, padx=5, pady=2)
        self.mlLabel = tk.Label(
            self.frame, text="ML Controls:", relief=tk.RIDGE, padx=5, pady=2)
        self.humanLabel = tk.Label(
            self.frame, text="Entertainment for humans:", relief=tk.RIDGE, padx=5, pady=2)
        # Customization
        self.labelCustomization = tk.Label(
            self.frame, text="Customization", relief=tk.RIDGE, padx=5, pady=2)
        # Memory capacity, Batch size, Alpha learning rate, Gamma discount, Epsilon greedy
        self.stringMemorycap = tk.StringVar(
            value="Mem. capacity: "+str(self.memory_capacity))
        self.labelMemorycap = tk.Label(
            self.frame, textvariable=self.stringMemorycap, relief=tk.RIDGE, padx=5, pady=2)
        self.buttonMemorycap = tk.Button(
            self.frame, text="Set", command=self.buttonMemorycap_press, bg="sea green")
        self.stringBatchsize = tk.StringVar(
            value="Batch size: "+str(self.batch_size))
        self.labelBatchsize = tk.Label(
            self.frame, textvariable=self.stringBatchsize, relief=tk.RIDGE, padx=5, pady=2)
        self.buttonBatchsize = tk.Button(
            self.frame, text="Set", command=self.buttonBatchsize_press, bg="sea green")
        self.stringCiters = tk.StringVar(value="C-iters: "+str(self.c_iters))
        self.labelCiters = tk.Label(
            self.frame, textvariable=self.stringCiters, relief=tk.RIDGE, padx=5, pady=2)
        self.buttonCiters = tk.Button(
            self.frame, text="Set", command=self.buttonCiters_press, bg="sea green")
        self.stringAlphalr = tk.StringVar(
            value="α-learning: "+str(self.learning_rate))
        self.labelAlphalr = tk.Label(
            self.frame, textvariable=self.stringAlphalr, relief=tk.RIDGE, padx=5, pady=2)
        self.buttonAlphalr = tk.Button(
            self.frame, text="Set", command=self.buttonAlphalr_press, bg="sea green")
        self.stringGammadisc = tk.StringVar(
            value="γ-discount: "+str(self.discount))
        self.labelGammadisc = tk.Label(
            self.frame, textvariable=self.stringGammadisc, relief=tk.RIDGE, padx=5, pady=2)
        self.buttonGammadisc = tk.Button(
            self.frame, text="Set", command=self.buttonGammadisc_press, bg="sea green")
        self.stringEpsilongreedy = tk.StringVar(
            value="ε-greedy: "+str(self.greedy))
        self.labelEpsilongreedy = tk.Label(
            self.frame, textvariable=self.stringEpsilongreedy, relief=tk.RIDGE, padx=5, pady=2)
        self.buttonEpsilongreedy = tk.Button(
            self.frame, text="Set", command=self.buttonEpsilongreedy_press, bg="sea green")
        self.stringEtadecay = tk.StringVar(value="η-decay: "+str(self.decay))
        self.labelEtadecay = tk.Label(
            self.frame, textvariable=self.stringEtadecay, relief=tk.RIDGE, padx=5, pady=2)
        self.buttonEtadecay = tk.Button(
            self.frame, text="Set", command=self.buttonEtadecay_press, bg="sea green")
        # Start
        self.root.after(0, self.update_loop)
        self.root.mainloop()

    # Resizing event
    def resizing_event(self, event):
        if event.widget == self.root:
            self.redraw = True
            self.canvas_width = max(event.width - 250, 1)
            self.canvas_height = max(event.height - 40, 1)
            self.frame.configure(width=event.width, height=event.height)
            self.canvas.configure(width=self.canvas_width,
                                  height=self.canvas_height)
            self.canvas.place(x=20, y=20)
            if (WIDTH/HEIGHT)*self.canvas_height > self.canvas_width:
                self.board_width, self.board_height = self.canvas_width, int(
                    (HEIGHT/WIDTH)*self.canvas_width)
            else:
                self.board_height, self.board_width = self.canvas_height, int(
                    (WIDTH/HEIGHT)*self.canvas_height)
            self.board_offset_x, self.board_offset_y = (
                self.canvas_width - self.board_width)//2, (self.canvas_height - self.board_height)//2
            self.mlLabel.place(x=event.width - 210, y=20, width=200)
            self.epochLabel.place(x=event.width - 210, y=50)
            self.scoreLabel.place(x=event.width - 210, y=80)
            self.buttonReset.place(x=event.width - 195, y=110, width=50)
            self.buttonStep.place(x=event.width - 130, y=110, width=50)
            self.buttonSkip.place(x=event.width - 65, y=110, width=50)
            self.buttonPlayAgent.place(x=event.width - 155, y=145, width=100)
            self.humanLabel.place(x=event.width - 210, y=200, width=200)
            self.buttonPlayUser.place(x=event.width - 155, y=235, width=100)
            # Customization
            self.labelCustomization.place(
                x=event.width - 210, y=290, width=190)
            self.labelMemorycap.place(x=event.width - 210, y=320)
            self.buttonMemorycap.place(x=event.width - 50, y=320)
            self.labelBatchsize.place(x=event.width - 210, y=350)
            self.buttonBatchsize.place(x=event.width - 50, y=350)
            self.labelCiters.place(x=event.width - 210, y=380)
            self.buttonCiters.place(x=event.width - 50, y=380)
            self.labelAlphalr.place(x=event.width - 210, y=410)
            self.buttonAlphalr.place(x=event.width - 50, y=410)
            self.labelGammadisc.place(x=event.width - 210, y=440)
            self.buttonGammadisc.place(x=event.width - 50, y=440)
            self.labelEpsilongreedy.place(x=event.width - 210, y=470)
            self.buttonEpsilongreedy.place(x=event.width - 50, y=470)
            self.labelEtadecay.place(x=event.width - 210, y=500)
            self.buttonEtadecay.place(x=event.width - 50, y=500)

    # Key press event
    def key_press_event(self, event):
        self.direction = (event.keycode - 38) % 4

    # Update loop
    def update_loop(self):
        if time.time() - self.last_action >= 1/APS:
            if self.playing_user and self.direction >= 0:
                self.redraw = True
                self.last_direction = self.direction
                self.last_action = time.time()
                self.snake.perform_action(self.direction)
                if self.snake.is_terminal_state():
                    self.buttonPlayuser_press()
            elif self.playing_agent:
                self.redraw = True
                self.last_action = time.time()
                if not self.snake.is_terminal_state():
                    self.agent.step(self.snake, learn=False)
        if self.redraw:
            self.redraw_canvas()
        self.root.after(int(1000/FPS), self.update_loop)

    # Play User button
    def buttonPlayuser_press(self):
        if not self.playing_agent:
            self.playing_user = not self.playing_user
            self.buttonPlayUser.configure(text=("Stop" if self.playing_user else "Play"), bg=(
                "indian red" if self.playing_user else "forest green"))
            if self.playing_user:
                self.direction = -1
                self.last_direction = -10
                self.last_action = 0
                self.snake = Snake(seed=int(time.time()*1000))
                self.redraw = True

    # Resets the learning model
    def buttonReset_press(self):
        if self.playing_agent or self.playing_user:
            return
        self.snake = Snake()
        self.agent = self.agentCls(self.memory_capacity, self.batch_size, self.c_iters,
                                   self.learning_rate, self.discount, self.greedy, self.decay)
        self.epoch = 0
        self.score, self.highscore = 0, 0
        self.epochString.set("Episodes: %i" % (self.epoch,))
        self.scoreString.set("Score/Best: %i/%i" %
                             (self.score, self.highscore))
        self.redraw = True

    # Executes an epoch
    def buttonStep_press(self):
        if self.playing_agent or self.playing_user:
            return
        self.epoch += 1
        self.snake = Snake()
        self.agent.simulation(self.snake)
        self.score = self.snake.get_score()
        self.highscore = max(self.highscore, self.score)
        self.epochString.set("Episodes: %i" % (self.epoch,))
        self.scoreString.set("Score/Best: %i/%i" %
                             (self.score, self.highscore))
        self.redraw = True

    # Executes epochs until epoch X
    def buttonSkip_press(self):
        if self.playing_agent or self.playing_user:
            return
        x = tk.simpledialog.askinteger(
            "Run simulations", "How many simulations:", parent=self.root, minvalue=1, initialvalue=10)
        if x:
            for i in range(x):
                self.buttonStep_press()
            self.agent.print_losses()

    # Play Agent button
    def buttonPlayagent_press(self):
        if not self.playing_user:
            self.snake = Snake()
            self.playing_agent = not self.playing_agent
            self.buttonPlayAgent.configure(text=("Stop" if self.playing_agent else "Simulation"), bg=(
                "indian red" if self.playing_agent else "forest green"))
            self.redraw = True

    # Memory-cap button
    def buttonMemorycap_press(self):
        if self.playing_agent or self.playing_user:
            return
        x = tk.simpledialog.askinteger(
            "Memory capacity", "Input the memory capacity:", parent=self.root, minvalue=1)
        if x:
            self.memory_capacity = x
            self.stringMemorycap.set(
                "Mem. capacity: "+str(self.memory_capacity))
            self.buttonReset_press()

    # Batch-size button
    def buttonBatchsize_press(self):
        if self.playing_agent or self.playing_user:
            return
        x = tk.simpledialog.askinteger(
            "Memory capacity", "Input the batch size:", parent=self.root, minvalue=1)
        if x:
            self.batch_size = x
            self.stringBatchsize.set("Batch size: "+str(self.batch_size))
            self.buttonReset_press()

    # C-iters button
    def buttonCiters_press(self):
        if self.playing_agent or self.playing_user:
            return
        x = tk.simpledialog.askinteger(
            "C-iterations", "Input the c-iterations:", parent=self.root, minvalue=1)
        if x:
            self.c_iters = x
            self.stringCiters.set("C-iters: "+str(self.c_iters))
            self.buttonReset_press()

    # Alpha-lr button
    def buttonAlphalr_press(self):
        if self.playing_agent or self.playing_user:
            return
        x = tk.simpledialog.askfloat(
            "α Learning rate", "Input the learning rate:", parent=self.root, minvalue=0, maxvalue=1)
        if x:
            self.learning_rate = x
            self.stringAlphalr.set("α-learning: "+str(self.learning_rate))
            self.buttonReset_press()

    # Gamma-disc button
    def buttonGammadisc_press(self):
        if self.playing_agent or self.playing_user:
            return
        x = tk.simpledialog.askfloat(
            "γ Discount factor", "Input the discount factor:", parent=self.root, minvalue=0, maxvalue=1)
        if x:
            self.discount = x
            self.stringGammadisc.set("γ-discount: "+str(self.discount))
            self.buttonReset_press()

    # Epsilon-greedy button
    def buttonEpsilongreedy_press(self):
        if self.playing_agent or self.playing_user:
            return
        x = tk.simpledialog.askfloat(
            "ε Greedy", "Input the initial ε greedy value:", parent=self.root, minvalue=0, maxvalue=1)
        if x:
            self.greedy = x
            self.stringEpsilongreedy.set("ε-greedy: "+str(self.greedy))
            self.buttonReset_press()

    # Eta-decay button
    def buttonEtadecay_press(self):
        if self.playing_agent or self.playing_user:
            return
        x = tk.simpledialog.askfloat(
            "η Decay factor", "Input the η decay factor for ε:", parent=self.root, minvalue=0, maxvalue=1)
        if x:
            self.decay = x
            self.stringEtadecay.set("η-decay: "+str(self.decay))
            self.buttonReset_press()

    def redraw_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(
            0, 0, self.canvas_width, self.canvas_height, fill="#606060", width=0)
        pixels = np.array([[colors[y] for y in x] for x in self.snake.board])
        self.image = Image.fromarray(pixels.astype('uint8'), 'RGB')
        self.photo = ImageTk.PhotoImage(image=self.image.resize(
            (self.board_width, self.board_height), resample=Image.NEAREST))
        self.canvas.create_image(
            self.board_offset_x, self.board_offset_y, image=self.photo, anchor=tk.NW)
        dy = self.board_height / HEIGHT
        dx = self.board_width / WIDTH
        for i in range(1, HEIGHT):
            self.canvas.create_line(self.board_offset_x, self.board_offset_y+int(
                dy*i), self.board_offset_x+self.board_width, self.board_offset_y+int(dy*i))
        for i in range(1, WIDTH):
            self.canvas.create_line(self.board_offset_x + int(dx*i), self.board_offset_y,
                                    self.board_offset_x+int(dx*i), self.board_offset_y+self.board_height)
        self.canvas.create_rectangle(self.board_offset_x, self.board_offset_y, self.board_offset_x +
                                     self.board_width, self.board_offset_y+self.board_height, outline="#0000FF", width=3)
        self.redraw = False


if __name__ == "__main__":
    x = mainWindow()
