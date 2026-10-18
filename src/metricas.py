"""
Métricas de error, comparación de predicciones y salida de resultados.
"""

import csv
import math

import numpy as np

from src.predictor import (ajustar_pendiente, calcular_espectro,
                           predecir_T_corregida, predecir_T_simple)
from src.redes import es_simetrica, verificar_estructura
from src.simulacion import simular_degroot


def error_absoluto(T_real, T_pred) -> float:
    """|T_real - T_pred|. NaN si falta alguno de los dos."""
    if T_real is None or T_pred is None or math.isnan(T_pred):
        return float("nan")
    return abs(T_real - T_pred)


def error_relativo(T_real, T_pred) -> float:
    """|T_real - T_pred| / T_real. NaN si falta alguno o T_real = 0."""
    if T_real is None or T_real == 0:
        return float("nan")
    return error_absoluto(T_real, T_pred) / T_real


def comparar_predicciones(nombre: str, A: np.ndarray, x0: np.ndarray, p: dict) -> dict:
    """Mide T_real y lo compara con la predicción simple y la corregida.

    Entradas : nombre del caso, A, x0, parámetros p (tau, max_iter).
    Salida   : dict (una fila de la tabla) con rho, T_real, T_simple, T_corr,
               errores relativos, rho_fit (mínimos cuadrados), simetrica y estructura.
    Si la estructura no es de consenso no se simula (no tiene sentido predecir T).
    """
    estructura = verificar_estructura(A)
    fila = {"caso": nombre, "simetrica": es_simetrica(A),
            "estructura": estructura["clasificacion"]}
    if estructura["clasificacion"] != "consenso":
        fila.update(rho=float("nan"), T_real=None, T_simple=float("nan"),
                    T_corr=float("nan"), err_simple=float("nan"),
                    err_corr=float("nan"), rho_fit=float("nan"))
        return fila

    esp = calcular_espectro(A)
    _, D, T_real = simular_degroot(A, x0, p["tau"], p["max_iter"])
    T_simple = predecir_T_simple(esp.rho, D[0], p["tau"])
    T_corr = predecir_T_corregida(esp, x0, p["tau"])
    _, rho_fit = ajustar_pendiente(D)
    fila.update(rho=esp.rho, T_real=T_real, T_simple=T_simple, T_corr=T_corr,
                err_simple=error_relativo(T_real, T_simple),
                err_corr=error_relativo(T_real, T_corr), rho_fit=rho_fit)
    return fila


def imprimir_tabla(filas: list) -> None:
    """Imprime los resultados en una tabla de texto."""
    enc = (f"{'caso':<34}{'sim':>5}{'rho':>8}{'rho_fit':>9}{'T_real':>8}"
           f"{'T_simple':>10}{'T_corr':>9}{'err_s':>8}{'err_c':>8}  estructura")
    print(enc)
    print("-" * len(enc))
    for f in filas:
        tr = "-" if f["T_real"] is None else str(f["T_real"])
        print(f"{f['caso']:<34}{'si' if f['simetrica'] else 'no':>5}"
              f"{f['rho']:>8.4f}{f['rho_fit']:>9.4f}{tr:>8}"
              f"{f['T_simple']:>10.1f}{f['T_corr']:>9.1f}"
              f"{f['err_simple']:>8.2f}{f['err_corr']:>8.2f}  {f['estructura']}")


def guardar_tabla_csv(filas: list, ruta: str) -> None:
    """Guarda la tabla de resultados en un CSV (carpeta resultados/tablas/)."""
    campos = ["caso", "simetrica", "estructura", "rho", "rho_fit", "T_real",
              "T_simple", "T_corr", "err_simple", "err_corr"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for fila in filas:
            w.writerow({k: fila[k] for k in campos})


def graficar_dispersion(A: np.ndarray, x0: np.ndarray, p: dict,
                        titulo: str = "", ruta_salida: str = None) -> None:
    """Gráfica de log D(t) con la recta de mínimos cuadrados (requiere matplotlib).

    Si se da ruta_salida guarda la figura (resultados/graficas/); si no, la muestra.
    """
    import matplotlib
    if ruta_salida:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    _, D, _ = simular_degroot(A, x0, p["tau"], p["max_iter"])
    pend, _ = ajustar_pendiente(D)
    t = np.arange(len(D))
    i0 = int(len(D) * 0.3)
    plt.figure()
    plt.semilogy(t, D, label="D(t) simulada")
    plt.semilogy(t, D[i0] * np.exp(pend * (t - i0)), "--",
                 label="ajuste por mínimos cuadrados")
    plt.axhline(p["tau"], color="gray", ls=":", label="tau")
    plt.xlabel("iteración t")
    plt.ylabel("dispersión D(t)")
    plt.title(titulo)
    plt.legend()
    if ruta_salida:
        plt.savefig(ruta_salida, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()
