# Proyecto: predecir el tiempo de consenso en una red de opiniones

## ¿Cuál es el problema?

En el modelo de DeGroot, las personas actualizan sus opiniones teniendo en cuenta las opiniones de otras personas de la red. Con el tiempo, esas opiniones pueden acercarse hasta alcanzar un consenso.

Existen herramientas matemáticas que permiten estimar qué tan rápido ocurre ese proceso. Sin embargo, esa estimación no siempre permite predecir con precisión cuántas iteraciones se necesitan para que las opiniones estén suficientemente cerca. Queremos entender por qué ocurre esa diferencia y si podemos mejorar la predicción.

## ¿Qué pregunta queremos responder?

**¿Podemos mejorar la predicción del número de iteraciones que necesita una red de opiniones para alcanzar el consenso, utilizando información adicional sobre la red y las opiniones iniciales?**

## ¿Cuál sería la respuesta?

Todavía no conocemos la respuesta; precisamente eso es lo que queremos investigar. Compararemos una estimación existente con los resultados de simulaciones para evaluar su precisión. Después estudiaremos en qué situaciones presenta errores y comprobaremos si incorporar información adicional permite reducirlos.

La mejora podría funcionar en algunos casos y no en otros. Nuestro objetivo es comprobarlo con resultados, sin asumir de antemano que el método será siempre más preciso.

## ¿Qué vamos a hacer?

1. **Revisar artículos y métodos existentes** para comprender cómo se estima el tiempo de consenso y qué limitaciones tienen esas estimaciones.
2. **Crear o seleccionar redes de prueba** y definir diferentes opiniones iniciales para cada caso.
3. **Simular la evolución de las opiniones** y registrar cuántas iteraciones necesitan para alcanzar un nivel de acuerdo previamente definido.
4. **Comparar las predicciones con los resultados de las simulaciones** para medir los errores e investigar de qué dependen.
5. **Evaluar una posible mejora** de la estimación y comprobar si funciona también en casos diferentes de los utilizados para diseñarla.

Primero trabajaremos con redes controladas para comprender mejor el comportamiento del modelo. Si resulta viable, podremos probar el método en una red real disponible públicamente.

## ¿Qué resultados esperamos obtener?

- Determinar qué tan precisa es la estimación existente y en qué situaciones presenta errores.
- Identificar qué características de la red o de las opiniones iniciales pueden ayudar a explicar esos errores.
- Comprobar si una estimación mejorada reduce el error y bajo qué condiciones funciona.
- Presentar tablas o gráficos comparativos, el código de las simulaciones y conclusiones sobre las ventajas y limitaciones del método.

No asumimos que la mejora será perfecta ni que necesariamente superará todos los métodos existentes. El resultado será la evidencia que obtengamos al comparar las alternativas.

## En una frase

**Queremos estudiar qué tan bien podemos predecir el tiempo que tarda una red de opiniones en alcanzar el consenso, entender por qué las estimaciones pueden fallar y comprobar si es posible mejorarlas.**

## Cómo correrlo

```bash
pip install -r requirements.txt
python experimentos/prueba_integrada_karate.py   # primero esta
python experimentos/exp1_prediccion.py
python experimentos/exp2_estructura.py
python experimentos/exp3_opiniones.py
```

Las tablas se guardan en `resultados/tablas/`.

  `predecir_T_simple` es un punto de partida, no una fórmula verificada.
- Persona 2: descargar Email-Eu-core y decidir/justificar la dirección de influencia
  (`cargar_email_eu_core`, parámetro `invertir`).
- La predicción corregida usa solo el modo lento (vectores propios izquierdo y derecho); si el modo lento no es simple o A es muy no normal, revisar con cuidado.
