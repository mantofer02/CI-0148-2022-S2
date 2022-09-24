
def imprimir(entrada):
    print(str(entrada))


def duplicar(n):
    numero = 2/0
    imprimir(2*n)


try:
    numero = int(input())
    duplicar(numero)
except Exception as e:
    print(e)
