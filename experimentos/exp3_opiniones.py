"""Experimento 3 (Persona 3): ¿cuánto importan las opiniones iniciales?"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))   # permite correr el archivo desde cualquier carpeta

from src.configuracion import PARAMETROS
from src.metricas import comparar_predicciones, guardar_tabla_csv, imprimir_tabla
from src.opiniones import (cargar_opiniones_csv, generar_opiniones,
                           opiniones_sin_modo_lento)
from src.redes import dos_comunidades_con_puente, matriz_karate

RUTA_CSV = RAIZ / "datos" / "PensionReform.csv"


def escenarios(A, n: int, sem: int) -> dict:
    """Escenarios de opiniones iniciales para la red A (reproducibles)."""
    esc = {
        "aleatoria": generar_opiniones(n, "aleatoria", sem),
        "polarizada": generar_opiniones(n, "polarizada", sem),
        "cercana": generar_opiniones(n, "cercana", sem),
    }
    esc["sin modo lento"] = opiniones_sin_modo_lento(A, esc["aleatoria"])
    if RUTA_CSV.exists():
        esc["CSV real"] = cargar_opiniones_csv(str(RUTA_CSV), n, sem)
    return esc


def main() -> list:
    p = dict(PARAMETROS)
    sem = p["semilla"]
    redes = {
        "dos_com": dos_comunidades_con_puente(p["n"], 0.3, p["autoinfluencia_s"]),
        "karate": matriz_karate(p["autoinfluencia_s"]),
    }
    filas = []
    for nombre, A in redes.items():
        for esc, x0 in escenarios(A, A.shape[0], sem).items():
            filas.append(comparar_predicciones(f"{nombre} | {esc}", A, x0, p))
    imprimir_tabla(filas)
    guardar_tabla_csv(filas, str(RAIZ / "resultados/tablas/exp3_opiniones.csv"))
    return filas


main()