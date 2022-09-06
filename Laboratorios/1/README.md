# Laboratorio 1 | Machine Learning

## ¿Cuántos grupos de datos parece haber? ¿Qué comportamientos se pueden observar? ¿Qué podría explicar estos comportamientos? ¿Qué nos indica el círculo de correlación?

- Viendo el comportamiento de la gráfica de PCA, notamos que hay 2 grupos de datos. Los datos de las personas que no sobrevivieron parece que tienden a concentrarse en la derecha de la gráfica, mientras que el resto de datos no. Aunque hay una clara separación, parece existir pequeñas excepciones.
- Podemos observar que los primeros 2 componentes manejan un total del 55% de la información. Podemos observar que las condiciones para que alguien no haya sobrevivido son muy similares, a diferencia de los que si sobrevivieron. Esto lo podemos deducir ya que los puntos rojos se concentran y parecen tener una concentración muy homogenia, aunque hayan puntos azules que se traslapan.
- Algo que podria explicar estos comportamientos son las caracteristicas de cada individuo del data set. Para ver las relaciones lo mejor es ver el circulo de correlaciones.
- El circulo de correlaciones nos indica que tan correlacionadas estan las variables entre si, y con que magnitud.

## Si yo fuera un pasajero del Titanic, ¿qué atributos o características maximizarían mi probabilidad de sobrevivencia?

- Viendo el circulo de correlaciones, podemos ver que el precio de venta del pasaje, la cantidad de padres y la cantidad de hermanos están relacionadas con el chance de sobrevivir. De igual manera, la edad esta correlacionada pero no de una manera tan predominante como las anteriores.

## ¿Hay alguna diferencia entre las gráficas? De ser así, ¿por qué cree que ocurrió esto? ¿Impacta el resultado de alguna manera?

- Si, viendo los gráficos podemos ver una diferencia muy evidente; parece que los gráficos estan reflejados.
- Esto puede ser un resultado de la forma en que `sci-kit learn` genera los cálculos de vectores y valores propios. Al analizar con mayor profundidad los valores de las matrices de correlaciones, podemos notar que varios de los valores tienen el signo opuesto, pero mantienen el mismo valor absoluto.
- No, no impacta el resultado. Esto se debe a que, como hemos visto en clase, si un valor o vector propio tienen un valor negativo se van a reflejar en direccion opuesta. Sin embargo, a nosotros lo que nos interesa son la relaciones entre valores, entonces, aunque un gráfico esté reflejado va a mantener su relación o diferencia entre los puntos.
