"""
Lógica principal: decide qué tan bien combina un outfit.

La idea es imitar lo que uno piensa frente al espejo, pero con reglas:
  1. Colores  -> teoría del color básica (neutros, tonos tierra,
                 monocromático, análogos, complementarios). Pesa 40 %.
  2. Estilos  -> ¿las prendas son del mismo "mundo"? Un pantalón sastre con
                 tenis de correr se ve raro. Pesa 40 %.
  3. Clima    -> opcional. Si la persona dice que hace frío, una camisa de
                 lino no ayuda mucho. Pesa 20 % (si no hay clima, colores y
                 estilos quedan en 50 % cada uno).

Con eso sale un puntaje de 0 a 100, unos avisos amigables y sugerencias para
completar lo que falte.
"""

from dataclasses import dataclass, field
from itertools import combinations

from app.catalogo import (
    CATEGORIAS, CATEGORIAS_OBLIGATORIAS, CLIMAS, COLORES, LOOKS, NOMBRE_CLIMA,
    PRENDAS, Look, Prenda, nombre_color,
)


class SeleccionInvalida(ValueError):
    """Se lanza cuando llega una prenda o un clima que no existen."""


# ---------------------------------------------------------------- colores --

def relacion_colores(c1: str, c2: str) -> tuple:
    """Devuelve (tipo_de_relacion, puntaje entre 0 y 1) para dos colores."""
    if c1 == c2:
        return "monocromático", 1.0

    t1, t2 = COLORES[c1]["tono"], COLORES[c2]["tono"]
    if t1 is None or t2 is None:
        return "neutro", 1.0

    # distancia en el círculo cromático (lo máximo es 180°)
    distancia = abs(t1 - t2) % 360
    distancia = min(distancia, 360 - distancia)

    if distancia <= 60:
        return "análogos", 0.9
    if distancia >= 150:
        return "complementarios", 0.85
    # los tonos tierra (café, camel, oliva) se portan casi como neutros
    if "tierra" in (COLORES[c1]["familia"], COLORES[c2]["familia"]):
        return "tierra", 0.85
    return "atrevido", 0.5


EXPLICACION_COLOR = {
    "monocromático": "mismo color, se ve ordenado",
    "neutro": "un neutro combina con todo",
    "análogos": "están cerca en el círculo cromático",
    "complementarios": "son opuestos y hacen buen contraste",
    "tierra": "los tonos tierra son casi neutros",
    "atrevido": "no es una combinación clásica, puede chocar",
}


def _puntaje_colores(prendas: list) -> tuple:
    colores = sorted({p.color for p in prendas})
    detalles, avisos = [], []

    if len(colores) == 1:
        detalles.append(f"Todo en {nombre_color(colores[0])}: outfit monocromático.")
        return 1.0, detalles, avisos

    puntajes = []
    for c1, c2 in combinations(colores, 2):
        tipo, valor = relacion_colores(c1, c2)
        puntajes.append(valor)
        detalles.append(
            f"{nombre_color(c1).capitalize()} + {nombre_color(c2)}: {tipo} ({EXPLICACION_COLOR[tipo]})."
        )
        if tipo == "atrevido":
            avisos.append(
                f"El {nombre_color(c1)} con {nombre_color(c2)} es arriesgado. "
                "Si quieres jugar a lo seguro, cambia uno de los dos por un neutro."
            )

    # igual que con los estilos: promedio + la peor pareja
    valor = (sum(puntajes) / len(puntajes) + min(puntajes)) / 2

    # regla de los 3 colores: más de dos colores "protagonistas" satura
    protagonistas = [c for c in colores if COLORES[c]["familia"] == "color"]
    if len(protagonistas) > 2:
        valor -= 0.15
        avisos.append("Hay muchos colores peleando por atención; prueba dejando máximo dos protagonistas.")

    return max(valor, 0.0), detalles, avisos


# ---------------------------------------------------------------- estilos --

# Qué tan bien conviven dos estilos (1 = perfecto). La tabla es simétrica.
_COMPATIBILIDAD = {
    ("casual", "formal"): 0.7,
    ("casual", "bohemio"): 0.8,
    ("casual", "deportivo"): 0.7,
    ("formal", "bohemio"): 0.5,
    ("formal", "deportivo"): 0.2,
    ("bohemio", "deportivo"): 0.3,
}


def compatibilidad_estilos(e1: str, e2: str) -> float:
    if e1 == e2:
        return 1.0
    return _COMPATIBILIDAD.get((e1, e2)) or _COMPATIBILIDAD.get((e2, e1), 0.5)


def _compatibilidad_prendas(p1: Prenda, p2: Prenda) -> float:
    # una prenda puede tener varios estilos, me quedo con la mejor coincidencia
    return max(compatibilidad_estilos(a, b) for a in p1.estilos for b in p2.estilos)


def _puntaje_estilos(prendas: list) -> tuple:
    avisos = []
    valores = []
    for p1, p2 in combinations(prendas, 2):
        valor = _compatibilidad_prendas(p1, p2)
        valores.append(valor)
        if valor < 0.5:
            avisos.append(
                f"¿Estás segura? {p1.nombre} ({p1.estilos[0]}) y {p2.nombre.lower()} "
                f"({p2.estilos[0]}) no se llevan muy bien."
            )
    # promedio + peor pareja: una sola prenda que choca ya daña el outfit,
    # así que no dejo que el promedio la esconda
    return (sum(valores) / len(valores) + min(valores)) / 2, avisos


# ------------------------------------------------------------------ clima --

def _puntaje_clima(prendas: list, clima: str) -> tuple:
    no_aptas = [p for p in prendas if clima not in p.climas]
    avisos = [
        f"{p.nombre} no es muy de clima {NOMBRE_CLIMA[clima]}." for p in no_aptas
    ]
    return 1 - len(no_aptas) / len(prendas), avisos


# ------------------------------------------------------------- evaluación --

@dataclass
class Evaluacion:
    prendas: list
    clima: str | None = None
    puntaje: int | None = None
    etiqueta: str = ""
    detalles_color: list = field(default_factory=list)
    avisos: list = field(default_factory=list)
    faltantes: list = field(default_factory=list)
    sugerencias: dict = field(default_factory=dict)
    look: Look | None = None
    coincidencias: int = 0

    @property
    def look_exacto(self) -> bool:
        return self.look is not None and self.coincidencias == len(self.look.prendas) == len(self.prendas)


def validar_seleccion(seleccion: dict, clima: str | None = None) -> list:
    """
    Recibe algo como {"superior": "blusa_blanca", "calzado": ""} y devuelve la
    lista de objetos Prenda. Los valores vacíos se ignoran (la persona no
    eligió nada en esa categoría).
    """
    if clima and clima not in CLIMAS:
        raise SeleccionInvalida(f"El clima '{clima}' no existe. Usa: frío, templado o caluroso.")

    prendas = []
    for categoria, prenda_id in seleccion.items():
        if not prenda_id:
            continue
        if categoria not in CATEGORIAS:
            raise SeleccionInvalida(f"La categoría '{categoria}' no existe.")
        prenda = PRENDAS.get(prenda_id)
        if prenda is None:
            raise SeleccionInvalida(f"No encontré la prenda '{prenda_id}' en el clóset.")
        if prenda.categoria != categoria:
            raise SeleccionInvalida(
                f"'{prenda.nombre}' es de {CATEGORIAS[prenda.categoria].lower()}, "
                f"no de {CATEGORIAS[categoria].lower()}."
            )
        prendas.append(prenda)
    return prendas


def puntuar(prendas: list, clima: str | None = None) -> tuple:
    """Calcula el puntaje (0-100) de una lista de prendas. Necesita al menos 2."""
    p_color, detalles, avisos_color = _puntaje_colores(prendas)
    p_estilo, avisos_estilo = _puntaje_estilos(prendas)
    avisos = avisos_color + avisos_estilo

    if clima:
        p_clima, avisos_clima = _puntaje_clima(prendas, clima)
        avisos += avisos_clima
        total = 0.40 * p_color + 0.40 * p_estilo + 0.20 * p_clima
    else:
        total = 0.50 * p_color + 0.50 * p_estilo

    return round(total * 100), detalles, avisos


def etiqueta_puntaje(puntaje: int) -> str:
    if puntaje >= 90:
        return "¡Combina increíble!"
    if puntaje >= 75:
        return "Buen outfit"
    if puntaje >= 55:
        return "Se puede mejorar"
    return "Mejor probemos otra cosa"


def look_mas_parecido(prendas: list) -> tuple:
    """
    Busca el look (imagen) que más prendas comparte con la selección.
    Uso el índice de Jaccard: |A ∩ B| / |A ∪ B|, así un look con muchas prendas
    extra no gana solo por ser grande.
    """
    elegidas = {p.id for p in prendas}
    if not elegidas:
        return None, 0

    mejor, mejor_valor, mejor_comunes = None, 0.0, 0
    for look in LOOKS.values():
        del_look = set(look.prendas)
        comunes = len(elegidas & del_look)
        valor = comunes / len(elegidas | del_look)
        if valor > mejor_valor:
            mejor, mejor_valor, mejor_comunes = look, valor, comunes
    return mejor, mejor_comunes


def sugerir_complementos(prendas: list, clima: str | None = None) -> dict:
    """
    Para cada categoría obligatoria que falte, prueba todas las prendas del
    catálogo y se queda con la que deja el puntaje más alto.
    Si hace frío y no hay abrigo, también sugiere uno.
    """
    if not prendas:
        return {}

    tengo = {p.categoria for p in prendas}
    por_sugerir = [c for c in CATEGORIAS_OBLIGATORIAS if c not in tengo]
    if clima == "frio" and "abrigo" not in tengo:
        por_sugerir.append("abrigo")

    sugerencias = {}
    for categoria in por_sugerir:
        candidatas = [p for p in PRENDAS.values() if p.categoria == categoria]
        if clima:
            # primero las que sirven para el clima; si no hay, todas
            candidatas = [p for p in candidatas if clima in p.climas] or candidatas
        mejor = max(candidatas, key=lambda p: (puntuar(prendas + [p], clima)[0], p.id))
        sugerencias[categoria] = mejor
    return sugerencias


def evaluar_outfit(seleccion: dict, clima: str | None = None) -> Evaluacion:
    """Función que usan las rutas: valida, puntúa, busca avatar y sugiere."""
    clima = clima or None
    prendas = validar_seleccion(seleccion, clima)
    ev = Evaluacion(prendas=prendas, clima=clima)

    if not prendas:
        ev.etiqueta = "Elige al menos una prenda para vestir al avatar."
        return ev

    tengo = {p.categoria for p in prendas}
    ev.faltantes = [c for c in CATEGORIAS_OBLIGATORIAS if c not in tengo]
    ev.look, ev.coincidencias = look_mas_parecido(prendas)
    ev.sugerencias = sugerir_complementos(prendas, clima)

    if len(prendas) < 2:
        ev.etiqueta = "Con una sola prenda todavía no puedo decir si combina."
        return ev

    ev.puntaje, ev.detalles_color, ev.avisos = puntuar(prendas, clima)
    ev.etiqueta = etiqueta_puntaje(ev.puntaje)
    return ev
