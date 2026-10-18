"""
Predictores del tiempo de consenso (espectro de A).

PENDIENTE (Persona 1): confirmar contra Lu, Sun y Liu (2017) cuál es la estimación
exacta de la literatura y sus hipótesis. predecir_T_simple es un punto de partida,
NO se debe presentar como "la fórmula de la literatura" hasta verificarlo.
"""

import math
from dataclasses import dataclass

import numpy as np
from scipy.linalg import eig


@dataclass
class Espectro:
    """Resultado de calcular_espectro.

    valores      : valores propios de A ordenados por módulo (mayor primero).
    vectores     : vectores propios por la derecha (columnas), mismo orden.
    izquierdos   : vectores propios por la izquierda (columnas), mismo orden.
    idx_consenso : posición del valor propio igual a 1.
    rho          : segundo valor propio dominante (módulo), descartando UNA copia
                   de lambda = 1. Si rho = 1 hay oscilación o grupos separados.
    """
    valores: np.ndarray
    vectores: np.ndarray
    izquierdos: np.ndarray
    idx_consenso: int
    rho: float


def calcular_espectro(A: np.ndarray) -> Espectro:
    """Valores y vectores propios (derechos e izquierdos) de A y rho."""
    valores, izq, der = eig(A, left=True, right=True)
    orden = np.argsort(-np.abs(valores))
    valores, izq, der = valores[orden], izq[:, orden], der[:, orden]
    idx = int(np.argmin(np.abs(valores - 1.0)))
    resto = np.delete(np.arange(len(valores)), idx)
    rho = float(np.abs(valores[resto]).max())
    return Espectro(valores, der, izq, idx, rho)


def predecir_T_simple(rho: float, D0: float, tau: float) -> float:
    """Predicción simple: T = ln(tau / D0) / ln(rho).

    Supone que todo el desacuerdo inicial D0 está en el modo lento (ignora la
    constante C de la cota |x_i(t) - x*_i| <= C rho^t).

    Casos especiales: D0 <= tau -> 0;  rho == 0 -> 1;  rho >= 1 -> NaN.
    """
    if D0 <= tau:
        return 0.0
    if rho == 0:
        return 1.0
    if rho >= 1.0 - 1e-12:
        return float("nan")
    return math.log(tau / D0) / math.log(rho)


def ajustar_pendiente(D: np.ndarray, fraccion_inicial: float = 0.3):
    """Ajuste por mínimos cuadrados de la recta  log D(t) = a t + b.

    Se descarta la fracción inicial (transitorio de los modos rápidos).
    Salida: (pendiente, rho_ajustado = exp(pendiente)); compárese con rho teórico.
    """
    D = np.asarray(D, dtype=float)
    inicio = int(len(D) * fraccion_inicial)
    t = np.arange(len(D))[inicio:]
    y = np.log(np.clip(D[inicio:], 1e-300, None))
    if len(t) < 3:
        return float("nan"), float("nan")
    X = np.column_stack([t, np.ones_like(t)])
    (pendiente, _), *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(pendiente), float(math.exp(pendiente))


def componente_modo_lento(esp: Espectro, x0: np.ndarray, tol: float = 1e-7) -> np.ndarray:
    """Parte de x(0) que cae en el modo lento (el de módulo rho).

    Para cada modo lento k, con vectores propios derecho v_k e izquierdo w_k:
        coeficiente c_k = (w_k^H x0) / (w_k^H v_k),   aporte = c_k v_k.
    Si el modo lento es un par complejo se suman ambos y se toma la parte real.
    Se usa solo el modo lento (no hace falta invertir toda la matriz de vectores
    propios), lo que evita problemas numéricos cuando hay valores propios repetidos.

    Salida: x_lento, vector con la contribución del modo lento a x(0).
    """
    x_lento = np.zeros(len(x0), dtype=complex)
    for k in range(len(esp.valores)):
        if k == esp.idx_consenso or abs(abs(esp.valores[k]) - esp.rho) >= tol:
            continue
        v, w = esp.vectores[:, k], esp.izquierdos[:, k]
        den = np.vdot(w, v)
        if abs(den) > 1e-14:
            x_lento += (np.vdot(w, x0) / den) * v
    return np.real(x_lento)


def predecir_T_corregida(esp: Espectro, x0: np.ndarray, tau: float) -> float:
    """Predicción corregida: T = ln(tau / K) / ln(rho).

    K = dispersión (max - min) de la parte de x(0) en el modo lento.
    """
    x_lento = componente_modo_lento(esp, x0)
    K = float(x_lento.max() - x_lento.min())
    return predecir_T_simple(esp.rho, K, tau)
