# -*- coding: utf-8 -*-
"""Laboratorio3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CUIP_2ceSth5w6LguMqtehSDP7-F8AXq

# Laboratorio 3: Regresión Lineal

*   Marco Ferraro | B82957
"""

import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split

df = pd.read_csv('fish_perch.csv')
df

df_y = df['Weight'].copy()
df_x = df.drop(columns=['Weight'])
df_y

"""# 1. Función `MSE(y_true, y_predict)` 
Recibe dos objetos pd.Series que
contienen los valores reales de un conjunto de datos y los valores estimados por un modelo. Calcule y retorne el error cuadrático medio de dicha predicción.
"""

def MSE(y_true, y_predict, c=[], regularization='none', lbd=0):
  sum = 0.0
  n = len(y_true)
  add_on = 0.0

  if regularization == 'lasso' or regularization == 'l1':
    sum_l1 = 0.0
    for i in range(len(c)):
      sum_l1 += abs(c[i])
    add_on = lbd * sum_l1

  elif regularization == 'ridge' or regularization == 'l2': 
    sum_l2 = 0.0
    for i in range(len(c)):
      sum_l2 += c[i]**2
    add_on = lbd * sum_l2

  for i in range(n):
    sum += ((y_predict[i] - y_true[i])**2)
  return float(sum / n) + add_on

"""# 2. Función `score(y_true, y_predict)`

Recibe dos objetos pd.Series que
contienen los valores reales de un conjunto de datos y los valores estimados por un
modelo. Calcule y retorne el coeficiente de determinación (R^2) de dicha predicción
"""

def score(y_true, y_predict):

  y_true.to_numpy()
  y_predict.to_numpy()

  mean = y_true.mean()
  first_sum = sum(((y_true - y_predict)**2))
  second_sum = sum(((y_true - mean)**2))

  return float((second_sum - first_sum) / second_sum)

class LinearRegression:
  def __init__(self):
    self.c_vector = []
    self.errors = []
    self.past_dc = 0.0

  def update_c(self, x, y, c, learning_rate, momentum=0):

    a = (np.matmul(x, c) - y).T
    b = np.matmul(a, x).T
    dc = (2.0 / len(y)) * b

    new_c = c - (learning_rate * (dc + (momentum * self.past_dc))) 
    self.past_dc = dc

    return new_c

  def predict(self, x, add_bias=False):
    if (add_bias):
       x.insert(0, "bias", 1.0, True)
       x = x.to_numpy()
    predict_y = []
    for i in range(len(x)):
      predict_y.append(np.dot(x[i], self.c_vector)[0])
    
    return pd.Series(predict_y)

  def get_error_history(self):
    return self.errors

  def fit(self, x, y, max_epochs=1e5, threshold=1e-3, learning_rate=1e-5, momentum=0, decay=0, error='mse', regularization='none', lbd=0):
    
    ready = False
    error = 0
    iteration = 0
    self.errors = []
    
    x.insert(0, "bias", 1.0, True)
    x = x.to_numpy()
    y = np.array([y.to_numpy()]).T
    self.c_vector = np.array([random.sample(range(len(x[0])), len(x[0]))]).T

    while not ready and iteration < max_epochs:
      self.c_vector = self.update_c(x, y, self.c_vector, learning_rate, momentum=momentum)
      new_error = MSE(y, np.matmul(x, self.c_vector), c=self.c_vector, regularization=regularization, lbd=lbd)
      if abs(error - new_error) < threshold:
        ready = True
      error = new_error
      self.errors.append(error)
      learning_rate = learning_rate / (1 + decay)

      iteration += 1

"""# 3 Funcionamiento del algoritmo 
Utilice el set de datos proveído para probar el funcionamiento de su algoritmo. Recuerde que el error debe reducirse en cada iteración del algoritmo (o llegar a un “zig-zag” producto de una tasa de aprendizaje muy elevada).
"""

lr = LinearRegression()
preds = lr.fit(df_x, df_y)

errors = lr.get_error_history()
reduced_errors = []
jumps = 2150

for i in range(0, len(errors), jumps): reduced_errors.append(errors[i])

reduced_errors

"""# 4 Split de datos 
Luego utilice el método train_test_split de la biblioteca sklearn.model_selection para separar un conjunto de datos en un conjunto de datos de entrenamiento y otro de prueba, utilice de semilla del split el número 21 (el método permite el parámetro opcional trandom_state para sembrar la aleatoriedad).



> **Nota**: Para esta sección se hará el cálculo del r2 con scikit learn, ya que el modelo implementado genera `nan` en la primera resta



"""

from sklearn.metrics import r2_score


X_fish_train, X_fish_test, y_fish_train, y_fish_test = train_test_split(df_x, df_y, test_size=0.3, random_state=21)

lr = LinearRegression()
lr.fit(X_fish_train, y_fish_train)

pred = lr.predict(X_fish_test, add_bias=True)

r2 = r2_score(y_fish_test, pred)
r2

from sklearn.metrics import r2_score

X_fish_train, X_fish_test, y_fish_train, y_fish_test = train_test_split(df_x, df_y, test_size=0.3, random_state=21)

lr = LinearRegression()
lr.fit(X_fish_train, y_fish_train, learning_rate=1e-6, decay=1e-3, regularization='l1', momentum=0.5, lbd=0.5)

pred = lr.predict(X_fish_test, add_bias=True)

r2 = r2_score(y_fish_test, pred)
r2

from sklearn.metrics import r2_score

X_fish_train, X_fish_test, y_fish_train, y_fish_test = train_test_split(df_x, df_y, test_size=0.3, random_state=21)

lr = LinearRegression()
lr.fit(X_fish_train, y_fish_train, learning_rate=1e-6, decay=1e-3, regularization='l2', momentum=0.5, lbd=0.5)

pred = lr.predict(X_fish_test, add_bias=True)

r2 = r2_score(y_fish_test, pred)
r2

from sklearn.metrics import r2_score

X_fish_train, X_fish_test, y_fish_train, y_fish_test = train_test_split(df_x, df_y, test_size=0.3, random_state=21)

lr = LinearRegression()
lr.fit(X_fish_train, y_fish_train, learning_rate=1e-4, decay=1e-5, regularization='l1', momentum=0.7, lbd=0.7)

pred = lr.predict(X_fish_test, add_bias=True)

r2 = r2_score(y_fish_test, pred)
r2

from sklearn.metrics import r2_score

X_fish_train, X_fish_test, y_fish_train, y_fish_test = train_test_split(df_x, df_y, test_size=0.3, random_state=21)

lr = LinearRegression()
lr.fit(X_fish_train, y_fish_train, learning_rate=1e-4, decay=1e-5, regularization='l2', momentum=0.7, lbd=0.7)

pred = lr.predict(X_fish_test, add_bias=True)

r2 = r2_score(y_fish_test, pred)
r2

"""## 4.1 ¿Cuál fue la combinación de parámetros que le proveyó el mejor resultado?


> Viendo los resultados de las 4 pruebas que se lograron hacer, la combinación de parametros que brindó mejor resultado fue: 
```
learning_rate=1e-4, decay=1e-5, regularization='l1', momentum=0.7, lbd=0.7
```

> Esto dió como resultado un `r2 score` de `0.8883647017635607`

## 4.2 ¿Qué pasa si utiliza esa misma combinación pero cambia la semilla del train_test_split?  
Pruebe con varias semillas
"""

from sklearn.metrics import r2_score


X_fish_train, X_fish_test, y_fish_train, y_fish_test = train_test_split(df_x, df_y, test_size=0.3, random_state=53)

lr = LinearRegression()
lr.fit(X_fish_train, y_fish_train, learning_rate=1e-4, decay=1e-5, regularization='l1', momentum=0.7, lbd=0.7)

pred = lr.predict(X_fish_test, add_bias=True)

r2 = r2_score(y_fish_test, pred)
r2

from sklearn.metrics import r2_score


X_fish_train, X_fish_test, y_fish_train, y_fish_test = train_test_split(df_x, df_y, test_size=0.3, random_state=74)

lr = LinearRegression()
lr.fit(X_fish_train, y_fish_train, learning_rate=1e-4, decay=1e-5, regularization='l1', momentum=0.7, lbd=0.7)

pred = lr.predict(X_fish_test, add_bias=True)

r2 = r2_score(y_fish_test, pred)
r2

"""## 4.3 Si pasa algo inusual: ¿Por qué cree que pasa esto?


> Analizando los resultado, vemos que se generan `r2 score` mejores que los de las pruebas pasadas. Esto puede ser por la naturaleza de los datos, ya que al variar el set de entrenamiento el modelo puede que genere un mejor `fit` que los anteriores. 


"""