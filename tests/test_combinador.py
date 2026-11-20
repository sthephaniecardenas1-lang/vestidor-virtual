"""Pruebas de la lógica de combinación (sin servidor, solo funciones)."""

import pytest

from app.catalogo import LOOKS, PRENDAS
from app.combinador import (
    SeleccionInvalida, evaluar_outfit, look_mas_parecido, relacion_colores,
)


def seleccion_de(look_id):
    """Convierte un look del catálogo en el dict que manda el formulario."""
    return {PRENDAS[p].categoria: p for p in LOOKS[look_id].prendas}


# --- funcionalidad principal ---

def test_look_monocromatico_saca_puntaje_alto():
    ev = evaluar_outfit(seleccion_de("negro_casual"))
    assert ev.puntaje >= 90
    assert ev.etiqueta == "¡Combina increíble!"
    assert ev.avisos == []


@pytest.mark.parametrize("c1, c2, esperado", [
    ("azul", "cafe", "complementarios"),   # el ejemplo clásico azul + café
    ("rosa", "verde", "complementarios"),
    ("cafe", "camel", "análogos"),
    ("negro", "rosa", "neutro"),
    ("azul", "rosa", "atrevido"),
    ("verde", "verde", "monocromático"),
], ids=["azul-cafe", "rosa-verde", "cafe-camel", "negro-rosa", "azul-rosa", "verde-verde"])
def test_relacion_entre_colores(c1, c2, esperado):
    tipo, _ = relacion_colores(c1, c2)
    assert tipo == esperado


def test_estilos_que_chocan_dan_aviso_y_bajan_puntaje():
    bien = evaluar_outfit({"superior": "cuello_alto_negro", "inferior": "pantalon_sastre_negro",
                           "calzado": "botines_negros"})
    mal = evaluar_outfit({"superior": "cuello_alto_negro", "inferior": "pantalon_sastre_negro",
                          "calzado": "tenis_running"})
    assert mal.puntaje < bien.puntaje
    assert any("¿Estás segura?" in a for a in mal.avisos)


def test_muchos_colores_protagonistas_genera_aviso():
    ev = evaluar_outfit({"superior": "camisa_lino_verde", "inferior": "jean_mom_azul",
                         "calzado": "bailarinas_rosa"})
    assert ev.puntaje < 75
    assert any("muchos colores" in a for a in ev.avisos)


def test_el_clima_cambia_el_resultado():
    seleccion = {"superior": "sueter_cuello_alto_blanco", "inferior": "pantalon_pana_blanco",
                 "calzado": "tenis_blancos"}
    frio = evaluar_outfit(seleccion, "frio")
    calor = evaluar_outfit(seleccion, "caluroso")
    assert frio.puntaje > calor.puntaje
    assert any("caluroso" in a for a in calor.avisos)


def test_reconoce_un_look_completo():
    ev = evaluar_outfit(seleccion_de("azul_formal"))
    assert ev.look.id == "azul_formal"
    assert ev.coincidencias == len(LOOKS["azul_formal"].prendas) == 6
    assert ev.look_exacto


def test_avatar_busca_el_look_mas_parecido():
    prendas = [PRENDAS["sueter_trenzado_cafe"], PRENDAS["bufanda_crema"]]
    look, comunes = look_mas_parecido(prendas)
    assert look.id == "color_cafe"
    assert comunes == 2


def test_sugiere_lo_que_falta_y_abrigo_si_hace_frio():
    ev = evaluar_outfit({"superior": "sueter_trenzado_cafe", "inferior": "pantalon_recto_camel"}, "frio")
    assert set(ev.sugerencias) == {"calzado", "abrigo"}
    # lo sugerido tiene que servir para el frío
    assert all("frio" in p.climas for p in ev.sugerencias.values())


# --- casos límite y datos inválidos ---

def test_sin_prendas_no_hay_puntaje_ni_avatar():
    ev = evaluar_outfit({"superior": "", "inferior": ""})
    assert ev.puntaje is None
    assert ev.look is None
    assert "al menos una prenda" in ev.etiqueta


def test_una_sola_prenda_no_se_puede_calificar():
    ev = evaluar_outfit({"superior": "blusa_blanca"})
    assert ev.puntaje is None
    assert set(ev.sugerencias) == {"inferior", "calzado"}


def test_prenda_que_no_existe():
    with pytest.raises(SeleccionInvalida, match="No encontré"):
        evaluar_outfit({"superior": "camiseta_de_unicornio"})


def test_prenda_en_la_categoria_equivocada():
    with pytest.raises(SeleccionInvalida, match="es de calzado"):
        evaluar_outfit({"superior": "tenis_blancos"})


def test_clima_invalido():
    with pytest.raises(SeleccionInvalida):
        evaluar_outfit({"superior": "blusa_blanca"}, "nevando")
