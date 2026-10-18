"""
Primera prueba integrada en Karate Club (los 3, cuando estén listas las 3 partes).

Pasos del plan:
  1. Cargar Karate y construir A.        2. Comprobar que las filas suman 1.
  3. Calcular valores y vectores propios. 4. Generar opiniones reproducibles.
  5. Simular DeGroot y obtener T_tau.    6. Calcular T estimado con el predictor.
  7. Comparar tiempos y calcular errores.

Solo cuando esto funcione se pasa a Email-Eu-core.txt
Ejecutar desde la raíz:  python experimentos/prueba_integrada_karate.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))   # permite correr el archivo desde cualquier carpeta

import numpy as np

from src.configuracion import PARAMETROS
from src.metricas import error_relativo
from src.opiniones import generar_opiniones
from src.predictor import (calcular_espectro, predecir_T_corregida,
                           predecir_T_simple)
from src.redes import es_estocastica_por_filas, matriz_karate, verificar_estructura
from src.simulacion import calcular_limite, simular_degroot


def main() -> None:
    p = PARAMETROS
    A = matriz_karate(p["autoinfluencia_s"])                       # 1
    print(f"1. A construida: {A.shape[0]} personas")
    assert es_estocastica_por_filas(A), "las filas de A no suman 1"
    print("2. Todas las filas suman 1: OK")
    esp = calcular_espectro(A)                                     # 3
    print(f"3. rho = {esp.rho:.4f}; estructura: {verificar_estructura(A)}")
    x0 = generar_opiniones(A.shape[0], "aleatoria", p["semilla"])  # 4
    print("4. Opiniones iniciales generadas (semilla fija)")
    _, D, T_real = simular_degroot(A, x0, p["tau"], p["max_iter"])  # 5
    print(f"5. T_real = {T_real}")
    T_s = predecir_T_simple(esp.rho, D[0], p["tau"])                # 6
    T_c = predecir_T_corregida(esp, x0, p["tau"])
    print(f"6. T_simple = {T_s:.1f}   T_corregida = {T_c:.1f}")
    print(f"7. error relativo simple = {error_relativo(T_real, T_s):.3f}   "
          f"corregida = {error_relativo(T_real, T_c):.3f}")
    _, limite = calcular_limite(A, x0)                             # extra
    print(f"   Verificación extra: límite teórico (LU) = {limite:.4f}")


if __name__ == "__main__":
    main()
