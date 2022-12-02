import random
import enum
import numpy as np
import neural_network
import torch
import copy
import matplotlib as plt

RANDOM_SEED = 0
DEVICE = torch.device("cuda:0")
CHOOSE_UMBRAL = 0.5
class Action(enum.IntEnum):
  UP = 0
  DOWN = 1

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
    self.target_nn = neural_network.DQL_NN(len(self.actions)).to(DEVICE)
    self.policy_nn = neural_network.DQL_NN(len(self.actions)).to(DEVICE)
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
      if (steps % self.c_iters) == 0:
        # actualizar pesos en la red target
        self.target_nn = copy.deepcopy(self.policy_nn)
    
    # Actualización del greedy
    self.eps_greedy = self.eps_greedy / (1 + self.decay)

  # Performs a single step of the simulation by the agent, if learn=False memories are not stored
  def step(self, env='Pong', learn=True):
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

      # Actualización del nuevo estado respecto a si es terminal o no
      if env.is_terminal_state():
        target = reward
        new_state = None
      else:
        new_state = new_state.to(DEVICE)
        target = reward + self.discount_factor * \
            torch.max(self.target_nn(
                new_state[None, :]))  # target = R(s’) + γ · maxa’ Q(s’,a’)
        new_state = new_state.cpu()
      
      # Guardado en memoria del estado
      if len(self.samples) > self.memory_capacity:
        self.samples = self.samples[: (len(self.samples) - 1)]

      self.samples = np.append(self.samples, MemoryElement(
          state, action, new_state, reward))
      
      # Aquí se ejecuta el aprendizaje para aproximar los valores de la salida
      x_train, y_train = self.get_train_dset()
      self.policy_nn.train()
      y_pred = self.policy_nn(x_train.to(DEVICE))
      loss = self.loss_func(y_pred, y_train.detach().to(DEVICE))
      self.opt.zero_grad()
      loss.backward()
      self.opt.step()
      self.losses.append(loss.item())

    else:  # seleccionar la mejor acción conocida
      actions = self.target_nn(env.get_state()[None, :].to(DEVICE))
      action = self.agent_argmax(actions)
      reward, new_state = env.perform_action(action.item())


  '''Método para obtener el set de entrenamiento del modelo a partir de la memoria
     y el tamaño del conjunto de datos.
  '''
  def get_train_dset(self):

    memory_set = []
    # Selección del tamaño de la muestra, se toma el bach size si el tamaño de la memoria es mayor a este, sino se escoge el tamaño de la memoria
    size = self.batch_size - \
        1 if len(self.samples) > self.batch_size else len(self.samples)
    if len(self.samples) > 0:
      index = np.random.randint(0, len(self.samples), size)
      memory_set = self.samples[index]

    x_memory = torch.tensor([])
    y_memory = torch.tensor([])

    # Cálculo de la salida y_true
    for _tuple in memory_set:
      y_true = torch.tensor(_tuple.reward) if _tuple.new_state == None else _tuple.reward + self.discount_factor * torch.max(
          self.target_nn(_tuple.new_state[None, :].to(DEVICE)))  # target = reward else target = R(s’) + γ · maxa’ Q(s’,a’)
      y_true_tuple = self.target_nn(_tuple.state[None, :].to(DEVICE))

      y_true_tuple[0][_tuple.action] = y_true.item()
      # Guardado en memoria del estado
      x_memory = torch.cat((x_memory, _tuple.state))
      # Guardado en memoria del valor (columna de salida) verdadero
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

  '''Método de selección binaria a partir del umbral definido'''
  def agent_argmax(self, value):
    action = self.actions[0]
    if value > CHOOSE_UMBRAL:
        action = self.actions[1]
    return action

'''Clase de almacenamiento de los datos de entrenamiento'''
class Dset(torch.utils.data.Dataset):
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.n_samples = x.shape[0]

  def __getitem__(self, index):
    return self.x[index], self.y[index]

  def __len__(self):
    return self.n_samples

'''Elemento de la memoria del agente el cual contiene la información
de un elemento de dicha memoria (estado, acción ejecutada, nuevo estado, recompensa)'''
class MemoryElement():
  def __init__(self, state, action, new_state, reward):
    self.state = state
    self.action = action
    self.new_state = new_state
    self.reward = reward