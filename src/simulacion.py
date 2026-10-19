"""Simulación del modelo de DeGroot   x(t+1) = A x(t)"""

import numpy as np
from scipy.linalg import lu_factor, lu_solve


def simular_degroot(A: np.ndarray, x0: np.ndarray, tau: float, max_iter: int):
    """Simula DeGroot hasta lograr consenso aproximado."""
    x = np.array(x0, dtype=float)
    trayectoria = [x.copy()]
    D = [float(np.ptp(x))]
    t = 0
    while D[-1] > tau and t < max_iter:
        x = A @ x
        t += 1
        trayectoria.append(x.copy())
        D.append(float(np.ptp(x)))
    T_real = t if D[-1] <= tau else None
    return np.array(trayectoria), np.array(D), T_real


def calcular_limite(A: np.ndarray, x0: np.ndarray):
    """Valor límite teórico del consenso: x* = (pi^T x0) * 1   (DeGroot, 1974)."""
    n = A.shape[0]
    M = A.T - np.eye(n)
    M[-1, :] = 1.0                      # última ecuación: suma de pi = 1
    b = np.zeros(n)
    b[-1] = 1.0
    pi = lu_solve(lu_factor(M), b)
    return pi, float(pi @ x0)
