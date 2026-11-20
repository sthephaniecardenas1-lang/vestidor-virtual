"""
Recomendador: la persona dice qué color, estilo o clima quiere y le muestro
los looks del catálogo ordenados por afinidad.

Puntos por cada filtro:
  color  -> 40 si es el color principal del look, 20 si alguna prenda lo tiene,
            10 si el color del look armoniza con el pedido.
  estilo -> 30 si es igual, 15 si son compatibles (>= 0.7).
  clima  -> 30 si es igual, 10 si todas las prendas aguantan ese clima.

La afinidad es el porcentaje sobre el máximo posible de los filtros usados.
Si hay empate, gana el look que mejor combina por sí solo.
"""

from dataclasses import dataclass

from app.catalogo import CLIMAS, COLORES, ESTILOS, LOOKS, NOMBRE_CLIMA, PRENDAS, Look, nombre_color
from app.combinador import SeleccionInvalida, compatibilidad_estilos, puntuar, relacion_colores


@dataclass
class Recomendacion:
    look: Look
    afinidad: int
    armonia: int
    razones: list


def armonia_look(look: Look) -> int:
    prendas = [PRENDAS[p] for p in look.prendas]
    return puntuar(prendas, look.clima)[0]


def recomendar(color: str | None = None, estilo: str | None = None,
               clima: str | None = None, cantidad: int = 3) -> list:
    color, estilo, clima = color or None, estilo or None, clima or None

    if not (color or estilo or clima):
        raise SeleccionInvalida("Elige al menos un filtro: color, estilo o clima.")
    if color and color not in COLORES:
        raise SeleccionInvalida(f"El color '{color}' no está en la paleta.")
    if estilo and estilo not in ESTILOS:
        raise SeleccionInvalida(f"El estilo '{estilo}' no existe.")
    if clima and clima not in CLIMAS:
        raise SeleccionInvalida(f"El clima '{clima}' no existe.")
    if cantidad < 1:
        raise SeleccionInvalida("La cantidad de recomendaciones debe ser al menos 1.")

    maximo = (40 if color else 0) + (30 if estilo else 0) + (30 if clima else 0)
    resultados = []

    for look in LOOKS.values():
        prendas = [PRENDAS[p] for p in look.prendas]
        puntos, razones = 0, []

        if color:
            if look.color == color:
                puntos += 40
                razones.append(f"El {nombre_color(color)} es el protagonista.")
            elif any(p.color == color for p in prendas):
                puntos += 20
                razones.append(f"Tiene detalles en {nombre_color(color)}.")
            else:
                tipo, valor = relacion_colores(look.color, color)
                if valor >= 0.85 and tipo != "neutro":
                    puntos += 10
                    razones.append(f"Su {nombre_color(look.color)} y el {nombre_color(color)} son {tipo}.")

        if estilo:
            compat = compatibilidad_estilos(look.estilo, estilo)
            if compat == 1.0:
                puntos += 30
                razones.append(f"Es estilo {estilo}.")
            elif compat >= 0.7:
                puntos += 15
                razones.append(f"Es {look.estilo}, que se acerca al {estilo}.")

        if clima:
            if look.clima == clima:
                puntos += 30
                razones.append(f"Pensado para clima {NOMBRE_CLIMA[clima]}.")
            elif all(clima in p.climas for p in prendas):
                puntos += 10
                razones.append(f"Todas sus prendas sirven para clima {NOMBRE_CLIMA[clima]}.")

        if puntos == 0:
            continue
        afinidad = round(puntos / maximo * 100)
        resultados.append(Recomendacion(look, afinidad, armonia_look(look), razones))

    resultados.sort(key=lambda r: (r.afinidad, r.armonia), reverse=True)
    return resultados[:cantidad]
