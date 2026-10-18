"""
Redes y matrices de influencia A (estocásticas por filas).

Convención: A[i, j] es el peso que la persona i da a la opinión de la persona j.
Para redes con pesos W se usa  A = D^-1 (W + s I), donde s = autoinfluencia y D
normaliza cada fila para que sume 1.
"""

import gzip
import math

import numpy as np
from scipy.sparse.csgraph import connected_components


# ---------------------------------------------------------------------------
# Comprobaciones de propiedades
# ---------------------------------------------------------------------------

def es_estocastica_por_filas(A: np.ndarray, tol: float = 1e-9) -> bool:
    """True si A es no negativa y cada fila suma 1."""
    return bool((A >= -tol).all() and np.allclose(A.sum(axis=1), 1.0, atol=tol))


def es_simetrica(A: np.ndarray, tol: float = 1e-9) -> bool:
    """True si A == A^T (con A simétrica el predictor espectral suele ir mejor)."""
    return bool(np.allclose(A, A.T, atol=tol))


def _periodo_de_clase(adj_sub: np.ndarray) -> int:
    """Periodo de un grafo fuertemente conexo (mcd de las longitudes de ciclos)."""
    n = adj_sub.shape[0]
    nivel = -np.ones(n, dtype=int)
    nivel[0] = 0
    cola, g = [0], 0
    while cola:
        u = cola.pop(0)
        for v in np.flatnonzero(adj_sub[u]):
            if nivel[v] < 0:
                nivel[v] = nivel[u] + 1
                cola.append(v)
            else:
                g = math.gcd(g, int(nivel[u] + 1 - nivel[v]))
    return g


def verificar_estructura(A: np.ndarray, tol: float = 1e-12) -> dict:
    """Clasifica la red por su ESTRUCTURA (no solo por sus valores propios).

    Salida: dict con
        n_clases_cerradas : grupos que no reciben influencia de fuera.
        periodos          : periodo de cada clase cerrada (1 = aperiódica).
        clasificacion     : 'consenso' | 'periodica' | 'sin consenso global'.
    """
    adj = A > tol
    n_comp, etiquetas = connected_components(adj, directed=True, connection="strong")
    cerradas = [c for c in range(n_comp)
                if not adj[np.ix_(etiquetas == c, etiquetas != c)].any()]
    periodos = []
    for c in cerradas:
        idx = np.flatnonzero(etiquetas == c)
        periodos.append(_periodo_de_clase(adj[np.ix_(idx, idx)]))
    if len(cerradas) >= 2:
        clasif = "sin consenso global"
    elif periodos and periodos[0] > 1:
        clasif = "periodica"
    else:
        clasif = "consenso"
    return {"n_clases_cerradas": len(cerradas), "periodos": periodos,
            "clasificacion": clasif}


# ---------------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------------

def normalizar_con_autoinfluencia(W: np.ndarray, s: float = 1.0) -> np.ndarray:
    """A = D^-1 (W + s I): cada fila de W + sI se divide entre su suma."""
    M = W + s * np.eye(W.shape[0])
    return M / M.sum(axis=1, keepdims=True)


def aplicar_peso_propio(A: np.ndarray, alpha: float) -> np.ndarray:
    """A' = alpha I + (1 - alpha) A. Quita el valor propio -1 en redes periódicas."""
    return alpha * np.eye(A.shape[0]) + (1 - alpha) * A


def _pesos_metropolis(adj: np.ndarray) -> np.ndarray:
    """Pesos de Metropolis: A simétrica y estocástica para un grafo no dirigido.

    A_ij = 1 / (1 + max(grado_i, grado_j)) en cada arista; el resto va a la diagonal.
    """
    grado = adj.sum(axis=1)
    W = adj / (1.0 + np.maximum.outer(grado, grado))
    np.fill_diagonal(W, 0.0)
    np.fill_diagonal(W, 1.0 - W.sum(axis=1))
    return W


# ---------------------------------------------------------------------------
# Redes sintéticas
# ---------------------------------------------------------------------------

def construir_matriz(tipo: str, n: int, semilla: int = 0,
                     simetrica: bool = True, s: float = 1.0) -> np.ndarray:
    """Construye la matriz A de una red de prueba.

    tipo      : 'completa' | 'anillo' | 'camino' | 'dos_comunidades' |
                'aleatoria' | 'dirigida'
    n         : número de personas.
    semilla   : para las redes aleatorias.
    simetrica : True  -> pesos de Metropolis (A simétrica).
                False -> A = D^-1 (W + sI) (estocástica, en general no simétrica;
                         en redes regulares como el anillo sale simétrica igual).
                'dirigida' siempre es no simétrica.
    s         : autoinfluencia (solo cuando simetrica=False).
    """
    rng = np.random.default_rng(semilla)
    adj = np.zeros((n, n))

    if tipo == "completa":
        adj = np.ones((n, n)) - np.eye(n)
    elif tipo == "anillo":
        for i in range(n):
            adj[i, (i + 1) % n] = adj[(i + 1) % n, i] = 1
    elif tipo == "camino":
        for i in range(n - 1):
            adj[i, i + 1] = adj[i + 1, i] = 1
    elif tipo == "dos_comunidades":
        return dos_comunidades_con_puente(n, w_puente=1.0, s=s, simetrica=simetrica)
    elif tipo == "aleatoria":
        aleat = np.triu(rng.random((n, n)) < 0.15, 1)
        adj = (aleat | aleat.T).astype(float)
        for i in range(n - 1):                       # garantiza que esté conectada
            adj[i, i + 1] = adj[i + 1, i] = 1
    elif tipo == "dirigida":
        for i in range(n):
            adj[i, (i + 1) % n] = 1                  # anillo dirigido (conexa)
        adj = np.maximum(adj, (rng.random((n, n)) < 0.08).astype(float))
        np.fill_diagonal(adj, 0)
        simetrica = False
    else:
        raise ValueError(f"tipo de red desconocido: {tipo}")

    return _pesos_metropolis(adj) if simetrica else normalizar_con_autoinfluencia(adj, s)


def dos_comunidades_con_puente(n: int, w_puente: float = 1.0, s: float = 1.0,
                               simetrica: bool = False) -> np.ndarray:
    """Dos comunidades completas unidas por UN enlace de peso w_puente.

    Sirve para experimentos controlados: al bajar w_puente la red se parece
    cada vez más a dos grupos separados (rho -> 1, consenso cada vez más lento).
    Con simetrica=True se usan pesos de Metropolis (el peso del puente se ignora
    y vale 1); con False se usa A = D^-1 (W + sI), donde sí cuenta w_puente.
    """
    m = n // 2
    W = np.zeros((n, n))
    W[:m, :m] = 1
    W[m:, m:] = 1
    np.fill_diagonal(W, 0)
    W[m - 1, m] = W[m, m - 1] = w_puente
    if simetrica:
        return _pesos_metropolis((W > 0).astype(float))
    return normalizar_con_autoinfluencia(W, s)


# ---------------------------------------------------------------------------
# Redes reales
# ---------------------------------------------------------------------------

def matriz_desde_aristas(aristas, s: float = 1.0) -> np.ndarray:
    """Convierte una red real (aristas i -> j, "i escucha a j") en A.

    Pasos: (1) matriz de adyacencia; (2) se queda con la componente
    fuertemente conexa más grande (si no, no hay consenso); (3) A = D^-1 (W + sI).

    Entradas : aristas = [(i, j), ...] con ids enteros cualesquiera; s autoinfluencia.
    Salida   : A de la componente más grande.
    """
    ids = sorted({v for a in aristas for v in a})
    pos = {v: k for k, v in enumerate(ids)}
    adj = np.zeros((len(ids), len(ids)))
    for i, j in aristas:
        if i != j:
            adj[pos[i], pos[j]] = 1
    _, etiquetas = connected_components(adj > 0, directed=True, connection="strong")
    mayor = np.argmax(np.bincount(etiquetas))
    idx = np.flatnonzero(etiquetas == mayor)
    return normalizar_con_autoinfluencia(adj[np.ix_(idx, idx)], s)


def matriz_karate(s: float = 1.0) -> np.ndarray:
    """Club de karate de Zachary (34 personas, no dirigida, viene en networkx)."""
    import networkx as nx
    G = nx.karate_club_graph()
    aristas = list(G.edges()) + [(j, i) for i, j in G.edges()]
    return matriz_desde_aristas(aristas, s)


def cargar_email_eu_core(ruta: str, s: float = 1.0, invertir: bool = False) -> np.ndarray:
    """Matriz A de Email-Eu-core a partir del archivo de aristas (.txt o .txt.gz).

    Cada línea del archivo es "u v" (u envió correos a v). Es una red DIRIGIDA.
    DECISIÓN PENDIENTE (Persona 2): qué significa influencia aquí.
        invertir=False -> u escucha a v (u pondera a quien le escribió).
        invertir=True  -> u escucha a quienes le escribieron a u.
    Justificar la elección en el informe. Se usa la componente fuertemente
    conexa más grande.
    """
    abrir = gzip.open if ruta.endswith(".gz") else open
    aristas = []
    with abrir(ruta, "rt") as f:
        for linea in f:
            partes = linea.split()
            if len(partes) >= 2 and not linea.startswith("#"):
                u, v = int(partes[0]), int(partes[1])
                aristas.append((v, u) if invertir else (u, v))
    return matriz_desde_aristas(aristas, s)
