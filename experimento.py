# Comparacion de centralidad y convergencia en tres redes.
from pathlib import Path
import csv
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CARPETA = Path(__file__).resolve().parent
RESULTADOS = CARPETA / 'resultados'
TOLERANCIAS = [0.001, 0.01]
SEMILLAS = range(20)
ESCENARIOS = [('Original', 1, 'centrales'), ('Centrales x2', 2, 'centrales'),
              ('Centrales x3', 3, 'centrales'), ('Perifericos x3', 3, 'perifericos')]
MAX_ITERACIONES = 20000

# Dos grupos de diez nodos unidos por una conexion.
def crear_dos_comunidades():
    red = nx.Graph()
    red.add_nodes_from(range(20))
    for inicio in [0, 10]:
        for nodo in range(inicio, inicio + 10):
            for vecino in range(nodo + 1, inicio + 10):
                red.add_edge(nodo, vecino)
    red.add_edge(9, 10)
    return red

# Orden estable: se redondea la centralidad para evitar desempates por ruido numerico.
def seleccionar_nodos(red):
    valores = nx.eigenvector_centrality_numpy(red, weight=None)
    centrales = sorted(red.nodes(), key=lambda n: (-round(valores[n], 8), n))[:3]
    perifericos = [n for n in sorted(red.nodes(), key=lambda n: (round(valores[n], 8), n)) if n not in centrales][:3]
    return centrales, perifericos, valores

# Se multiplican columnas, incluyendo entradas diagonales, y luego se normalizan filas.
def crear_matriz(red, seleccionados, factor):
    orden = sorted(red.nodes())
    matriz = nx.to_numpy_array(red, nodelist=orden, weight=None) + np.eye(len(orden))
    indices = [orden.index(nodo) for nodo in seleccionados]
    matriz[:, indices] = matriz[:, indices] * factor
    matriz = matriz / matriz.sum(axis=1, keepdims=True)
    return matriz

# Calcula el segundo mayor modulo entre los valores propios de la matriz estocastica.
def segundo_valor(matriz):
    modulos = sorted(np.abs(np.linalg.eigvals(matriz)), reverse=True)
    return float(modulos[1])

# Cuenta iteraciones hasta que la diferencia entre maximo y minimo llega a la tolerancia.
def simular(matriz, iniciales, tolerancia):
    opiniones = iniciales.copy()
    historia = [float(np.ptp(opiniones))]
    pasos = 0
    while historia[-1] > tolerancia and pasos < MAX_ITERACIONES:
        opiniones = matriz @ opiniones
        pasos += 1
        historia.append(float(np.ptp(opiniones)))
    if historia[-1] > tolerancia:
        pasos = None
    return pasos, historia

# Guarda una tabla con encabezados.
def guardar_csv(ruta, filas):
    with open(ruta, 'w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)

# Graficas generadas a partir de las simulaciones.
def graficas(resumen, espectros, trayectorias):
    nombres = ['Karate Club', 'Camino', 'Dos comunidades']
    posicion = np.arange(3)
    anchura = 0.19
    for tipo in ['iteraciones', 'espectro']:
        plt.figure(figsize=(9, 4.4))
        for indice, (escenario, factor, seleccion) in enumerate(ESCENARIOS):
            if tipo == 'iteraciones':
                datos = [fila['promedio_iteraciones'] for nombre in nombres for fila in resumen
                         if fila['red'] == nombre and fila['escenario'] == escenario
                         and fila['tolerancia'] == 0.001]
            else:
                datos = [fila['segundo_valor_modulo'] for nombre in nombres for fila in espectros
                         if fila['red'] == nombre and fila['escenario'] == escenario]
            plt.bar(posicion + (indice - 1.5) * anchura, datos, width=anchura, label=escenario)
        plt.xticks(posicion, nombres)
        plt.ylabel('Promedio de iteraciones' if tipo == 'iteraciones' else 'Segundo valor propio en modulo')
        plt.title('Comparacion de ' + tipo)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(RESULTADOS / 'graficas' / ('comparacion_' + tipo + '.png'), dpi=170)
        plt.close()
    for nombre, historias in trayectorias.items():
        plt.figure(figsize=(7, 4))
        for escenario, historia in historias.items():
            plt.plot(range(len(historia)), historia, label=escenario)
        plt.axhline(0.001, color='gray', linestyle='--', label='Tolerancia 0.001')
        plt.yscale('log')
        plt.xlabel('Iteraciones')
        plt.ylabel('Diferencia maxima entre opiniones')
        plt.title('Evolucion: ' + nombre)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(RESULTADOS / 'graficas' / ('evolucion_' + nombre.replace(' ', '_') + '.png'), dpi=170)
        plt.close()

# Ejecuta los mismos escenarios con las mismas opiniones iniciales en cada red.
def main():
    (RESULTADOS / 'graficas').mkdir(parents=True, exist_ok=True)
    redes = {'Karate Club': nx.karate_club_graph(), 'Camino': nx.path_graph(20),
             'Dos comunidades': crear_dos_comunidades()}
    registros = []
    resumen = []
    espectros = []
    centralidades = []
    trayectorias = {}
    for nombre, red in redes.items():
        centrales, perifericos, valores = seleccionar_nodos(red)
        print(nombre + ': centrales ' + str(centrales) + ', perifericos ' + str(perifericos))
        for nodo in sorted(red.nodes()):
            centralidades.append({'red': nombre, 'nodo': nodo,
                                  'centralidad_vector_propio': round(float(valores[nodo]), 8),
                                  'central': nodo in centrales, 'periferico': nodo in perifericos})
        matrices = {}
        for escenario, factor, tipo in ESCENARIOS:
            seleccionados = centrales if tipo == 'centrales' else perifericos
            matriz = crear_matriz(red, seleccionados, factor)
            matrices[escenario] = matriz
            espectros.append({'red': nombre, 'escenario': escenario, 'factor_influencia': factor,
                              'segundo_valor_modulo': segundo_valor(matriz),
                              'nodos_seleccionados': ', '.join(str(n) for n in seleccionados)})
        trayectorias[nombre] = {}
        for semilla in SEMILLAS:
            iniciales = np.random.default_rng(semilla).uniform(0, 1, len(red))
            for tolerancia in TOLERANCIAS:
                for escenario, factor, tipo in ESCENARIOS:
                    pasos, historia = simular(matrices[escenario], iniciales, tolerancia)
                    registros.append({'red': nombre, 'semilla': semilla,
                                      'tolerancia': tolerancia, 'escenario': escenario,
                                      'iteraciones': pasos})
                    if semilla == 0 and tolerancia == 0.001:
                        trayectorias[nombre][escenario] = historia
        for tolerancia in TOLERANCIAS:
            originales = {fila['semilla']: fila['iteraciones'] for fila in registros
                          if fila['red'] == nombre and fila['tolerancia'] == tolerancia
                          and fila['escenario'] == 'Original'}
            for escenario, factor, tipo in ESCENARIOS:
                filas = [fila for fila in registros if fila['red'] == nombre
                         and fila['tolerancia'] == tolerancia and fila['escenario'] == escenario]
                tiempos = [fila['iteraciones'] for fila in filas if fila['iteraciones'] is not None]
                mejoras = sum(fila['iteraciones'] < originales[fila['semilla']] for fila in filas
                              if fila['iteraciones'] is not None and originales[fila['semilla']] is not None)
                empeora = sum(fila['iteraciones'] > originales[fila['semilla']] for fila in filas
                              if fila['iteraciones'] is not None and originales[fila['semilla']] is not None)
                resumen.append({'red': nombre, 'tolerancia': tolerancia, 'escenario': escenario,
                                'casos': len(tiempos), 'promedio_iteraciones': float(np.mean(tiempos)),
                                'desviacion_estandar': float(np.std(tiempos)),
                                'mejora_respecto_original': mejoras,
                                'empeora_respecto_original': empeora})
    guardar_csv(RESULTADOS / 'experimentos.csv', registros)
    guardar_csv(RESULTADOS / 'resumen.csv', resumen)
    guardar_csv(RESULTADOS / 'espectros.csv', espectros)
    guardar_csv(RESULTADOS / 'centralidades.csv', centralidades)
    graficas(resumen, espectros, trayectorias)
    print('Resultados guardados. Total de ejecuciones: ' + str(len(registros)))
    print('Red | Tolerancia | Escenario | Iteraciones promedio | Desviacion | Mejoras | Empeora')
    for fila in resumen:
        print(f"{fila['red']} | {fila['tolerancia']:.3f} | {fila['escenario']} | "
              f"{fila['promedio_iteraciones']:.2f} | {fila['desviacion_estandar']:.2f} | "
              f"{fila['mejora_respecto_original']} | {fila['empeora_respecto_original']}")


# SEGUNDA FASE. Se conservan las tres redes y las 480 ejecuciones originales.
# Solo se amplian los experimentos para la red de Dos comunidades.
# En una flecha origen -> destino, el origen influye sobre el destino.
def crear_redes_dirigidas():
    original = nx.DiGraph(crear_dos_comunidades())
    sin_puente = original.copy()
    sin_puente.remove_edge(9, 10)
    sin_puente.remove_edge(10, 9)

    dirigido = sin_puente.copy()
    dirigido.add_edge(9, 10)

    retorno_central = dirigido.copy()
    retorno_central.add_edge(10, 9)

    retorno_no_puente = dirigido.copy()
    retorno_no_puente.add_edge(11, 1)

    avance_central = dirigido.copy()
    avance_central.add_edge(9, 11)

    avance_no_puente = dirigido.copy()
    avance_no_puente.add_edge(1, 11)

    return {
        'Puente bidireccional': original,
        'Sin puente': sin_puente,
        'Puente 9 a 10': dirigido,
        'Retorno central 10 a 9': retorno_central,
        'Retorno no puente 11 a 1': retorno_no_puente,
        'Avance central 9 a 11': avance_central,
        'Avance no puente 1 a 11': avance_no_puente
    }


# NetworkX guarda origen -> destino en B[origen, destino]. En DeGroot,
# A[destino, origen] representa cuanto escucha destino a origen.
# Por esta convencion se transpone B al construir la matriz dirigida.
def crear_matriz_dirigida(red, seleccionados, factor):
    orden = sorted(red.nodes())
    matriz = nx.to_numpy_array(red, nodelist=orden, weight=None).T + np.eye(len(orden))
    indices = [orden.index(nodo) for nodo in seleccionados]
    matriz[:, indices] = matriz[:, indices] * factor
    matriz = matriz / matriz.sum(axis=1, keepdims=True)
    return matriz


# Describe si las conexiones dirigidas permiten comunicacion en ambos sentidos.
def describir_red_dirigida(red):
    condensacion = nx.condensation(red)
    fuentes = sum(condensacion.in_degree(nodo) == 0 for nodo in condensacion.nodes())
    return {
        'nodos': red.number_of_nodes(),
        'arcos': red.number_of_edges(),
        'fuertemente_conexa': nx.is_strongly_connected(red),
        'debilmente_conexa': nx.is_weakly_connected(red),
        'componentes_fuertes': nx.number_strongly_connected_components(red),
        'componentes_fuente': fuentes
    }


# Amplia el mismo experimento sin reemplazar los resultados de la primera fase.
def ejecutar_extension_dirigida():
    carpeta = RESULTADOS / 'dirigidas'
    carpeta.mkdir(parents=True, exist_ok=True)
    redes = crear_redes_dirigidas()
    centrales, perifericos, valores = seleccionar_nodos(crear_dos_comunidades())
    registros = []
    resumen = []
    espectros = []
    conectividad = []

    for configuracion, red in redes.items():
        propiedades = describir_red_dirigida(red)
        conectividad.append({'configuracion': configuracion, **propiedades})
        matrices = {}
        for escenario, factor, tipo in ESCENARIOS:
            seleccionados = centrales if tipo == 'centrales' else perifericos
            matriz = crear_matriz_dirigida(red, seleccionados, factor)
            matrices[escenario] = matriz
            valores_propios = np.linalg.eigvals(matriz)
            multiplicidad = int(np.count_nonzero(np.isclose(valores_propios, 1, atol=1e-8)))
            espectros.append({
                'configuracion': configuracion, 'escenario': escenario,
                'factor_influencia': factor, 'segundo_valor_modulo': 1.0 if multiplicidad > 1 else segundo_valor(matriz),
                'multiplicidad_valor_propio_uno': multiplicidad,
                'slem_interpretable': multiplicidad == 1,
                'nodos_seleccionados': ', '.join(str(nodo) for nodo in seleccionados)
            })

        for semilla in SEMILLAS:
            iniciales = np.random.default_rng(semilla).uniform(0, 1, len(red))
            for tolerancia in TOLERANCIAS:
                for escenario, factor, tipo in ESCENARIOS:
                    matriz = matrices[escenario]
                    pasos, historia = simular(matriz, iniciales, tolerancia)
                    numero_pasos = pasos if pasos is not None else MAX_ITERACIONES
                    finales = np.linalg.matrix_power(matriz, numero_pasos) @ iniciales
                    media_a = float(np.mean(finales[:10]))
                    media_b = float(np.mean(finales[10:]))
                    registros.append({
                        'configuracion': configuracion, 'red': 'Dos comunidades',
                        'semilla': semilla, 'tolerancia': tolerancia,
                        'escenario': escenario, 'iteraciones': pasos if pasos is not None else '',
                        'convergio': pasos is not None,
                        'brecha_final': float(np.ptp(finales)),
                        'opinion_consenso': float(np.mean(finales)) if pasos is not None else '',
                        'media_final_comunidad_1': media_a,
                        'media_final_comunidad_2': media_b,
                        'diferencia_medias_comunidades': abs(media_a - media_b)
                    })

        for tolerancia in TOLERANCIAS:
            originales = {fila['semilla']: fila['iteraciones'] for fila in registros
                          if fila['configuracion'] == configuracion and fila['tolerancia'] == tolerancia
                          and fila['escenario'] == 'Original'}
            for escenario, factor, tipo in ESCENARIOS:
                filas = [fila for fila in registros if fila['configuracion'] == configuracion
                         and fila['tolerancia'] == tolerancia and fila['escenario'] == escenario]
                tiempos = [fila['iteraciones'] for fila in filas if fila['convergio']]
                mejoras = sum(fila['iteraciones'] < originales[fila['semilla']] for fila in filas
                              if fila['convergio'] and originales[fila['semilla']] != '')
                empeora = sum(fila['iteraciones'] > originales[fila['semilla']] for fila in filas
                              if fila['convergio'] and originales[fila['semilla']] != '')
                promedio = float(np.mean(tiempos)) if tiempos else ''
                desviacion = float(np.std(tiempos)) if tiempos else ''
                resumen.append({
                    'configuracion': configuracion, 'tolerancia': tolerancia,
                    'escenario': escenario, 'casos': len(filas), 'consensos': len(tiempos),
                    'promedio_iteraciones': promedio, 'desviacion_estandar': desviacion,
                    'mejora_respecto_original_de_la_configuracion': mejoras,
                    'empeora_respecto_original_de_la_configuracion': empeora,
                    'brecha_final_promedio': float(np.mean([fila['brecha_final'] for fila in filas])),
                    'diferencia_medias_comunidades_promedio': float(np.mean(
                        [fila['diferencia_medias_comunidades'] for fila in filas])),
                    'opinion_consenso_promedio': float(np.mean(
                        [fila['opinion_consenso'] for fila in filas if fila['convergio']])) if tiempos else ''
                })

    guardar_csv(carpeta / 'experimentos_dirigidos.csv', registros)
    guardar_csv(carpeta / 'resumen_dirigidas.csv', resumen)
    guardar_csv(carpeta / 'espectros_dirigidos.csv', espectros)
    guardar_csv(carpeta / 'conectividad_dirigida.csv', conectividad)
    print('Extension dirigida: ' + str(len(registros)) + ' simulaciones guardadas')


main()
ejecutar_extension_dirigida()
