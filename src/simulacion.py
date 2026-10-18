"""
Simulación del modelo de DeGroot   x(t+1) = A x(t)
"""

import numpy as np
from scipy.linalg import lu_factor, lu_solve


def simular_degroot(A: np.ndarray, x0: np.ndarray, tau: float, max_iter: int):
    """Simula x(t+1) = A x(t) hasta que la dispersión baje de tau.

    Dispersión: D(t) = max(x(t)) - min(x(t)).
    T_tau = primera iteración con D(t) < tau.

    Entradas : A (n x n), opiniones iniciales x0, tolerancia tau, máximo de iteraciones.
    Salidas  : (trayectoria, D, T_real)
        trayectoria : arreglo (pasos+1, n) con las opiniones en cada paso.
        D           : arreglo con la dispersión en cada paso.
        T_real      : T_tau, o None si "no alcanzada en el horizonte de simulación"
                      (esto NO prueba que nunca habrá consenso).
    """
    x = np.array(x0, dtype=float)
    trayectoria = [x.copy()]
    D = [x.max() - x.min()]
    if D[0] < tau:
        return np.array(trayectoria), np.array(D), 0
    for t in range(1, max_iter + 1):
        x = A @ x
        trayectoria.append(x.copy())
        D.append(x.max() - x.min())
        if D[-1] < tau:
            return np.array(trayectoria), np.array(D), t
    return np.array(trayectoria), np.array(D), None


def calcular_limite(A: np.ndarray, x0: np.ndarray):
    """Valor límite teórico del consenso: x* = (pi^T x0) * 1   (DeGroot, 1974).

    pi es el vector propio izquierdo de A asociado a 1, con suma 1. Se obtiene
    resolviendo con factorización LU el sistema (A^T - I) pi = 0 completado con
    la ecuación sum(pi) = 1.

    Salida: (pi, valor_limite). Solo tiene sentido si hay consenso.
    """
    n = A.shape[0]
    M = A.T - np.eye(n)
    M[-1, :] = 1.0                      # última ecuación: suma de pi = 1
    b = np.zeros(n)
    b[-1] = 1.0
    pi = lu_solve(lu_factor(M), b)
    return pi, float(pi @ x0)
