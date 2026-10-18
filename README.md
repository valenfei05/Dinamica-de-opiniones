# Degroot-espectral

Proyecto de Computación Científica (PUJ Cali): **alcances y límites del análisis
espectral para predecir el comportamiento del modelo de DeGroot**, comparado con
Friedkin–Johnsen (FJ).

Pregunta principal: ¿qué tan bien permite el espectro de la matriz de influencia
predecir el comportamiento y la velocidad de convergencia en condiciones de
observación finita y ante perturbaciones de la red, y cómo cambia al incorporar
persistencia de las opiniones iniciales (FJ)?

## Cómo correrlo

```bash
pip install -r requirements.txt
python experimentos/prueba_integrada_karate.py   # primero esta
python experimentos/exp1_prediccion.py
python experimentos/exp2_estructura.py
python experimentos/exp3_opiniones.py
```

Las tablas se guardan en `resultados/tablas/`.

## Estructura

```
datos/           PensionReform.csv (opiniones) y, cuando se descargue, email-Eu-core.txt.gz
src/
  configuracion.py   parámetros acordados (n, tau, max_iter, semilla, s)
  simulacion.py      simular_degroot, calcular_limite (LU)            -> Persona 3
  predictor.py       espectro, predicción simple y corregida, mínimos cuadrados -> Persona 1
  redes.py           construcción de A, propiedades, redes reales      -> Persona 2
  opiniones.py       opiniones iniciales y lectura del CSV             -> Persona 3
  metricas.py        errores, comparar_predicciones, tablas, gráficas  -> Persona 3
experimentos/
  exp1_prediccion.py   Persona 1
  exp2_estructura.py   Persona 2
  exp3_opiniones.py    Persona 3
  prueba_integrada_karate.py   los 3
resultados/tablas, resultados/graficas
```

## Pendientes

- Persona 1: confirmar con Lu, Sun y Liu (2017) la estimación de la literatura;
  `predecir_T_simple` es un punto de partida, no una fórmula verificada.
- Persona 2: descargar Email-Eu-core y decidir/justificar la dirección de influencia
  (`cargar_email_eu_core`, parámetro `invertir`).
- La predicción corregida usa solo el modo lento (vectores propios izquierdo y derecho); si el modo lento no es simple o A es muy no normal, revisar con cuidado.