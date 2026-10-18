"""
Experimento 1 (Persona 1): ¿qué tan bien predice el espectro el tiempo de consenso?

Misma red y mismas opiniones; se comparan las FÓRMULAS de predicción (simple vs
corregida) y se estudia cómo cambia el error al modificar la tolerancia tau.
Redes simétricas: es el mejor caso para el predictor espectral.

Ejecutar desde la raíz:  python experimentos/exp1_prediccion.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))   # permite correr el archivo desde cualquier carpeta

from src.configuracion import PARAMETROS
from src.metricas import comparar_predicciones, guardar_tabla_csv, imprimir_tabla
from src.opiniones import generar_opiniones
from src.redes import construir_matriz

TAUS = [1e-2, 1e-3, 1e-4]
REDES = ["completa", "anillo", "camino", "dos_comunidades", "aleatoria"]


def main() -> list:
    p = dict(PARAMETROS)
    x0 = generar_opiniones(p["n"], "aleatoria", p["semilla"])
    filas = []
    for tau in TAUS:
        p["tau"] = tau
        for tipo in REDES:
            A = construir_matriz(tipo, p["n"], p["semilla"])
            filas.append(comparar_predicciones(f"{tipo} (tau={tau:g})", A, x0, p))
    imprimir_tabla(filas)
    guardar_tabla_csv(filas, str(RAIZ / "resultados/tablas/exp1_prediccion.csv"))
    return filas


if __name__ == "__main__":
    main()
