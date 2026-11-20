"""
Botón "Sorpréndeme": arma un outfit al azar... pero que combine.

No es azar puro: elige una parte superior al azar y después, para cada
categoría, ordena las opciones por puntaje y escoge al azar entre las 3
mejores. Así cada vez sale algo distinto pero con sentido.
Si el resultado no llega a 85, lo vuelve a intentar (máximo 30 veces) y se
queda con el mejor.
"""

import random

from app.catalogo import CLIMAS, ESTILOS, PRENDAS
from app.combinador import SeleccionInvalida, compatibilidad_estilos, puntuar

META = 85


def _candidatas(categoria, estilo, clima):
    todas = [p for p in PRENDAS.values() if p.categoria == categoria]
    if clima:
        todas = [p for p in todas if clima in p.climas] or todas
    del_estilo = [p for p in todas if estilo in p.estilos]
    if del_estilo:
        return del_estilo
    # si no hay del mismo estilo (ej: abrigo deportivo), uso uno compatible
    return [p for p in todas if max(compatibilidad_estilos(estilo, e) for e in p.estilos) >= 0.7]


def _mejor_entre_top(base, opciones, clima, rng, top=3):
    if not opciones:
        return None
    ordenadas = sorted(opciones, key=lambda p: (puntuar(base + [p], clima)[0], p.id), reverse=True)
    return rng.choice(ordenadas[:top])


def sorprender(estilo=None, clima=None, semilla=None, intentos=30) -> tuple:
    """Devuelve (lista_de_prendas, puntaje)."""
    estilo, clima = estilo or None, clima or None
    if estilo and estilo not in ESTILOS:
        raise SeleccionInvalida(f"El estilo '{estilo}' no existe.")
    if clima and clima not in CLIMAS:
        raise SeleccionInvalida(f"El clima '{clima}' no existe.")

    rng = random.Random(semilla)
    mejor, mejor_puntaje = None, -1

    for _ in range(intentos):
        est = estilo or rng.choice(ESTILOS)
        elegidas = [rng.choice(_candidatas("superior", est, clima))]

        for categoria in ("inferior", "calzado"):
            elegida = _mejor_entre_top(elegidas, _candidatas(categoria, est, clima), clima, rng)
            if elegida:
                elegidas.append(elegida)

        # extras: solo se agregan si no bajan el puntaje
        quiere_abrigo = clima == "frio" or (clima != "caluroso" and rng.random() < 0.45)
        extras = [("abrigo", quiere_abrigo), ("bolso", rng.random() < 0.75),
                  ("cuello", rng.random() < 0.4), ("cabeza", rng.random() < 0.3)]
        for categoria, quiere in extras:
            if not quiere:
                continue
            extra = _mejor_entre_top(elegidas, _candidatas(categoria, est, clima), clima, rng)
            if extra and puntuar(elegidas + [extra], clima)[0] >= puntuar(elegidas, clima)[0] - 2:
                elegidas.append(extra)

        puntaje = puntuar(elegidas, clima)[0]
        if puntaje > mejor_puntaje:
            mejor, mejor_puntaje = elegidas, puntaje
        if puntaje >= META:
            break

    return mejor, mejor_puntaje
