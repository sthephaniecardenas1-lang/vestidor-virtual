"""Botón Sorpréndeme: outfits al azar que siempre combinan."""

import pytest

from app.combinador import SeleccionInvalida, puntuar
from app.sorpresa import sorprender


# --- sorpréndeme ---

@pytest.mark.parametrize("semilla", range(8))
def test_sorpresa_siempre_combina(semilla):
    prendas, puntaje = sorprender(semilla=semilla)
    categorias = [p.categoria for p in prendas]
    assert {"superior", "inferior", "calzado"} <= set(categorias)
    assert len(categorias) == len(set(categorias))  # una prenda por categoría
    assert puntaje == puntuar(prendas)[0] >= 80


def test_sorpresa_respeta_el_clima():
    prendas, _ = sorprender(clima="caluroso", semilla=1)
    assert all("caluroso" in p.climas for p in prendas)


def test_sorpresa_es_repetible_con_semilla():
    assert sorprender(semilla=42) == sorprender(semilla=42)


def test_sorpresa_estilo_invalido():
    with pytest.raises(SeleccionInvalida):
        sorprender(estilo="gotico")
