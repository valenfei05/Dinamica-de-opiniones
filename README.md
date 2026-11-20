# Centralidad, direccionalidad y consenso en el modelo de DeGroot

## Preguntas de investigación

Primera versión del proyecto: ¿Cómo influye la centralidad de los nodos en el número de iteraciones necesarias para alcanzar el consenso en diferentes estructuras de red bajo el modelo de DeGroot?

Versión final: ¿Cómo cambian la existencia y la velocidad del consenso cuando se orienta el puente entre dos comunidades, se agregan arcos y se repiten los escenarios de refuerzo de influencia?

## Qué se conservó

El experimento original permanece en `experimento.py` sin reestructurar su lógica: se mantienen las mismas redes iniciales: Karate Club, Camino y Dos comunidades, la centralidad de vector propio, la selección determinista de nodos, las cuatro intervenciones, las 20 semillas, las dos tolerancias y las 480 simulaciones. Se agregaron funciones de la fase dirigida al mismo archivo y verificaciones al final de `pruebas.py`. 

## Dependencias

Python 3.10+ y las bibliotecas declaradas en `requirements.txt`.

```bash
py -m pip install -r requirements.txt
```

En Linux/macOS se puede usar `python` o `python3` en lugar de `py`.

## Ejecución completa y reproducible

Desde esta carpeta, en este orden:

```bash
py experimento.py
py pruebas.py
py graficas_informe.py
py graficas_extension.py
```

- `experimento.py`: regenera la primera fase (480 simulaciones) y ejecuta la extensión (1.120 nuevas). Los resultados originales van a `resultados/`, los nuevos a `resultados/dirigidas/`.
- `pruebas.py`: verifica el diseño y los registros. Resultado esperado: **17 de 17 pruebas correctas**.
- `graficas_informe.py`: regenera las tres figuras originales del informe desde los CSV originales.
- `graficas_extension.py`: produce las figuras dirigidas, las siete tablas CSV para Canva y tres tablas en PNG; no repite simulaciones.

## Archivos de código

- `experimento.py`: código original, más `crear_redes_dirigidas()`, `crear_matriz_dirigida()`, `describir_red_dirigida()` y `ejecutar_extension_dirigida()`.
- `pruebas.py`: seis verificaciones originales y once adicionales sobre la extensión.
- `graficas_extension.py`: nuevo archivo para reproducir gráficas y tablas desde los CSV.

## Diseño experimental

La primera versión usa tres redes y cuatro escenarios:

1. Original, factor 1.
2. Centrales x2.
3. Centrales x3.
4. Perifericos x3.

En la versión final solo se modifica la red **Dos comunidades** (20 nodos). Sus conexiones internas siguen siendo bidireccionales, pero se estudian siete configuraciones:

1. **Puente bidireccional**: 9 → 10 y 10 → 9. Equivale al original.
2. **Sin puente**: los dos grupos no se comunican.
3. **Puente 9 a 10**: solo 9 → 10.
4. **Retorno central 10 a 9**: se agrega 10 → 9. Recupera exactamente el original y sirve como control.
5. **Retorno no puente 11 a 1**: se agrega 11 → 1 al puente 9 → 10.
6. **Avance central 9 a 11**: se agrega 9 → 11 al puente 9 → 10.
7. **Avance no puente 1 a 11**: se agrega 1 → 11 al puente 9 → 10.

En cada una se repiten **los cuatro escenarios de peso**, las **20 semillas de 0 a 19** y **ambas tolerancias 0.001 y 0.01**:

`7 x 4 x 20 x 2 = 1120` experimentos nuevos. Total sumado a la primera versión: `1600` ejecuciones registradas.

### Convención de los grafos dirigidos

La flecha `u -> v` se interpreta como **u influye sobre v**. NetworkX almacena el arco en `B[u,v]`, mientras que DeGroot expresa cuánto escucha v a u en `A[v,u]`. Por eso, solo para las redes dirigidas se construye la matriz de pesos con `M = B.T + I` antes de reforzar columnas y normalizar filas.

Se usan los mismos nodos centrales y periféricos seleccionados sobre la red original no dirigida. Esto evita cambiar simultáneamente la estructura y el criterio de centralidad. En la red Dos comunidades los tres centrales son 9, 10 y 0, y los tres periféricos por desempate son 1, 2 y 3. El nodo 11 tiene la misma centralidad que varios nodos no puente, pero no está entre los tres elegidos como periféricos, por eso los escenarios de arcos se llaman **no puente** y no **periféricos**.

### Consenso, conectividad y SLEM

La condición numérica es `max(opiniones) - min(opiniones) <= tolerancia`. Las ejecuciones que no cumplen dentro de 20.000 iteraciones almacenan el campo de iteraciones vacío y `convergio=False`.

En un grafo dirigido, no ser fuertemente conexo **no implica automáticamente** que DeGroot no pueda alcanzar un consenso. Con un puente de 9 hacia 10 existe una única comunidad fuente de influencia y se observó convergencia. Sin puente existen dos fuentes independientes y no hay garantía de consenso global. Para esta configuración, el valor propio 1 tiene multiplicidad dos: aunque se registra un segundo módulo propio igual a 1, **no se interpreta como velocidad de consenso global**.

Con tolerancia 0.001, ninguno de los 80 casos de «Sin puente» alcanzó el criterio; con tolerancia 0.01, tres de 80 casos lo alcanzaron por cercanía accidental entre las opiniones de ambos grupos, no por transmisión de información.

## Resultados y tablas para el póster

`resultados/dirigidas/`:

- `experimentos_dirigidos.csv`: 1.120 registros individuales, incluye opinión final y brecha entre comunidades.
- `resumen_dirigidas.csv`: promedio, desviación, número de consensos y comparaciones emparejadas.
- `espectros_dirigidos.csv`: SLEM, multiplicidad de 1 y selección de nodos.
- `conectividad_dirigida.csv`: cantidad de arcos, conectividad fuerte/débil, componentes fuertes y fuentes.

`resultados/tablas_poster/`:

- `01_primera_fase.csv`: resumen de las tres redes, tolerancia 0.001.
- `02_conectividad.csv`: diferencias estructurales entre las siete redes dirigidas.
- `03_extension_completa_0001.csv`: todos los escenarios dirigidos y cambio porcentual respecto a la línea base del mismo escenario.
- `04_comparacion_esencial_poster.csv`: Original y Centrales x3 en las siete configuraciones.
- `05_casos_emparejados.csv`: mejoras y empeoramientos frente al Original de cada configuración.
- `06_opiniones_y_brechas.csv`: opiniones finales y brechas residuales.
- `07_sensibilidad_tolerancias.csv`: ambas tolerancias, todos los escenarios y convergencia.
- `tabla_01_primera_fase.png`, `tabla_02_extension_esencial.png`, `tabla_03_conectividad.png`: tablas de alta resolución.