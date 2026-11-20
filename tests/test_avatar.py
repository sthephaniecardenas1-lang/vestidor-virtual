"""Pruebas de la avatar: cada prenda se dibuja, se ajusta al cuerpo y va en su capa."""

import xml.etree.ElementTree as ET

import pytest

from app.ajuste import PARES, deformar, deformar_svg
from app.avatar import CAPAS, svg_avatar, svg_miniatura
from app.catalogo import LOOKS, PRENDAS
from app.prendas_svg import VESTUARIO, dibujar, dibujar_ajustada
from app.svg import espejo, ruta

NS = {"s": "http://www.w3.org/2000/svg"}


def test_todas_las_prendas_tienen_molde():
    assert set(VESTUARIO) == set(PRENDAS)


@pytest.mark.parametrize("prenda_id", sorted(PRENDAS))
def test_cada_prenda_se_dibuja(prenda_id):
    svg = dibujar(prenda_id)
    assert svg.startswith("<")
    assert any(etiqueta in svg for etiqueta in ("<path", "<circle", "<rect"))
    # ya ajustada al cuerpo de la modelo tiene que seguir siendo XML válido
    ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{dibujar_ajustada(prenda_id)}</svg>')
    ET.fromstring(svg_miniatura(prenda_id).replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1))


def test_avatar_es_svg_valido_con_todo_el_closet():
    raiz = ET.fromstring(svg_avatar(LOOKS["cafe_bohemio"].prendas))
    grupos = raiz.findall(".//s:g[@data-id]", NS)
    assert len(grupos) == len(PRENDAS)
    puestas = [g.get("data-id") for g in grupos if "puesta" in g.get("class")]
    assert sorted(puestas) == sorted(LOOKS["cafe_bohemio"].prendas)


def test_orden_de_las_capas():
    # el abrigo tiene que dibujarse DESPUÉS (encima) de la parte superior, etc.
    raiz = ET.fromstring(svg_avatar([], todas=True))
    orden = [g.get("data-capa") for g in raiz.findall(".//s:g[@data-capa]", NS)]
    esperado = [c for c in CAPAS if c != "manos"]
    assert orden == esperado
    assert orden.index("calzado") < orden.index("inferior") < orden.index("superior") < orden.index("abrigo")


def test_solo_puestas_cuando_todas_es_false():
    raiz = ET.fromstring(svg_avatar(["camiseta_negra", "jean_negro"], todas=False))
    ids = {g.get("data-id") for g in raiz.findall(".//s:g[@data-id]", NS)}
    assert ids == {"camiseta_negra", "jean_negro"}


def test_espejo_es_simetrico():
    puntos = espejo([(200, 0), (150, 50), (200, 100)])
    assert puntos == [(200, 0), (150, 50), (200, 100), (250, 50)]
    assert ruta(puntos).startswith("M200.0,0.0") and ruta(puntos).endswith("Z")


def test_el_ajuste_respeta_los_puntos_marcados():
    # sin holgura, cada punto del maniquí cae exacto en su lugar de la modelo
    for origen, destino in PARES:
        x, y = deformar(*origen, holgura=False)
        assert abs(x - destino[0]) < 0.6 and abs(y - destino[1]) < 0.6


def test_la_ropa_queda_un_poco_por_fuera_del_cuerpo():
    # el hombro izquierdo con holgura queda más a la izquierda que sin holgura
    sin, con = deformar(152, 175, holgura=False), deformar(152, 175)
    assert con[0] < sin[0]


def test_la_modelo_es_simetrica():
    # un punto y su reflejo en el maniquí caen reflejados en la modelo
    izq, der = deformar(160, 600, holgura=False), deformar(240, 600, holgura=False)
    assert abs((izq[0] + der[0]) / 2 - 300) < 0.5 and abs(izq[1] - der[1]) < 0.5


def test_deformar_svg_mueve_rectangulos_y_circulos():
    svg = deformar_svg('<rect x="190" y="300" width="20" height="10" fill="red"/><circle cx="200" cy="300" r="4"/>')
    assert "<rect" not in svg and "<path" in svg  # el rect se vuelve path
    assert 'cy="300"' not in svg                  # el círculo se movió
