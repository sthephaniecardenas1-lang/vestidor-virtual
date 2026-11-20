"""
Telas reales de las prendas.

Para que la ilustración se vea realista, el color y la textura de cada prenda
salen de MIS fotos: herramientas/preparar_fotos.py toma un pedacito de tela
en el punto indicado aquí (look, (x, y) en la foto de 600 x 885) y guarda:
  - el color real (mediana del pedazo) en app/telas.json
  - la textura (solo luces y sombras) en static/img/telas/<id>.webp

Las prendas que no están aquí (sandalias de tiras, gafas, collares...) son
muy pequeñas en la foto, así que usan el color y la textura dibujados en
prendas_svg.py.
"""

import json
from functools import lru_cache
from pathlib import Path

MUESTRAS = {
    # parte superior
    "blusa_campesina": ("cafe_bohemio", (300, 250)),
    "camisola_satin_rosa": ("rosa_bohemio", (300, 280)),
    "camisa_lino_verde": ("verde_caluroso", (330, 260)),
    "blusa_satin_marfil": ("beige_formal", (300, 270)),
    "sueter_cuello_alto_blanco": ("blanco_invierno", (300, 300)),
    "camiseta_negra": ("negro_casual", (300, 260)),
    "blusa_blanca": ("color_rosa", (300, 260)),
    "sueter_trenzado_cafe": ("color_cafe", (210, 300)),
    "camisa_anudada_blanca": ("color_blanco", (330, 260)),
    "blusa_encaje_crema": ("estilo_bohemio", (330, 250)),
    "esqueleto_salvia": ("estilo_deportivo", (300, 300)),
    "cuello_alto_negro": ("estilo_formal", (300, 230)),
    "camiseta_blanca": ("estilo_casual", (300, 260)),
    # parte inferior
    "pantalon_acampanado_camel": ("cafe_bohemio", (265, 600)),
    "falda_plisada_rosa": ("rosa_bohemio", (300, 600)),
    "falda_midi_oliva": ("verde_caluroso", (310, 600)),
    "pantalon_sastre_beige": ("beige_formal", (222, 760)),
    "pantalon_pana_blanco": ("blanco_invierno", (265, 600)),
    "jean_negro": ("negro_casual", (270, 600)),
    "pantalon_sastre_azul": ("azul_formal", (270, 620)),
    "pantalon_recto_camel": ("color_cafe", (265, 600)),
    "pantalon_sastre_gris": ("color_rosa", (265, 620)),
    "pantalon_lino_blanco": ("color_blanco", (265, 620)),
    "falda_escalonada_beige": ("estilo_bohemio", (300, 620)),
    "licra_ciclista_verde": ("estilo_deportivo", (250, 480)),
    "pantalon_sastre_negro": ("estilo_formal", (215, 760)),
    "jean_mom_azul": ("estilo_casual", (265, 600)),
    # calzado
    "botas_vaqueras_cafe": ("cafe_bohemio", (200, 820)),
    "tenis_blancos": ("blanco_invierno", (195, 845)),
    "botines_negros": ("negro_casual", (205, 830)),
    "botines_cafe": ("color_cafe", (195, 830)),
    "botines_gamuza_camel": ("estilo_bohemio", (195, 820)),
    "tenis_running": ("estilo_deportivo", (200, 840)),
    # abrigos
    "chaqueta_flecos": ("cafe_bohemio", (230, 260)),
    "gabardina_beige": ("beige_formal", (230, 330)),
    "chaqueta_cuero_negra": ("negro_casual", (230, 280)),
    "blazer_azul": ("azul_formal", (225, 300)),
    "cardigan_rosa": ("color_rosa", (350, 320)),
    "abrigo_largo_negro": ("estilo_formal", (380, 450)),
    "chaqueta_jean": ("estilo_casual", (390, 300)),
    # bolsos, cuello y cabeza
    "bolso_montura_cafe": ("cafe_bohemio", (228, 455)),
    "bolso_paja": ("verde_caluroso", (230, 430)),
    "tote_beige": ("beige_formal", (180, 590)),
    "tote_azul": ("azul_formal", (410, 620)),
    "bolso_crochet": ("estilo_bohemio", (225, 460)),
    "bufanda_crema": ("color_cafe", (365, 300)),
    "gorro_tejido_blanco": ("blanco_invierno", (300, 60)),
    "gorra_menta": ("estilo_deportivo", (300, 45)),
}

ARCHIVO = Path(__file__).resolve().parent / "telas.json"


@lru_cache(maxsize=1)
def colores_reales() -> dict:
    if not ARCHIVO.exists():
        return {}
    return json.loads(ARCHIVO.read_text(encoding="utf-8"))


def tiene_tela(prenda_id: str) -> bool:
    return prenda_id in colores_reales()
