# Figuras y tablas del poster a partir de los CSV, sin repetir las simulaciones.
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CARPETA = Path(__file__).resolve().parent
RESULTADOS = CARPETA / 'resultados'
DIRIGIDAS = RESULTADOS / 'dirigidas'
GRAFICAS = RESULTADOS / 'graficas'
TABLAS = RESULTADOS / 'tablas_poster'
ESCENARIOS = ['Original', 'Centrales x2', 'Centrales x3', 'Perifericos x3']
COLORES = ['#506781', '#4A91A8', '#136E6B', '#CF8758']
CONFIGURACIONES = [
    'Puente bidireccional', 'Sin puente', 'Puente 9 a 10',
    'Retorno central 10 a 9', 'Retorno no puente 11 a 1',
    'Avance central 9 a 11', 'Avance no puente 1 a 11'
]
ETIQUETAS = [
    'Bidireccional', 'Sin puente', 'Unidireccional',
    'Retorno central', 'Retorno no puente', 'Avance central', 'Avance no puente'
]


# Crea versiones resumidas de los datos, listas para seleccionar en Canva.
def guardar_tablas(resumen_original, resumen_dirigido, espectros, conectividad):
    originales = resumen_original[np.isclose(resumen_original['tolerancia'], 0.001)].copy()
    tabla1 = originales[['red', 'escenario', 'promedio_iteraciones', 'desviacion_estandar',
                         'mejora_respecto_original', 'empeora_respecto_original']].copy()
    tabla1.columns = ['Red', 'Escenario', 'Promedio', 'Desviacion', 'Mejoran', 'Empeoran']
    tabla1.to_csv(TABLAS / '01_primera_fase.csv', index=False, float_format='%.4f')

    tabla2 = conectividad[['configuracion', 'arcos', 'fuertemente_conexa', 'debilmente_conexa',
                            'componentes_fuertes', 'componentes_fuente']].copy()
    tabla2.to_csv(TABLAS / '02_conectividad.csv', index=False)

    datos = resumen_dirigido[np.isclose(resumen_dirigido['tolerancia'], 0.001)].copy()
    datos = datos.merge(espectros[['configuracion', 'escenario', 'segundo_valor_modulo',
                                    'multiplicidad_valor_propio_uno']],
                        on=['configuracion', 'escenario'])
    referencias = datos[datos['configuracion'] == 'Puente bidireccional'][
        ['escenario', 'promedio_iteraciones']].copy()
    referencias.columns = ['escenario', 'promedio_referencia']
    datos = datos.merge(referencias, on='escenario')
    datos['cambio_porcentual_vs_referencia'] = (
        100 * (datos['promedio_iteraciones'] / datos['promedio_referencia'] - 1))
    columnas3 = ['configuracion', 'escenario', 'consensos', 'casos',
                 'promedio_iteraciones', 'desviacion_estandar', 'segundo_valor_modulo',
                 'multiplicidad_valor_propio_uno', 'cambio_porcentual_vs_referencia']
    datos[columnas3].to_csv(TABLAS / '03_extension_completa_0001.csv',
                            index=False, float_format='%.5f')

    tabla4 = datos[datos['escenario'].isin(['Original', 'Centrales x3'])][
        ['configuracion', 'escenario', 'consensos', 'promedio_iteraciones',
         'segundo_valor_modulo', 'cambio_porcentual_vs_referencia']].copy()
    tabla4.to_csv(TABLAS / '04_comparacion_esencial_poster.csv',
                  index=False, float_format='%.4f')

    tabla5 = datos[['configuracion', 'escenario', 'consensos',
                    'mejora_respecto_original_de_la_configuracion',
                    'empeora_respecto_original_de_la_configuracion']].copy()
    tabla5.to_csv(TABLAS / '05_casos_emparejados.csv', index=False)

    tabla6 = datos[['configuracion', 'escenario', 'consensos',
                    'opinion_consenso_promedio', 'diferencia_medias_comunidades_promedio',
                    'brecha_final_promedio']].copy()
    tabla6.to_csv(TABLAS / '06_opiniones_y_brechas.csv',
                  index=False, float_format='%.6f')

    tabla7 = resumen_dirigido[['configuracion', 'tolerancia', 'escenario', 'consensos',
                               'promedio_iteraciones', 'desviacion_estandar']].copy()
    tabla7.to_csv(TABLAS / '07_sensibilidad_tolerancias.csv',
                  index=False, float_format='%.4f')
    return tabla1, tabla2, tabla4


# Dibuja la red completa y destaca en rojo los arcos entre las comunidades.
def graficar_estructuras():
    red = nx.Graph()
    red.add_nodes_from(range(20))
    for inicio in [0, 10]:
        for nodo in range(inicio, inicio + 10):
            for vecino in range(nodo + 1, inicio + 10):
                red.add_edge(nodo, vecino)
    red.add_edge(9, 10)
    posiciones = {}
    for nodo in range(10):
        angulo = 2 * np.pi * nodo / 10
        posiciones[nodo] = (-2.0 + np.cos(angulo), np.sin(angulo))
    for nodo in range(10, 20):
        angulo = np.pi + 2 * np.pi * (nodo - 10) / 10
        posiciones[nodo] = (2.0 + np.cos(angulo), np.sin(angulo))
    pares = [
        ('Bidireccional', [(9, 10), (10, 9)]),
        ('Unidireccional', [(9, 10)]),
        ('Retorno no puente', [(9, 10), (11, 1)]),
        ('Sin puente', [])
    ]
    figura, ejes = plt.subplots(2, 2, figsize=(11, 7.2))
    internos = [(a, b) for a, b in red.edges() if (a < 10 and b < 10)
                or (a >= 10 and b >= 10)]
    for eje, (nombre, arcos) in zip(ejes.flat, pares):
        nx.draw_networkx_edges(red, posiciones, edgelist=internos, ax=eje,
                               width=0.55, alpha=0.16, edge_color='#7B8C9B')
        nx.draw_networkx_nodes(red, posiciones, nodelist=list(range(10)),
                               ax=eje, node_size=100, node_color='#438CB9')
        nx.draw_networkx_nodes(red, posiciones, nodelist=list(range(10, 20)),
                               ax=eje, node_size=100, node_color='#3D9E86')
        nx.draw_networkx_labels(red, posiciones, labels={9: '9', 10: '10', 1: '1', 11: '11'},
                                font_size=7.5, font_color='white', font_weight='bold', ax=eje)
        for origen, destino in arcos:
            nx.draw_networkx_edges(red, posiciones, edgelist=[(origen, destino)],
                                   arrows=True, arrowstyle='-|>', arrowsize=22,
                                   connectionstyle='arc3,rad=0.16', ax=eje,
                                   width=2.2, edge_color='#C65D49', node_size=100)
        eje.set_title(nombre, fontsize=13, fontweight='bold')
        eje.axis('off')
    figura.suptitle('Dos comunidades: conexiones entre grupos', fontsize=17, fontweight='bold')
    figura.text(0.5, 0.012, 'Las conexiones internas se mantienen en ambos sentidos. Las flechas rojas muestran los arcos entre comunidades.',
                ha='center', fontsize=10)
    figura.tight_layout(rect=[0, 0.035, 1, 0.94])
    figura.savefig(GRAFICAS / 'fig_extension_01_estructuras.png', dpi=210)
    plt.close(figura)


# Contrasta la misma intervencion de pesos en distintas estructuras dirigidas.
def graficar_comparacion(resumen):
    datos = resumen[np.isclose(resumen['tolerancia'], 0.001)]
    figura, eje = plt.subplots(figsize=(12, 5.6))
    filas = [(c, etiqueta) for c, etiqueta in zip(CONFIGURACIONES, ETIQUETAS)
             if c != 'Sin puente']
    lugares = np.arange(len(filas))
    ancho = 0.19
    for indice, escenario in enumerate(ESCENARIOS):
        valores = []
        for configuracion, etiqueta in filas:
            filtro = datos[(datos['configuracion'] == configuracion)
                           & (datos['escenario'] == escenario)]
            valores.append(float(filtro['promedio_iteraciones'].iloc[0]))
        eje.bar(lugares + (indice - 1.5) * ancho, valores,
                width=ancho, color=COLORES[indice], label=escenario)
    eje.set_xticks(lugares, [etiqueta.replace(' ', '\\n', 1) for _, etiqueta in filas], fontsize=10)
    eje.set_ylabel('Iteraciones promedio hasta consenso (tol. 0.001)', fontsize=11)
    eje.set_title('Dirección de los arcos y refuerzo de influencia', fontsize=16, fontweight='bold')
    eje.legend(ncol=4, loc='upper center', bbox_to_anchor=(0.5, 1.0), fontsize=10)
    eje.grid(axis='y', alpha=0.16)
    eje.set_axisbelow(True)
    figura.text(0.5, 0.015, 'Sin puente: 0 de 20 simulaciones con consenso en todos los escenarios (excluido del gráfico).',
                ha='center', fontsize=10, color='#7B3F3F')
    figura.tight_layout(rect=[0, 0.06, 1, 1])
    figura.savefig(GRAFICAS / 'fig_extension_02_iteraciones.png', dpi=210)
    plt.close(figura)


# Una comparacion breve y legible de los dos escenarios mas importantes.
def graficar_poster_principal(resumen):
    datos = resumen[np.isclose(resumen['tolerancia'], 0.001)]
    figura, eje = plt.subplots(figsize=(10, 5.3))
    filas = [(c, etiqueta) for c, etiqueta in zip(CONFIGURACIONES, ETIQUETAS)
             if c != 'Sin puente' and c != 'Retorno central 10 a 9']
    lugares = np.arange(len(filas))
    for indice, escenario in enumerate(['Original', 'Centrales x3']):
        valores = []
        for configuracion, etiqueta in filas:
            filtro = datos[(datos['configuracion'] == configuracion)
                           & (datos['escenario'] == escenario)]
            valores.append(float(filtro['promedio_iteraciones'].iloc[0]))
        barras = eje.bar(lugares + (indice - 0.5) * 0.35, valores, 0.35,
                         label=escenario, color=['#516A84', '#167C72'][indice])
        eje.bar_label(barras, fmt='%.0f', fontsize=10, padding=3)
    eje.set_xticks(lugares, [etiqueta.replace(' ', '\\n', 1) for _, etiqueta in filas], fontsize=11)
    eje.set_ylim(0, 575)
    eje.set_ylabel('Promedio de iteraciones (tol. 0.001)')
    eje.set_title(
    'Direccionalidad y refuerzo central: tiempo de consenso',
    fontsize=14,
    fontweight='bold'
)
    eje.legend(loc='upper right', fontsize=11)
    eje.grid(axis='y', alpha=0.18)
    eje.set_axisbelow(True)
    figura.tight_layout()
    figura.savefig(GRAFICAS / 'fig_extension_03_poster_principal.png', dpi=220)
    plt.close(figura)


# Compara el SLEM y las iteraciones solo en matrices con valor propio 1 simple.
def graficar_espectro(resumen, espectros):
    datos = resumen[np.isclose(resumen['tolerancia'], 0.001)]
    figura, eje = plt.subplots(figsize=(9, 5.8))
    for indice, escenario in enumerate(ESCENARIOS):
        for configuracion in CONFIGURACIONES:
            if configuracion != 'Sin puente' and configuracion != 'Retorno central 10 a 9':
                fila = datos[(datos['configuracion'] == configuracion)
                             & (datos['escenario'] == escenario)].iloc[0]
                espectro = espectros[(espectros['configuracion'] == configuracion)
                                     & (espectros['escenario'] == escenario)].iloc[0]
                eje.scatter(float(espectro['segundo_valor_modulo']),
                            float(fila['promedio_iteraciones']),
                            color=COLORES[indice], s=68, edgecolors='white', linewidth=0.7)
        eje.scatter([], [], color=COLORES[indice], label=escenario)
    eje.set_xlabel('SLEM (segundo mayor módulo propio)')
    eje.set_ylabel('Iteraciones promedio, tol. 0.001')
    eje.set_title('Relación espectral en las configuraciones con consenso',
                  fontsize=15, fontweight='bold')
    eje.grid(alpha=0.2)
    eje.legend(ncol=2, loc='upper left')
    figura.tight_layout()
    figura.savefig(GRAFICAS / 'fig_extension_04_espectro.png', dpi=210)
    plt.close(figura)


# Ilustra por que la direccion puede cambiar el consenso global.
def graficar_trayectorias():
    original = nx.Graph()
    original.add_nodes_from(range(20))
    for inicio in [0, 10]:
        for nodo in range(inicio, inicio + 10):
            for vecino in range(nodo + 1, inicio + 10):
                original.add_edge(nodo, vecino)
    original.add_edge(9, 10)
    bidireccional = nx.DiGraph(original)
    sin_puente = bidireccional.copy()
    sin_puente.remove_edge(9, 10)
    sin_puente.remove_edge(10, 9)
    unidireccional = sin_puente.copy()
    unidireccional.add_edge(9, 10)
    redes = [('Puente bidireccional', bidireccional),
             ('Puente unidireccional', unidireccional), ('Sin puente', sin_puente)]
    opiniones = np.random.default_rng(0).uniform(0, 1, 20)
    figura, eje = plt.subplots(figsize=(9, 5.2))
    for indice, (nombre, red) in enumerate(redes):
        adyacencia = nx.to_numpy_array(red, nodelist=sorted(red.nodes()), weight=None)
        pesos = adyacencia.T + np.eye(20)
        matriz = pesos / pesos.sum(axis=1, keepdims=True)
        x = opiniones.copy()
        historia = [float(np.ptp(x))]
        for paso in range(650):
            x = matriz @ x
            historia.append(float(np.ptp(x)))
        eje.plot(range(len(historia)), historia, label=nombre,
                 color=['#516A84', '#C78358', '#B64848'][indice], linewidth=2)
    eje.axhline(0.001, color='#555555', linestyle='--', linewidth=1,
                label='Tolerancia 0.001')
    eje.set_yscale('log')
    eje.set_ylim(1e-5, 1)
    eje.set_xlabel('Iteraciones, semilla 0, sin refuerzo')
    eje.set_ylabel('Máxima diferencia de opiniones')
    eje.set_title('La dirección modifica la evolución del desacuerdo',
                  fontsize=15, fontweight='bold')
    eje.legend(loc='upper right', fontsize=10)
    eje.grid(alpha=0.18, which='both')
    figura.tight_layout()
    figura.savefig(GRAFICAS / 'fig_extension_05_trayectorias.png', dpi=210)
    plt.close(figura)


# Permite pegar tablas como imagen en el poster, sin transcribir cifras.
def dibujar_tabla(datos, columnas, titulos, nombre, titulo, ancho):
    filas = []
    for _, fila in datos.iterrows():
        celdas = []
        for columna in columnas:
            valor = fila[columna]
            if pd.isna(valor):
                celdas.append('--')
            elif isinstance(valor, float):
                celdas.append(f'{valor:.1f}')
            else:
                celdas.append(str(valor))
        filas.append(celdas)
    alto = max(2.4, 1.1 + 0.43 * len(filas))
    figura, eje = plt.subplots(figsize=(ancho, alto))
    eje.axis('off')
    tabla = eje.table(cellText=filas, colLabels=titulos, loc='center', cellLoc='center')
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.scale(1, 1.32)
    for (i, j), celda in tabla.get_celld().items():
        celda.set_edgecolor('#DDE5EA')
        if i == 0:
            celda.set_facecolor('#1D3E55')
            celda.get_text().set_color('white')
            celda.get_text().set_weight('bold')
        elif i % 2 == 0:
            celda.set_facecolor('#F2F6F8')
    figura.suptitle(titulo, fontsize=15, fontweight='bold', y=0.99)
    figura.tight_layout(rect=[0, 0, 1, 0.93])
    figura.savefig(TABLAS / nombre, dpi=200)
    plt.close(figura)


# Lee lo que guardo experimento.py y construye material reproducible.
def main():
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    TABLAS.mkdir(parents=True, exist_ok=True)
    original = pd.read_csv(RESULTADOS / 'resumen.csv')
    resumen = pd.read_csv(DIRIGIDAS / 'resumen_dirigidas.csv')
    espectros = pd.read_csv(DIRIGIDAS / 'espectros_dirigidos.csv')
    conectividad = pd.read_csv(DIRIGIDAS / 'conectividad_dirigida.csv')
    tabla1, tabla2, tabla4 = guardar_tablas(original, resumen, espectros, conectividad)
    graficar_estructuras()
    graficar_comparacion(resumen)
    graficar_poster_principal(resumen)
    graficar_espectro(resumen, espectros)
    graficar_trayectorias()

    sencilla = tabla1[tabla1['Escenario'].isin(['Original', 'Centrales x3'])].copy()
    dibujar_tabla(sencilla, ['Red', 'Escenario', 'Promedio'],
                  ['Red', 'Escenario', 'Promedio'], 'tabla_01_primera_fase.png',
                  'Primera fase: resultados esenciales', 8.7)
    clave = tabla4[(tabla4['configuracion'] != 'Sin puente')
                   & (tabla4['configuracion'] != 'Retorno central 10 a 9')].copy()
    clave['Config.'] = clave['configuracion'].replace(dict(zip(CONFIGURACIONES, ETIQUETAS)))
    dibujar_tabla(clave, ['Config.', 'escenario', 'consensos', 'promedio_iteraciones'],
                  ['Configuracion', 'Influencia', 'Casos / 20', 'Iteraciones'],
                  'tabla_02_extension_esencial.png',
                  'Extension dirigida (tolerancia 0.001)', 10.5)
    grafo = tabla2.copy()
    grafo['Configuracion'] = grafo['configuracion'].replace(dict(zip(CONFIGURACIONES, ETIQUETAS)))
    dibujar_tabla(grafo, ['Configuracion', 'arcos', 'fuertemente_conexa', 'componentes_fuente'],
                  ['Configuracion', 'Arcos', 'Fuerte', 'Fuentes'],
                  'tabla_03_conectividad.png', 'Conectividad dirigida', 9.5)
    print('Graficas de extension y 7 tablas CSV de poster guardadas')


main()
