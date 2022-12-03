from torch import nn, flatten

class DQL_NN(nn.Module):
  def __init__(self, flatten_in_values, actions_number):
    super().__init__()
    # Red neuronal
    self.DQL_stack = nn.Sequential(
            nn.Linear(flatten_in_values, 64),
            nn.Tanh(),
            nn.Linear(64, actions_number),
            nn.LeakyReLU()
        )

  def forward(self, x):
    ''' Sobre escritura del método de forward propagation, aplicando las capas densas de la red neuronal'''
    # aplanamiento de los datos
    x = flatten(x, 1)

    # Ejecución en la red neuroral
    out = self.DQL_stack(x)

    return out
