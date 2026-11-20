# Tres graficas simples para el informe del modelo de DeGroot.
# Usa los CSV ya guardados, sin repetir las simulaciones.
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

CARPETA = Path(__file__).resolve().parent
RESULTADOS = CARPETA / 'resultados'
GRAFICAS = RESULTADOS / 'graficas'
REDES = ['Karate Club', 'Camino', 'Dos comunidades']
ESCENARIOS = ['Original', 'Centrales x2', 'Centrales x3', 'Perifericos x3']
COLORES = ['#64748b', '#5b9aa3', '#247a6d', '#d18a4d']
TAMANO_LETRA = 12

# Construye las mismas tres redes del experimento.
def construir_redes():
    comunidades = nx.Graph()
    comunidades.add_nodes_from(range(20))
    for inicio in [0, 10]:
        for nodo in range(inicio, inicio + 10):
            for vecino in range(nodo + 1, inicio + 10):
                comunidades.add_edge(nodo, vecino)
    comunidades.add_edge(9, 10)
    return {'Karate Club': nx.karate_club_graph(), 'Camino': nx.path_graph(20),
            'Dos comunidades': comunidades}

# Figura 1: nodos centrales (verde) y perifericos (naranja) de cada red.
def graficar_estructuras(centralidades):
    redes = construir_redes()
    figura, ejes = plt.subplots(1, 3, figsize=(10, 4.2))
    for eje, nombre in zip(ejes, REDES):
        red = redes[nombre]
        datos = centralidades[centralidades['red'] == nombre]
        centrales = set(datos.loc[datos['central'], 'nodo'])
        perifericos = set(datos.loc[datos['periferico'], 'nodo'])
        if nombre == 'Camino':
            posiciones = {nodo: (nodo, 0) for nodo in red.nodes()}
        elif nombre == 'Dos comunidades':
            posiciones = nx.spring_layout(red, seed=3, iterations=300)
        else:
            posiciones = nx.spring_layout(red, seed=5, iterations=200)
        colores = []
        for nodo in red.nodes():
            color = '#bdc6d0'
            if nodo in centrales:
                color = '#247a6d'
            if nodo in perifericos:
                color = '#d18a4d'
            colores.append(color)
        nx.draw_networkx_edges(red, posiciones, ax=eje, alpha=0.25, width=0.7)
        nx.draw_networkx_nodes(red, posiciones, ax=eje, node_size=120,
                               node_color=colores, edgecolors='white', linewidths=0.4)
        eje.set_title(nombre, fontsize=TAMANO_LETRA)
        eje.axis('off')
    figura.text(0.5, 0.03, 'Verde: nodos centrales     Naranja: nodos periféricos     Gris: demás nodos',
                ha='center', fontsize=TAMANO_LETRA - 1)
    figura.tight_layout(rect=[0, 0.08, 1, 1])
    figura.savefig(GRAFICAS / 'fig_estructuras.png', dpi=200)
    plt.close(figura)

# Figura 2: iteraciones de cada escenario como porcentaje del escenario original.
def graficar_porcentajes(resumen):
    figura, eje = plt.subplots(figsize=(7, 3.8))
    datos = resumen[np.isclose(resumen['tolerancia'], 0.001)]
    posiciones = np.arange(len(REDES))
    ancho = 0.2
    for indice, escenario in enumerate(ESCENARIOS):
        porcentajes = []
        for nombre in REDES:
            filas = datos[datos['red'] == nombre]
            original = filas.loc[filas['escenario'] == 'Original', 'promedio_iteraciones'].iloc[0]
            actual = filas.loc[filas['escenario'] == escenario, 'promedio_iteraciones'].iloc[0]
            porcentajes.append(100 * actual / original)
        barras = eje.bar(posiciones + (indice - 1.5) * ancho, porcentajes, ancho,
                         color=COLORES[indice], label=escenario)
        eje.bar_label(barras, fmt='%.0f', fontsize=9, padding=2)
    eje.axhline(100, linestyle='--', linewidth=1, color='#333333')
    eje.set_xticks(posiciones, REDES, fontsize=TAMANO_LETRA)
    eje.set_ylabel('Iteraciones respecto al original (%)', fontsize=TAMANO_LETRA)
    eje.set_ylim(0, 320)
    eje.legend(fontsize=10, ncol=2, loc='upper left')
    eje.grid(axis='y', alpha=0.2)
    eje.set_axisbelow(True)
    figura.tight_layout()
    figura.savefig(GRAFICAS / 'fig_porcentajes.png', dpi=200)
    plt.close(figura)

# Figura 3: segundo valor propio en modulo frente al promedio de iteraciones.
def graficar_espectro(resumen, espectros):
    figura, eje = plt.subplots(figsize=(7, 4))
    datos = resumen[np.isclose(resumen['tolerancia'], 0.001)]
    marcas = {'Karate Club': 'o', 'Camino': 's', 'Dos comunidades': '^'}
    for nombre in REDES:
        for indice, escenario in enumerate(ESCENARIOS):
            lam = espectros[(espectros['red'] == nombre) & (espectros['escenario'] == escenario)]['segundo_valor_modulo'].iloc[0]
            its = datos[(datos['red'] == nombre) & (datos['escenario'] == escenario)]['promedio_iteraciones'].iloc[0]
            eje.scatter(lam, its, marker=marcas[nombre], s=70, color=COLORES[indice],
                        edgecolors='black', linewidths=0.5, zorder=3)
    # Curva de referencia ln(tolerancia)/ln(lambda2).
    lambdas = np.linspace(0.82, 0.998, 200)
    eje.plot(lambdas, np.log(0.001) / np.log(lambdas), '--', color='gray', linewidth=1.2,
             label='Referencia: ln(0,001) / ln|λ₂|')
    eje.set_yscale('log')
    eje.set_xlabel('Segundo valor propio en módulo |λ₂|', fontsize=TAMANO_LETRA)
    eje.set_ylabel('Promedio de iteraciones (escala log.)', fontsize=TAMANO_LETRA)
    eje.grid(alpha=0.2, which='both')
    # Leyendas separadas: forma = red, color = escenario.
    for nombre in REDES:
        eje.scatter([], [], marker=marcas[nombre], color='white', edgecolors='black', label=nombre)
    for indice, escenario in enumerate(ESCENARIOS):
        eje.scatter([], [], marker='o', color=COLORES[indice], label=escenario)
    eje.legend(fontsize=9, loc='upper left', ncol=2)
    figura.tight_layout()
    figura.savefig(GRAFICAS / 'fig_espectro.png', dpi=200)
    plt.close(figura)

# Lee los CSV y crea las tres figuras del informe.
def main():
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    resumen = pd.read_csv(RESULTADOS / 'resumen.csv')
    espectros = pd.read_csv(RESULTADOS / 'espectros.csv')
    centralidades = pd.read_csv(RESULTADOS / 'centralidades.csv')
    graficar_estructuras(centralidades)
    graficar_porcentajes(resumen)
    graficar_espectro(resumen, espectros)
    print('Figuras del informe guardadas en resultados/graficas')

main()
