# Verificaciones basicas de las redes y de la simulacion del modelo.
import numpy as np
import networkx as nx
from pathlib import Path
import csv

# Valida las matrices que se guardan en los experimentos.
def main():
    carpeta = Path(__file__).resolve().parent
    with open(carpeta / 'resultados' / 'experimentos.csv', encoding='utf-8') as archivo:
        experimentos = list(csv.DictReader(archivo))
    with open(carpeta / 'resultados' / 'resumen.csv', encoding='utf-8') as archivo:
        resumen = list(csv.DictReader(archivo))
    with open(carpeta / 'resultados' / 'espectros.csv', encoding='utf-8') as archivo:
        espectros = list(csv.DictReader(archivo))
    pruebas = [len(experimentos) == 480, len(resumen) == 24, len(espectros) == 12]
    pruebas.append(all(int(fila['iteraciones']) >= 0 for fila in experimentos))
    pruebas.append(all(0 < float(fila['segundo_valor_modulo']) < 1 for fila in espectros))
    # Cada red se evalua con la misma semilla y tolerancia en cuatro escenarios.
    grupos = {}
    for fila in experimentos:
        llave = (fila['red'], fila['semilla'], fila['tolerancia'])
        grupos[llave] = grupos.get(llave, 0) + 1
    pruebas.append(len(grupos) == 120 and all(cantidad == 4 for cantidad in grupos.values()))
    # Verificaciones adicionales de la extension. No cambian las pruebas originales.
    carpeta_dirigida = carpeta / 'resultados' / 'dirigidas'
    with open(carpeta_dirigida / 'experimentos_dirigidos.csv', encoding='utf-8') as archivo:
        dirigidos = list(csv.DictReader(archivo))
    with open(carpeta_dirigida / 'resumen_dirigidas.csv', encoding='utf-8') as archivo:
        resumen_dirigido = list(csv.DictReader(archivo))
    with open(carpeta_dirigida / 'espectros_dirigidos.csv', encoding='utf-8') as archivo:
        espectros_dirigidos = list(csv.DictReader(archivo))
    with open(carpeta_dirigida / 'conectividad_dirigida.csv', encoding='utf-8') as archivo:
        conectividad = list(csv.DictReader(archivo))

    pruebas.append(len(dirigidos) == 1120)
    pruebas.append(len(resumen_dirigido) == 56)
    pruebas.append(len(espectros_dirigidos) == 28 and len(conectividad) == 7)
    grupos_dirigidos = {}
    for fila in dirigidos:
        llave = (fila['configuracion'], fila['semilla'], fila['tolerancia'])
        grupos_dirigidos[llave] = grupos_dirigidos.get(llave, 0) + 1
    pruebas.append(len(grupos_dirigidos) == 280 and all(
        cantidad == 4 for cantidad in grupos_dirigidos.values()))
    pruebas.append(all((fila['iteraciones'] != '') == (fila['convergio'] == 'True')
                       for fila in dirigidos))
    pruebas.append(all(float(fila['brecha_final']) >= 0 and
                       (float(fila['brecha_final']) <= float(fila['tolerancia']) + 1e-8
                        if fila['convergio'] == 'True' else True) for fila in dirigidos))
    pruebas.append(all(fila['convergio'] == 'False' for fila in dirigidos
                       if fila['configuracion'] == 'Sin puente' and fila['tolerancia'] == '0.001'))
    pruebas.append(all(fila['convergio'] == 'True' for fila in dirigidos
                       if fila['configuracion'] != 'Sin puente'))
    pruebas.append(all(fila['multiplicidad_valor_propio_uno'] == '2'
                       and abs(float(fila['segundo_valor_modulo']) - 1) < 1e-8
                       for fila in espectros_dirigidos if fila['configuracion'] == 'Sin puente'))
    pruebas.append(all(fila['fuertemente_conexa'] == 'False'
                       for fila in conectividad if fila['configuracion'] == 'Puente 9 a 10'))
    originales = {(fila['semilla'], fila['tolerancia'], fila['escenario']): fila['iteraciones']
                  for fila in experimentos if fila['red'] == 'Dos comunidades'}
    comparables = [fila for fila in dirigidos if fila['configuracion'] == 'Puente bidireccional'
                   or fila['configuracion'] == 'Retorno central 10 a 9']
    pruebas.append(len(comparables) == 320 and all(
        str(fila['iteraciones']) == originales[(fila['semilla'], fila['tolerancia'], fila['escenario'])]
        for fila in comparables))
    for numero, correcto in enumerate(pruebas, start=1):
        print('Prueba ' + str(numero) + ': ' + ('BIEN' if correcto else 'FALLA'))
    print('Resultado: ' + str(sum(pruebas)) + ' de ' + str(len(pruebas)) + ' pruebas correctas')

main()
