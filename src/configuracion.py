PARAMETROS = {
    "n": 20,                  # personas en las redes sintéticas
    "tau": 1e-3,              # tolerancia: hay consenso aproximado si D(t) < tau
    "max_iter": 20000,        # tope de iteraciones; si se pasa -> "no alcanzada"
    "semilla": 42,            # semilla aleatoria (reproducibilidad)
    "autoinfluencia_s": 1.0,  # s en A = D^-1 (W + sI)
}
