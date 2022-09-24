# -*- coding: utf-8 -*-
"""Laboratorio_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EXU5o8hFvIHKn9hEmQqlrK29il3tcBPw

# Laboratorio 2 | Machine Learning
* Marco Ferraro | B82957
* Roy Padilla | B85854
"""

from math import nan
import pdb
import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split

PARTICIONES = 10
GANANCIA_MINIMA = 0.0
MAX_DEPTH = 200

PARTICIONES = 10
GANANCIA_MINIMA = 0.0
MAX_DEPTH = 200

target_value_iris = 'class'
df_iris = pd.read_csv('iris.data', names=['sepal-length','sepal-width','petal-length','petal-width','class'])
df_iris

target_value_mushrooms = 'class'
df_mushrooms = pd.read_csv('mushrooms.csv')
df_mushrooms

target_value_titanic = 'Survived'
df_titanic = pd.read_csv('titanic.csv')
df_titanic = df_titanic.drop(columns=['PassengerId', 'Name', 'Ticket', 'Cabin']).dropna()
y = df_titanic['Survived']
df_titanic['Pclass'] = df_titanic['Pclass'].astype('category')
df_titanic.dtypes

ser_iris = pd.Series(data=df_iris.loc[:, target_value_iris])
ser_iris

ser_mushrooms = pd.Series(data=df_mushrooms.loc[:, target_value_mushrooms])
ser_mushrooms

ser_titanic = pd.Series(data=df_titanic.loc[:, target_value_titanic])
ser_titanic

"""Drop de las columnas a clasificar"""

df_iris = df_iris.drop(columns=[target_value_iris])
df_mushrooms = df_mushrooms.drop(columns=[target_value_mushrooms])
df_titanic = df_titanic.drop(columns=[target_value_titanic])

"""# 1. Función `Gini(y)` 
Recibe un objeto pandas.Series y calcula el coeficiente de Gini para dicha serie.

> a. Recuerde que los valores de y puede ser de tipos de datos diferentes como strings (mushrooms), booleanos o incluso números enteros.




"""

def Gini(y: pd.Series):
    gini = 0
    size = y.size
    for clase, cant in y.value_counts().iteritems():
        gini += (cant/size)**2
    gini = 1-gini
    return gini

"""#2. Función `Gini_split(ys)` 
Recibe un arreglo con diversos objetos pandas.Series y calcula el coeficiente de Ginisplit para esta división.
"""

def Gini_split(ys):
    gini_split = 0
    ginis = []
    total_elementos = 0
    # Generación de los Ginis individuales
    for y_serie in ys:
        total_elementos_y = y_serie.size
        total_elementos += total_elementos_y
        ginis.append([Gini(y_serie), total_elementos_y ])
    
    # Cálculo del Gini split
    for gini in ginis:
        gini_split += gini[0] * gini[1]/total_elementos
    
    return gini_split

"""# 3. `DecisionTree`
## 3.1 Método ```fit(self, x, y, max_depth = None)```
Recibe un objeto pandas.DataFrame x, un objeto pandas.Series y y (opcionalmente) un entero max_depth. El parámetro x contiene los datos y atributos que utilizará el modelo en sus predicciones; el parámetro y contiene la categoría a la que pertenece cada uno de los datos de x; max_depth es un parámetro opcional que de ser diferente a None, indica cuál es el valor máximo de profundidad para el árbol. Cuando se llama este método se deberán eliminar los datos previos del modelo y rehacer el árbol de decisión desde cero. Considere que para esto podría resultar útil una clase Nodo, el árbol será de tipo binario. Para cada nodo deberá analizar los siguiente:

## 3.2 Método ```predict(self, x)```
Recibe un objeto pandas.DataFrame x que contiene los valores de un conjunto de datos a predecir. El método debe retornar un objeto de tipo pandas.Series (si se tiene un arreglo array basta con ejecutar el llamado pandas.Series(array)) con las clases a las que pertenece cada uno de los datos de x.

## 3.3 Método ```Método to_dict(self)```
Retorna el árbol en formato de diccionario.
"""

class Node:
    def __init__(self, data, y_clasification, parent, depth):
        self.es_hoja = False
        self.data = data
        self.y_clasification = y_clasification
        self.gini = Gini(y_clasification)
        self.count = int(y_clasification.value_counts().sum().item())
        # Orden
        self.parent: parent
        self.left : Node = None
        self.right: Node = None
        self.depth = depth
        # Clasificación
        self.numeric_classification : bool = False
        self.classification_column = None
        self.clasification_value = None
        self.node_class = ''
    
    def getClass(self):
        '''
         Cuenta la cantidad de valores distintos dentro de la columna de clasificación
        '''
        return self.y_clasification.nunique()

    def setHoja(self):
        '''
         Establece los valores de un nodo para que este sea hoja
        '''
        self.es_hoja = True
        self.node_class = int(self.y_clasification.mode().values[0]) if type(self.y_clasification.mode().values[0]) == 'int64' else self.y_clasification.mode().values[0]
    
    def setIntermedio(self, left, right,  numeric_classification, classification_column, clasification_value):
        '''
         Establece los valores de un nodo para que este sea intermedio, es decir, que tenga hijos
        '''
        self.right = right
        self.left = left
        self.numeric_classification = numeric_classification
        self.classification_column = classification_column
        self.clasification_value = clasification_value
        self.data = None

class TreeJsonEncoder(json.JSONEncoder):
    '''
    Codificador para pasar las variables del objeto de diccionario a Json para evitar errores
    de tipos como int64. Tomado de https://bobbyhadz.com/blog/python-typeerror-object-of-type-int64-is-not-json-serializable
    '''
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class DecisionTree:
    def __init__(self): 
        self.x = None
        self.y = None
        self.ganancia_minima = GANANCIA_MINIMA
        self.root_node = []
    
    def __splitNumeric(self, data, index_columna, point):
      '''
        Método de partición del dataset para las columnas que son numéricas, esto se hace a partir
        del punto que se recibe de parámetro, dividiendo a la izquierda los valores que son menores
        o igual a este punto y a la derecha los que son mayores.
      '''
      indexes_split_le = []
      indexes_split_m = []
      for index, row in data.iterrows():
        if row[index_columna] <= point:
          indexes_split_le.append(index)
        else:
          indexes_split_m.append(index)
      return data.loc[indexes_split_le].astype(data.dtypes.to_dict()), data.loc[indexes_split_m].astype(data.dtypes.to_dict()), indexes_split_le, indexes_split_m

    def __splitCategoric(self, data, index_columna, value_to_split):
      '''
        Método de partición del dataset para las columnas que son categóricas, esto se hace a partir
        del valor que se recibe de parámetro, dividiendo a la izquierda los valores que son iguales
        a este y a la derecha los que son diferentes.
      '''
      indexes_split_eq_value = []
      indexes_neq_value = []
      for index, row in data.iterrows():
        if row[index_columna] == value_to_split:
          indexes_split_eq_value.append(index)
        else:
          indexes_neq_value.append(index)
      return data.loc[indexes_split_eq_value].astype(data.dtypes.to_dict()), data.loc[indexes_neq_value].astype(data.dtypes.to_dict()),indexes_split_eq_value, indexes_neq_value

    def __getGanancia(self, ig_max, gini_padre, y_left, y_right):
      '''
        calcula la ganacia del split que se pasa por parámetro, si esta es mayor
        que la actual entonces el valor retornado es el ig max y un diccionario con
        el split máximo
      '''      
      ig_change = False
      split_l = [] if y_left.empty else y_left.to_list()
      split_r = [] if y_right.empty else y_right.to_list()

      gini_split = Gini_split(pd.Series(y,dtype=pd.StringDtype()) for y in [split_l, split_r])
      
      ig_actual_split = gini_padre - gini_split
      if ig_actual_split > ig_max:
        ig_max = ig_actual_split
        ig_change = True
      
      return ig_max, ig_change

    def __split(self, parent : Node, max_depth):
      '''
        Método encargado de realizar las particiones del árbol de desición,
        genera los nodos.
      '''
      if parent.getClass() == 1 or parent.depth >= max_depth:
          parent.setHoja() 
      else:
        numeric_split = True
        clasification_column = ""
        clasification_value = 0.0

        columnas_numericas_x = parent.data.select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64']).columns
        ig_mayor = 0 # ganancia mayor del split
        split_optimo = {'left': None , 'right': None}

        for df_columna in parent.data.columns:
          # Caso de columnas numéricas
          if df_columna in columnas_numericas_x:
            split = parent.data.loc[:, df_columna]
            min = split.min()
            max = split.max()
            if min != max:
              points = np.linspace(min, max, num = PARTICIONES + 1, endpoint=False)[1:]
              for index in range(PARTICIONES):
                split_le, split_m, index_le, index_m = self.__splitNumeric(parent.data, parent.data.columns.get_loc(df_columna), points[index])
                ig_mayor, ig_change = self.__getGanancia(ig_mayor, parent.gini, self.y.loc[index_le], self.y.loc[index_m])
                if ig_change:
                  clasification_column = df_columna
                  clasification_value = points[index]
                  numeric_split = True
                  split_optimo['left'] = split_le
                  split_optimo['y_left'] = self.y.loc[index_le]
                  split_optimo['right'] = split_m
                  split_optimo['y_right'] = self.y.loc[index_m]
          else:
            # Caso de columnas categóricas
            split = parent.data.loc[:, df_columna]
            if split.unique().size > 1:
              for value in split.unique():
                split_eq_value, split_neq_value, index_eq, index_neq = self.__splitCategoric(parent.data, parent.data.columns.get_loc(df_columna), value)
                ig_mayor, ig_change = self.__getGanancia(ig_mayor, parent.gini, self.y.loc[index_eq], self.y.loc[index_neq])
                if ig_change:
                  clasification_column = df_columna
                  clasification_value = value
                  numeric_split = False
                  split_optimo['left'] = split_eq_value
                  split_optimo['y_left'] = self.y.loc[index_eq]
                  split_optimo['right'] = split_neq_value
                  split_optimo['y_right'] = self.y.loc[index_neq]
                            
        # En este punto ya encontramos la ganancia máxima de todos los splits por lo que hay que 
        # determinar si hubo ganacia para partir el nodo en hijos o bien que este pase a ser hoja 
        # en caso de que no haya ganancia
        if ig_mayor > self.ganancia_minima:
          # particion y creado los nodos y llamado recursivamente (Generación de nodo intermedio)
          left_node = Node(split_optimo['left'], split_optimo['y_left'], parent, parent.depth + 1)
          right_node = Node(split_optimo['right'], split_optimo['y_right'], parent, parent.depth + 1)
          parent.setIntermedio(left_node, right_node, numeric_split, clasification_column, clasification_value)
          self.__split(left_node, max_depth)
          self.__split(right_node, max_depth)
        else:
          # nodo actual pasa a ser nodo hoja y termina recusividad
          parent.setHoja()

    def predict(self, x):
      tags = []
      for index, row in x.iterrows():
        current_node = self.root_node
        while not(current_node.es_hoja):
          if current_node.numeric_classification:
            if current_node.clasification_value >= row[current_node.classification_column]:
              current_node = current_node.left
            else:
              current_node = current_node.right
          else:
            if current_node.clasification_value == row[current_node.classification_column]:
              current_node = current_node.left
            else:
              current_node = current_node.right
        tags.append(current_node.node_class)
      return pd.Series(tags)

    def to_dict(self, json_name = "tree"):
      dictionary = self.to_dict_node(self.root_node)
      json_object = json.dumps(dictionary, indent=4, cls=TreeJsonEncoder)
      # Escritura del Json
      with open("{}.json".format(json_name), "w") as outfile:
          outfile.write(json_object)
      return dictionary
    
    def to_dict_node(self, node : Node):
      '''
        Método auxiliar a to_dict para la generación recursiva del diccionario
        a generar del árbol
      '''
      if node.es_hoja:
        return {"type" : "leaf", "class" : node.node_class, "count" : node.count}
      else:
        json_split_node = {"type": "split", "gini": node.gini, "count": node.count, "split-type": "numerical" if node.numeric_classification else "categorical", "split-column": node.classification_column, "split-value": node.clasification_value}
        json_split_node["child-left"] = self.to_dict_node(node.left)
        json_split_node["child-right"] = self.to_dict_node(node.right)
        return json_split_node

    def fit(self, x: pd.DataFrame, y: pd.Series):
        self.x = x
        self.y = y
        root = Node(x, y, None, 0)
        self.root_node = root
        self.__split(root, MAX_DEPTH)

# Decision tree iris dataset
iris_tree =  DecisionTree()
iris_tree.fit(df_iris, ser_iris)
iris_dict = iris_tree.to_dict("iris")

# Decision tree mushrooms dataset
mushrooms_tree =  DecisionTree()
mushrooms_tree.fit(df_mushrooms, ser_mushrooms)
mushrooms_dict = mushrooms_tree.to_dict("mushrooms")

# Decision tree titanic dataset
titanic_tree =  DecisionTree()
titanic_tree.fit(df_titanic, ser_titanic)
titanic_dict = titanic_tree.to_dict("titanic")

dicts = {
    'mushrooms': mushrooms_dict,
    'iris': iris_dict,
    'titanic': titanic_dict
}

"""# 4.  Método ```calculate_confusion_matrix(predict, real)```

Recibe dos objetos pandas.Series predict y real, que corresponden a las clases estimadas por el modelo de árbol de decisión y los valores reales para un subconjunto de datos. Teniendo los datos estimados y los datos reales deberá calcular y retornar la matriz de conclusión de dichos datos.
"""

def calculate_confusion_matrix(predict, real):
    values = real.unique()
    confusion_matrix = np.zeros((len(values), len(values)))
    predict = predict.to_numpy()
    real = real.to_numpy()
    for i in range(len(real)):
        column = np.where(values == predict[i])[0][0]
        row = np.where(values == real[i])[0][0]
        confusion_matrix[row][column] += 1

    return confusion_matrix

"""# 5. `sklearn.model_selection`
Utilice los datasets provistos para verificar el correcto funcionamiento de su árbol. Además puede utilizar el método train_test_split de la biblioteca `sklearn.model_selection` para separar un conjunto de datos en un conjunto de datos de entrenamiento y otro de prueba, para verificar el rendimiento de los árboles generados.

"""

X_iris_train, X_iris_test, y_iris_train, y_iris_test = train_test_split(df_iris, ser_iris, test_size=0.3, random_state=42)
X_iris_train

X_titanic_train, X_titanic_test, y_titanic_train, y_titanic_test = train_test_split(df_titanic, ser_titanic, test_size=0.3, random_state=42)
X_titanic_train = pd.get_dummies(X_titanic_train, columns=['Sex', 'Embarked'])
X_titanic_test = pd.get_dummies(X_titanic_test, columns=['Sex', 'Embarked'])
X_titanic_train

X_mushrooms_train, X_mushrooms_test, y_mushrooms_train, y_mushrooms_test = train_test_split(df_mushrooms, ser_mushrooms, test_size=0.3, random_state=42)
X_mushrooms_train = pd.get_dummies(X_mushrooms_train)
X_mushrooms_test = pd.get_dummies(X_mushrooms_test)
X_mushrooms_train

"""# 6. Matrices de confusión de los modelos

Utilice los datasets provistos para verificar el correcto funcionamiento de su árbol. Además puede utilizar el método train_test_split de la biblioteca
`sklearn.model_selection` para separar un conjunto de datos en un conjunto de
datos de entrenamiento y otro de prueba, para verificar el rendimiento de los árboles generados. Compare el rendimiento de su árbol con el de un árbol de la biblioteca `sklearn`.
"""

from sklearn import tree

clf = tree.DecisionTreeClassifier()
clf_iris = clf.fit(X_iris_train, y_iris_train)

prediction = clf_iris.predict(X_iris_test)
conf_matrix = calculate_confusion_matrix(pd.Series(prediction), y_iris_test)
conf_matrix

iris_tree =  DecisionTree()
iris_tree.fit(X_iris_train, y_iris_train)
prediction = iris_tree.predict(X_iris_test)


conf_matrix = calculate_confusion_matrix(pd.Series(prediction), y_iris_test)
conf_matrix

from sklearn import tree

clf = tree.DecisionTreeClassifier()
clf_titanic = clf.fit(X_titanic_train, y_titanic_train)

prediction = clf_titanic.predict(X_titanic_test)
conf_matrix = calculate_confusion_matrix(pd.Series(prediction), y_titanic_test)
conf_matrix

titanic_tree =  DecisionTree()
titanic_tree.fit(X_titanic_train, y_titanic_train)
prediction = titanic_tree.predict(X_titanic_test)


conf_matrix = calculate_confusion_matrix(pd.Series(prediction), y_titanic_test)
conf_matrix

from sklearn import tree

clf = tree.DecisionTreeClassifier()
clf_mushrooms = clf.fit(X_mushrooms_train, y_mushrooms_train)

prediction = clf_mushrooms.predict(X_mushrooms_test)
conf_matrix = calculate_confusion_matrix(pd.Series(prediction), y_mushrooms_test)
conf_matrix

mushrooms_tree =  DecisionTree()
mushrooms_tree.fit(X_mushrooms_train, y_mushrooms_train)
prediction = mushrooms_tree.predict(X_mushrooms_test)


conf_matrix = calculate_confusion_matrix(pd.Series(prediction), y_mushrooms_test)
conf_matrix

"""# 7. Respuestas Breves

¿ Qué mejoras o funcionalidades adicionales se le ocurre que podría incluir en su clase DecisionTree ?


> Según la documentación de scikit learn, una de las desventajas de los árboles de decisión es que estos pueden ser "parcializados" si hay alguna clase dominante. Por lo tanto, una mejora que se le podria agregar a nuestro árbol de decisión es que antes de cada iteración o "split" se genere un balance sobre el dataset. Otra mejora que se le podría agregar a nuestro es mitigar los "grandes cambios" que pueden llegar a generar valores pequeños. Esto se debe a que, debido a pequeñas variaciones de valores dentro de un dataset, se puede llegar a generar un árbol de decisión completamente diferente debido al criterio de separación. Así mismo se puede incluir un análisis de correlación para determinar cuáles son las variables más relevantes y de esta manera priorizar y seleccionar de mejor manera las columnas a particionar.


¿ Qué tanto varían los resultados para el mismo set de datos de
entrenamiento-prueba?



> Al ver los resultado de las matrices de confusión podemos ver que los resultados no varian en sí. De hecho, las matrices de confusión generadas a partir de ambas implementaciones logran tener una precisión y un grado de acertividad bastante alto.

**Nota respecto a los test:**
Se encontró una diferencia en cuanto al árbol de titanic, esta viene dada por una relación de orden al analizar las columnas, donde se encuentra primero con Age la cual genera una ganancia igual que Fare, por lo que nuestra implementación toma Age como columna a separar causando así una pequeña diferencia en el orden de la rama respecto al archivo de test. Aún así nótese que se cambia únicamente el orden y no se pierde ninguna rama, esto se observa en la siguiente imagen (al lado izquierdo nuestra implementación y al lado derecho el test propuesto por el profesor):

![Justificacion](https://drive.google.com/uc?id=1uYpEUovoT20WGhp8zwKV3al0WQqNEZDp)
"""

# Commented out IPython magic to ensure Python compatibility.
# %%shell
# jupyter nbconvert --to html /content/Laboratorio_2.ipynb