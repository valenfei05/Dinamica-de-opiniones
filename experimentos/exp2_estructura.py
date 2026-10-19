"""Experimento 2 (Persona 2): ¿qué propiedades de la red explican tiempos y errores?"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))   # permite correr el archivo desde cualquier carpeta

from src.configuracion import PARAMETROS
from src.metricas import comparar_predicciones, guardar_tabla_csv, imprimir_tabla
from src.opiniones import generar_opiniones
from src.redes import (cargar_email_eu_core, construir_matriz,
                       dos_comunidades_con_puente, matriz_karate)

W_PUENTE = [1.0, 0.3, 0.1, 0.03]
AUTOINFLUENCIAS = [0.1, 0.5, 1.0, 3.0]
RUTA_EMAIL = RAIZ / "datos" / "email-Eu-core.txt"


def main() -> list:
    p = dict(PARAMETROS)
    n, sem = p["n"], p["semilla"]
    x0 = generar_opiniones(n, "aleatoria", sem)
    filas = []

    # (a) simetría
    for tipo in ["camino", "dos_comunidades", "aleatoria"]:
        for sim in (True, False):
            A = construir_matriz(tipo, n, sem, simetrica=sim, s=p["autoinfluencia_s"])
            filas.append(comparar_predicciones(f"{tipo} ({'sim' if sim else 'asim'})", A, x0, p))
    filas.append(comparar_predicciones("dirigida", construir_matriz("dirigida", n, sem), x0, p))

    # (b) peso del puente entre comunidades (s fija)
    for w in W_PUENTE:
        A = dos_comunidades_con_puente(n, w_puente=w, s=p["autoinfluencia_s"])
        filas.append(comparar_predicciones(f"dos_com puente w={w:g}", A, x0, p))

    # (c) autoinfluencia (puente fijo)
    for s in AUTOINFLUENCIAS:
        A = dos_comunidades_con_puente(n, w_puente=0.1, s=s)
        filas.append(comparar_predicciones(f"dos_com s={s:g}", A, x0, p))

    # (d) redes reales
    Ak = matriz_karate(p["autoinfluencia_s"])
    filas.append(comparar_predicciones(
        "karate (real)", Ak, generar_opiniones(Ak.shape[0], "aleatoria", sem), p))
    if RUTA_EMAIL.exists():
        Ae = cargar_email_eu_core(str(RUTA_EMAIL), p["autoinfluencia_s"])
        filas.append(comparar_predicciones(
            f"email-Eu-core (n={Ae.shape[0]})", Ae,
            generar_opiniones(Ae.shape[0], "aleatoria", sem), p))
    else:
        print("(Email-Eu-core no está en datos/: se omite. Ver datos/LEEME.txt)\n")

    imprimir_tabla(filas)
    guardar_tabla_csv(filas, str(RAIZ / "resultados/tablas/exp2_estructura.csv"))
    return filas


main()