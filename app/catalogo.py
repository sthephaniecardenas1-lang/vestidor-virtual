"""
Catálogo del vestidor: colores, prendas y looks.

Todo está "quemado" en el código a propósito. Para este proyecto no necesitaba
una base de datos, lo importante era la lógica de combinación, así que preferí
tener los datos a la mano y fáciles de leer.

Cada prenda sale de uno de mis looks de referencia (las imágenes de
static/img/looks). Algunas prendas se repiten en varios looks, por ejemplo los
tenis blancos o la blusa blanca, igual que pasa en un clóset de verdad.
"""

from dataclasses import dataclass
from urllib.parse import urlencode

CATEGORIAS = {
    "superior": "Parte superior",
    "inferior": "Parte inferior",
    "abrigo": "Abrigo / chaqueta",
    "calzado": "Calzado",
    "bolso": "Bolso",
    "cuello": "Cuello",
    "cabeza": "Cabeza",
}

# Sin estas tres el outfit queda incompleto (no tengo vestidos en el catálogo)
CATEGORIAS_OBLIGATORIAS = ("superior", "inferior", "calzado")

ESTILOS = ("casual", "formal", "bohemio", "deportivo")
CLIMAS = ("frio", "templado", "caluroso")
NOMBRE_CLIMA = {"frio": "frío", "templado": "templado", "caluroso": "caluroso"}

# tono = posición aproximada en el círculo cromático (grados).
# Los neutros no tienen tono porque combinan con todo.
COLORES = {
    "blanco": {"hex": "#f6f3ec", "tono": None, "familia": "neutro"},
    "negro":  {"hex": "#1f1d1c", "tono": None, "familia": "neutro"},
    "gris":   {"hex": "#a5a5a3", "tono": None, "familia": "neutro"},
    "beige":  {"hex": "#d8c3a5", "tono": None, "familia": "neutro"},
    "crema":  {"hex": "#efe4cf", "tono": None, "familia": "neutro"},
    "dorado": {"hex": "#c9a24a", "tono": None, "familia": "neutro"},
    "cafe":   {"hex": "#6b4430", "tono": 25,   "familia": "tierra"},
    "camel":  {"hex": "#b07a45", "tono": 35,   "familia": "tierra"},
    "oliva":  {"hex": "#6f7346", "tono": 75,   "familia": "tierra"},
    "verde":  {"hex": "#3f8f5a", "tono": 130,  "familia": "color"},
    "azul":   {"hex": "#22345c", "tono": 220,  "familia": "color"},
    "rosa":   {"hex": "#e3a6b0", "tono": 340,  "familia": "color"},
}

NOMBRE_COLOR = {"cafe": "café"}  # el resto se escribe igual


def nombre_color(color: str) -> str:
    return NOMBRE_COLOR.get(color, color)


@dataclass(frozen=True)
class Prenda:
    id: str
    nombre: str
    categoria: str
    color: str
    estilos: tuple
    climas: tuple = CLIMAS  # por defecto sirve para cualquier clima


@dataclass(frozen=True)
class Look:
    id: str
    nombre: str
    descripcion: str
    color: str
    estilo: str
    clima: str
    prendas: tuple  # ids de prendas

    def query_probador(self) -> str:
        """Arma el query string para abrir este look en el probador."""
        params = {PRENDAS[p].categoria: p for p in self.prendas}
        params["enviado"] = "1"
        return urlencode(params)


_LISTA_PRENDAS = [
    # ---- parte superior ----
    Prenda("blusa_campesina", "Blusa campesina", "superior", "crema", ("bohemio",), ("templado", "caluroso")),
    Prenda("camisola_satin_rosa", "Camisola de satín", "superior", "rosa", ("bohemio", "formal"), ("caluroso", "templado")),
    Prenda("camisa_lino_verde", "Camisa de lino", "superior", "verde", ("casual",), ("caluroso", "templado")),
    Prenda("blusa_satin_marfil", "Blusa de satín marfil", "superior", "crema", ("formal",), ("templado", "frio")),
    Prenda("sueter_cuello_alto_blanco", "Suéter tejido de cuello alto", "superior", "blanco", ("casual",), ("frio",)),
    Prenda("camiseta_negra", "Camiseta ajustada", "superior", "negro", ("casual",), ("templado", "caluroso")),
    Prenda("blusa_blanca", "Blusa de cuello en V", "superior", "blanco", ("formal", "casual"), ("templado", "caluroso")),
    Prenda("sueter_trenzado_cafe", "Suéter trenzado", "superior", "cafe", ("casual",), ("frio",)),
    Prenda("camisa_anudada_blanca", "Camisa de lino anudada", "superior", "blanco", ("casual",), ("caluroso",)),
    Prenda("blusa_encaje_crema", "Blusa de encaje", "superior", "crema", ("bohemio",), ("templado", "caluroso")),
    Prenda("esqueleto_salvia", "Esqueleto deportivo", "superior", "verde", ("deportivo",), ("caluroso", "templado")),
    Prenda("cuello_alto_negro", "Cuello alto acanalado", "superior", "negro", ("formal", "casual"), ("frio", "templado")),
    Prenda("camiseta_blanca", "Camiseta básica", "superior", "blanco", ("casual", "deportivo"), ("caluroso", "templado")),
    # ---- parte inferior ----
    Prenda("pantalon_acampanado_camel", "Pantalón acampanado", "inferior", "camel", ("bohemio",), ("templado", "frio")),
    Prenda("falda_plisada_rosa", "Falda plisada larga", "inferior", "rosa", ("bohemio", "formal"), ("caluroso", "templado")),
    Prenda("falda_midi_oliva", "Falda midi", "inferior", "oliva", ("casual", "bohemio"), ("caluroso", "templado")),
    Prenda("pantalon_sastre_beige", "Pantalón sastre", "inferior", "beige", ("formal",), ("templado", "frio")),
    Prenda("pantalon_pana_blanco", "Pantalón de pana", "inferior", "blanco", ("casual",), ("frio",)),
    Prenda("jean_negro", "Jean ajustado", "inferior", "negro", ("casual",), ("templado", "frio")),
    Prenda("pantalon_sastre_azul", "Pantalón sastre", "inferior", "azul", ("formal",), ("templado", "frio")),
    Prenda("pantalon_recto_camel", "Pantalón recto", "inferior", "camel", ("casual",), ("frio", "templado")),
    Prenda("pantalon_sastre_gris", "Pantalón sastre", "inferior", "gris", ("formal",), ("templado", "frio")),
    Prenda("pantalon_lino_blanco", "Pantalón ancho de lino", "inferior", "blanco", ("casual",), ("caluroso",)),
    Prenda("falda_escalonada_beige", "Falda larga escalonada", "inferior", "beige", ("bohemio",), ("templado", "caluroso")),
    Prenda("licra_ciclista_verde", "Licra ciclista", "inferior", "verde", ("deportivo",), ("caluroso", "templado")),
    Prenda("pantalon_sastre_negro", "Pantalón sastre", "inferior", "negro", ("formal",), ("frio", "templado")),
    Prenda("jean_mom_azul", "Jean mom", "inferior", "azul", ("casual",), ("templado", "frio")),
    # ---- calzado ----
    Prenda("botas_vaqueras_cafe", "Botas vaqueras", "calzado", "cafe", ("bohemio",), ("templado", "frio")),
    Prenda("sandalias_doradas", "Sandalias de tiras doradas", "calzado", "beige", ("bohemio", "formal"), ("caluroso",)),
    Prenda("sandalias_planas_camel", "Sandalias planas", "calzado", "camel", ("casual", "bohemio"), ("caluroso",)),
    Prenda("bailarinas_nude", "Bailarinas de punta", "calzado", "beige", ("formal", "casual"), ("templado", "caluroso")),
    Prenda("tenis_blancos", "Tenis blancos", "calzado", "blanco", ("casual",)),
    Prenda("botines_negros", "Botines de cuero", "calzado", "negro", ("casual", "formal"), ("templado", "frio")),
    Prenda("tacones_azules", "Tacones de punta", "calzado", "azul", ("formal",), ("templado",)),
    Prenda("botines_cafe", "Botines Chelsea", "calzado", "cafe", ("casual",), ("frio", "templado")),
    Prenda("bailarinas_rosa", "Bailarinas", "calzado", "rosa", ("formal", "casual"), ("templado", "caluroso")),
    Prenda("sandalias_tacon_nude", "Sandalias de tacón bajo", "calzado", "beige", ("casual", "formal"), ("caluroso",)),
    Prenda("botines_gamuza_camel", "Botines de gamuza", "calzado", "camel", ("bohemio",), ("templado", "frio")),
    Prenda("tenis_running", "Tenis de running", "calzado", "blanco", ("deportivo",)),
    # ---- abrigos ----
    Prenda("chaqueta_flecos", "Chaqueta de gamuza con flecos", "abrigo", "cafe", ("bohemio",), ("templado", "frio")),
    Prenda("gabardina_beige", "Gabardina", "abrigo", "beige", ("formal",), ("templado", "frio")),
    Prenda("chaqueta_cuero_negra", "Chaqueta de cuero", "abrigo", "negro", ("casual",), ("templado", "frio")),
    Prenda("blazer_azul", "Blazer", "abrigo", "azul", ("formal",), ("templado",)),
    Prenda("cardigan_rosa", "Cárdigan de punto", "abrigo", "rosa", ("casual", "formal"), ("templado", "frio")),
    Prenda("abrigo_largo_negro", "Abrigo largo de paño", "abrigo", "negro", ("formal",), ("frio",)),
    Prenda("chaqueta_jean", "Chaqueta de jean", "abrigo", "azul", ("casual",), ("templado",)),
    # ---- bolsos ----
    Prenda("bolso_montura_cafe", "Bolso de cuero tipo montura", "bolso", "cafe", ("bohemio", "casual")),
    Prenda("bolso_champagne", "Bolso pequeño champagne", "bolso", "beige", ("bohemio", "formal")),
    Prenda("bolso_paja", "Bolso de paja", "bolso", "beige", ("casual", "bohemio"), ("caluroso", "templado")),
    Prenda("tote_beige", "Bolso tote", "bolso", "beige", ("formal",)),
    Prenda("gorro_tejido_blanco", "Gorro tejido", "cabeza", "blanco", ("casual",), ("frio",)),
    Prenda("bandolera_negra", "Bolso bandolera", "bolso", "negro", ("casual", "formal")),
    Prenda("tote_azul", "Tote", "bolso", "azul", ("formal",)),
    Prenda("bufanda_crema", "Bufanda de lana", "cuello", "crema", ("casual",), ("frio",)),
    Prenda("bolso_blanco", "Bolso de hombro", "bolso", "blanco", ("casual", "formal")),
    Prenda("bolso_crema", "Bolso cruzado", "bolso", "crema", ("casual",)),
    Prenda("bolso_crochet", "Bolso de crochet", "bolso", "crema", ("bohemio",)),
    Prenda("gorra_menta", "Gorra", "cabeza", "verde", ("deportivo", "casual"), ("caluroso", "templado")),
    Prenda("bolso_negro", "Bolso estructurado", "bolso", "negro", ("formal",)),
    # ---- cuello ----
    Prenda("collar_dorado", "Collares dorados en capas", "cuello", "dorado", ("bohemio", "formal", "casual")),
    # ---- cabeza ----
    Prenda("gafas_carey", "Gafas redondas de carey", "cabeza", "cafe", ("bohemio", "casual"), ("caluroso", "templado")),
]

PRENDAS = {p.id: p for p in _LISTA_PRENDAS}

_LISTA_LOOKS = [
    Look("cafe_bohemio", "Café bohemio", "Flecos, tonos tierra y botas vaqueras. Muy de festival en la tarde.",
         "cafe", "bohemio", "templado",
         ("blusa_campesina", "pantalon_acampanado_camel", "botas_vaqueras_cafe", "chaqueta_flecos", "bolso_montura_cafe",
          "collar_dorado")),
    Look("rosa_bohemio", "Rosa bohemio", "Satín y falda plisada en el mismo tono: monocromático suave.",
         "rosa", "bohemio", "caluroso",
         ("camisola_satin_rosa", "falda_plisada_rosa", "sandalias_doradas", "bolso_champagne", "collar_dorado")),
    Look("verde_caluroso", "Verde para el calor", "Lino fresco y falda oliva, verdes de la misma familia.",
         "verde", "casual", "caluroso",
         ("camisa_lino_verde", "falda_midi_oliva", "sandalias_planas_camel", "bolso_paja")),
    Look("beige_formal", "Beige formal", "Todo en neutros cálidos, la gabardina le da el toque elegante.",
         "beige", "formal", "templado",
         ("blusa_satin_marfil", "pantalon_sastre_beige", "bailarinas_nude", "gabardina_beige", "tote_beige",
          "gafas_carey")),
    Look("blanco_invierno", "Blanco de invierno", "Texturas tejidas y pana, todo blanco para el frío.",
         "blanco", "casual", "frio",
         ("sueter_cuello_alto_blanco", "pantalon_pana_blanco", "tenis_blancos", "gorro_tejido_blanco")),
    Look("negro_casual", "Negro casual", "El clásico total black con chaqueta de cuero.",
         "negro", "casual", "templado",
         ("camiseta_negra", "jean_negro", "botines_negros", "chaqueta_cuero_negra", "bandolera_negra")),
    Look("azul_formal", "Azul formal", "Traje azul marino con blusa blanca, ideal para una presentación.",
         "azul", "formal", "templado",
         ("blusa_blanca", "pantalon_sastre_azul", "tacones_azules", "blazer_azul", "tote_azul", "collar_dorado")),
    Look("color_cafe", "Café acogedor", "Suéter trenzado y bufanda: café con crema, combinación segura.",
         "cafe", "casual", "frio",
         ("sueter_trenzado_cafe", "pantalon_recto_camel", "botines_cafe", "bufanda_crema", "bolso_montura_cafe")),
    Look("color_rosa", "Rosa con gris", "El rosa como único color y el gris lo equilibra.",
         "rosa", "formal", "templado",
         ("blusa_blanca", "pantalon_sastre_gris", "bailarinas_rosa", "cardigan_rosa", "bolso_blanco",
          "collar_dorado")),
    Look("color_blanco", "Blanco de lino", "Total white fresco para días de sol.",
         "blanco", "casual", "caluroso",
         ("camisa_anudada_blanca", "pantalon_lino_blanco", "sandalias_tacon_nude", "bolso_crema", "collar_dorado")),
    Look("estilo_bohemio", "Bohemio clásico", "Encaje, falda escalonada y gamuza.",
         "beige", "bohemio", "templado",
         ("blusa_encaje_crema", "falda_escalonada_beige", "botines_gamuza_camel", "bolso_crochet", "collar_dorado")),
    Look("estilo_deportivo", "Deportivo verde salvia", "Conjunto deportivo a juego, listo para entrenar.",
         "verde", "deportivo", "caluroso",
         ("esqueleto_salvia", "licra_ciclista_verde", "tenis_running", "gorra_menta")),
    Look("estilo_formal", "Formal en negro", "Abrigo largo y cuello alto, elegante y abrigado.",
         "negro", "formal", "frio",
         ("cuello_alto_negro", "pantalon_sastre_negro", "botines_negros", "abrigo_largo_negro", "bolso_negro")),
    Look("estilo_casual", "Casual de jean", "Doble denim con camiseta blanca, el básico de todos los días.",
         "azul", "casual", "templado",
         ("camiseta_blanca", "jean_mom_azul", "tenis_blancos", "chaqueta_jean", "bolso_crema")),
]

LOOKS = {l.id: l for l in _LISTA_LOOKS}


def prendas_por_categoria() -> dict:
    """Agrupa las prendas por categoría (lo uso para pintar los <select>)."""
    grupos = {c: [] for c in CATEGORIAS}
    for p in _LISTA_PRENDAS:
        grupos[p.categoria].append(p)
    for lista in grupos.values():
        lista.sort(key=lambda p: (p.color, p.nombre))
    return grupos
