import string
import pandas as pd
from myPCA import myPCA


def load_data():
    df = preprocess_df(load_df('titanic.csv'))
    return df.to_numpy()


def load_df(name: string):
    return pd.read_csv(name)


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    '''
      Limpieza de Datos
        @PassengerId: No consideramos este dato relevante ya que no nos interesa el Id especifico de cada pasajero.
          Nuestrs intención es analizar tendencias, por eso no nos interesa el Id. Además, como van de 1 -> N, se 
          vuelve redundante mantener estos datos ya que el Id es el número de fila.

        @Name: No lo consideramos relevante ya que queremos hacer un análisis de tendencias generalizado. No 
          queremos conocer la probabilidad de sobrevencia de una persona basada en su nombre, ya que los nombres 
          tienden a ser casi que únicos. Vale más la pena hacer un análisis de la probabilidad de sobreviviencia 
          basado en la clase social, ya que engloba más casos.

        @Ticket: Ocurre un análisis similar al de Name y PassengerId. No nos interesa analizar variables que tienden 
          a ser únicas.

        @Cabin: Al analizar los valores de Cabin vemos que se comporta como un Id. De esta manera, no le vamos a dar
          relevancia ya que nos interesa la tendencia generalizada de los datos.

        @Embarked: Consideramos el puerto en donde se embarco irrelevante ya que no aporta mucha importancia saber en que 
          entrada de abordó el Titanic. No consideramos que tiene mucha relevancia conocer esta información ya que no afecta
          las tendencias de sobrevivir o no.
    '''
    df.drop(columns=['PassengerId', 'Name',
                     'Ticket', 'Cabin', 'Embarked'], inplace=True)
    df.dropna(inplace=True)

    df = pd.get_dummies(df, columns=['Pclass', 'Sex'])

    # df.drop(columns=['Sex_female'], inplace=True)
    # df.rename(columns={'Sex_male': 'Male'}, inplace=True)

    return df
