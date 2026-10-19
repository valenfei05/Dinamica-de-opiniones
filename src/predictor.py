"""Predictores del tiempo de consenso (espectro de A)."""

import math
from dataclasses import dataclass

import numpy as np
from scipy.linalg import eig


@dataclass
class Espectro:
    """Resultado de calcular_espectro."""
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
    """Tiempo aproximado usando el segundo módulo propio."""
    tiempo = float("nan")
    if D0 <= tau:
        tiempo = 0.0
    elif rho < 1e-12:
        tiempo = 1.0
    elif rho < 1 - 1e-12:
        tiempo = float(math.ceil(math.log(tau / D0) / math.log(rho)))
    return tiempo


def ajustar_pendiente(D: np.ndarray, fraccion_inicial: float = 0.3):
    """Ajusta log(D) por mínimos cuadrados."""
    D = np.asarray(D, dtype=float)
    inicio = int(len(D) * fraccion_inicial)
    t = np.arange(len(D))[inicio:]
    pendiente, rho = float("nan"), float("nan")
    if len(t) >= 3:
        y = np.log(np.clip(D[inicio:], 1e-300, None))
        X = np.column_stack([t, np.ones_like(t)])
        coeficientes = np.linalg.lstsq(X, y, rcond=None)[0]
        pendiente = float(coeficientes[0])
        rho = float(math.exp(pendiente))
    return pendiente, rho


def componente_modo_lento(esp: Espectro, x0: np.ndarray, tol: float = 1e-7) -> np.ndarray:
    """Parte de x(0) que cae en el modo lento (el de módulo rho)."""
    x_lento = np.zeros(len(x0), dtype=complex)
    for k in range(len(esp.valores)):
        if k != esp.idx_consenso and abs(abs(esp.valores[k]) - esp.rho) < tol:
            v, w = esp.vectores[:, k], esp.izquierdos[:, k]
            den = np.vdot(w, v)
            if abs(den) > 1e-14:
                x_lento += (np.vdot(w, x0) / den) * v
    return np.real(x_lento)


def predecir_T_corregida(esp: Espectro, x0: np.ndarray, tau: float) -> float:
    """Predicción corregida: T = ln(tau / K) / ln(rho)."""
    x_lento = componente_modo_lento(esp, x0)
    K = float(x_lento.max() - x_lento.min())
    return predecir_T_simple(esp.rho, K, tau)
