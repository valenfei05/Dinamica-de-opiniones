"""Opiniones iniciales x(0)."""

import csv
import numpy as np
from src.predictor import calcular_espectro, componente_modo_lento


def generar_opiniones(n: int, tipo: str = "aleatoria", semilla: int = 0) -> np.ndarray:
    """Genera opiniones reproducibles entre cero y uno."""
    rng = np.random.default_rng(semilla)
    if tipo == "aleatoria":
        x = rng.random(n)
    elif tipo == "polarizada":
        base = rng.integers(0, 2, size=n).astype(float)
        x = np.clip(base + rng.normal(0, 0.05, size=n), 0, 1)
    elif tipo == "cercana":
        x = np.clip(0.5 + rng.normal(0, 0.01, size=n), 0, 1)
    else:
        x = rng.random(n)
        print("Tipo desconocido: se usa aleatoria")
    return x


def cargar_opiniones_csv(ruta: str, n: int, semilla: int = 0,
                         columna: str = "likert_scale_Q1") -> np.ndarray:
    """Toma n opiniones reales del CSV del profesor (escala 1-5 -> [0, 1])."""
    with open(ruta, newline="", encoding="utf-8") as f:
        valores = [float(fila[columna]) for fila in csv.DictReader(f)]
    rng = np.random.default_rng(semilla)
    elegidos = rng.choice(valores, size=n, replace=False)
    return (elegidos - 1.0) / 4.0


def opiniones_sin_modo_lento(A: np.ndarray, x0: np.ndarray) -> np.ndarray:
    """Quita de x0 su componente en el modo lento (caso extremo para probar la mejora)."""
    esp = calcular_espectro(A)
    x_lento = componente_modo_lento(esp, x0)
    x = x0 - x_lento
    # Traslada y escala sin alterar los modos no constantes.
    x = x - x.min()
    if x.max() > 0:
        x = x / x.max()
    return x
