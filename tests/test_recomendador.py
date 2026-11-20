"""Pruebas del recomendador de looks."""

import pytest

from app.catalogo import LOOKS
from app.combinador import SeleccionInvalida
from app.recomendador import armonia_look, recomendar


def test_recomienda_el_look_exacto_primero():
    resultados = recomendar(color="rosa", estilo="bohemio")
    assert resultados[0].look.id == "rosa_bohemio"
    assert resultados[0].afinidad == 100


def test_devuelve_maximo_tres_y_ordenados():
    resultados = recomendar(clima="frio")
    assert len(resultados) == 3
    afinidades = [r.afinidad for r in resultados]
    assert afinidades == sorted(afinidades, reverse=True)


def test_todos_los_looks_del_catalogo_combinan_bien():
    # si alguno sale bajo, o el look está mal armado o las reglas están mal
    for look in LOOKS.values():
        assert armonia_look(look) >= 90, look.id


def test_sin_filtros_es_un_error():
    with pytest.raises(SeleccionInvalida, match="al menos un filtro"):
        recomendar()


@pytest.mark.parametrize("filtros", [
    {"color": "morado"},
    {"estilo": "gotico"},
    {"clima": "tropical"},
])
def test_filtros_invalidos(filtros):
    with pytest.raises(SeleccionInvalida):
        recomendar(**filtros)
