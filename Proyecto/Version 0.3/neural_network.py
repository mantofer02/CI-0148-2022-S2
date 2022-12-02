from torch import nn, flatten



class DQL_NN(nn.Module):
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
    x = flatten(x, 1)

    # Ejecución en la red neuroral
    h = self.act1(self.fc1(x))
    out = self.act2(self.fc2(h))

    return out
