"""Pruebas de las rutas con el TestClient de FastAPI."""

import pytest
from fastapi.testclient import TestClient

from app.catalogo import PRENDAS
from app.main import app

AZUL_FORMAL = {
    "superior": "blusa_blanca", "inferior": "pantalon_sastre_azul", "calzado": "tacones_azules",
    "abrigo": "blazer_azul", "bolso": "tote_azul", "cuello": "collar_dorado", "enviado": "1",
}


@pytest.fixture
def cliente():
    return TestClient(app)


def test_inicio_responde(cliente):
    r = cliente.get("/")
    assert r.status_code == 200
    assert "Vestidor" in r.text
    assert "<svg" in r.text  # la avatar del inicio


def test_probador_vacio_muestra_la_modelo_en_ropa_base(cliente):
    r = cliente.get("/probador")
    assert r.status_code == 200
    assert "img/modelo/modelo.webp" in r.text
    assert 'class="prenda puesta"' not in r.text  # nada puesto
    assert r.text.count('class="tarjeta-prenda') == len(PRENDAS)  # todo el clóset


def test_probador_viste_a_la_avatar(cliente):
    r = cliente.get("/probador", params=AZUL_FORMAL)
    assert r.status_code == 200
    for prenda_id in ("blusa_blanca", "blazer_azul", "tacones_azules"):
        assert f'id="g-{prenda_id}" class="prenda puesta"' in r.text
    assert 'data-look="Azul formal"' in r.text        # reconoce el look completo


def test_panel_parcial(cliente):
    r = cliente.get("/probador/panel", params={"superior": "camiseta_blanca", "inferior": "jean_mom_azul"})
    assert r.status_code == 200
    assert 'class="panel-interno"' in r.text
    assert "<html" not in r.text  # es solo un pedazo de HTML


def test_probador_con_prenda_inventada_responde_400(cliente):
    r = cliente.get("/probador", params={"superior": "no_existe", "enviado": "1"})
    assert r.status_code == 400
    assert "No encontré la prenda" in r.text


def test_formulario_recomendar(cliente):
    r = cliente.post("/recomendar", data={"color": "verde", "estilo": "deportivo", "clima": ""})
    assert r.status_code == 200
    assert "Deportivo verde salvia" in r.text


def test_recomendar_sin_filtros_responde_400(cliente):
    r = cliente.post("/recomendar", data={"color": "", "estilo": "", "clima": ""})
    assert r.status_code == 400
    assert "al menos un filtro" in r.text


def test_api_evaluar(cliente):
    r = cliente.post("/api/evaluar", json={
        "prendas": {"superior": "camiseta_blanca", "inferior": "jean_mom_azul", "calzado": "tenis_blancos"},
        "clima": "templado",
    })
    assert r.status_code == 200
    datos = r.json()
    assert isinstance(datos["puntaje"], int) and 0 <= datos["puntaje"] <= 100
    assert datos["look_parecido"] == "estilo_casual"


def test_api_rechaza_clima_invalido(cliente):
    # aquí valida Pydantic antes de llegar a mi lógica -> 422
    r = cliente.post("/api/evaluar", json={"prendas": {}, "clima": "nevando"})
    assert r.status_code == 422


def test_api_sorpresa(cliente):
    r = cliente.get("/api/sorpresa", params={"estilo": "formal", "clima": "frio", "semilla": 7})
    assert r.status_code == 200
    datos = r.json()
    assert {"superior", "inferior", "calzado"} <= set(datos["seleccion"])
    assert datos["puntaje"] >= 80


def test_cada_tarjeta_del_closet_trae_su_dibujo(cliente):
    r = cliente.get("/probador")
    assert r.text.count('class="mini-prenda"><svg') == len(PRENDAS)
