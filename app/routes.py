"""
Rutas de la aplicación.

Las rutas solo reciben datos, llaman a la lógica (combinador, recomendador,
sorpresa, avatar) y le pasan el resultado a Jinja2 o lo devuelven en JSON.
Nada de reglas de moda aquí.
"""

from pathlib import Path
from typing import Literal
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.avatar import svg_avatar, svg_miniatura
from app.catalogo import (
    CATEGORIAS, CLIMAS, COLORES, ESTILOS, LOOKS, NOMBRE_CLIMA, PRENDAS,
    nombre_color, prendas_por_categoria,
)
from app.combinador import SeleccionInvalida, evaluar_outfit
from app.recomendador import recomendar
from app.sorpresa import sorprender

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")
router = APIRouter()


def url_probador(seleccion: dict, clima: str | None = None, **cambios) -> str:
    """URL del probador con la selección actual + cambios (None = quitar)."""
    params = {k: v for k, v in {**seleccion, **cambios}.items() if v}
    if clima:
        params["clima"] = clima
    params["enviado"] = "1"
    return "/probador?" + urlencode(params)


def url_alternar(seleccion: dict, clima: str | None, categoria: str, prenda_id: str) -> str:
    """Si la prenda ya está puesta la quita; si no, la pone (enlace sin JavaScript)."""
    nueva = None if seleccion.get(categoria) == prenda_id else prenda_id
    return url_probador(seleccion, clima, **{categoria: nueva})


templates.env.globals.update(
    CATEGORIAS=CATEGORIAS, CLIMAS=CLIMAS, NOMBRE_CLIMA=NOMBRE_CLIMA, COLORES=COLORES,
    ESTILOS=ESTILOS, nombre_color=nombre_color, url_probador=url_probador,
    url_alternar=url_alternar, miniatura=svg_miniatura,
)


@router.get("/")
def inicio(request: Request):
    looks = [LOOKS[i] for i in ("rosa_bohemio", "azul_formal", "color_cafe", "estilo_casual")]
    return templates.TemplateResponse(request, "index.html", {
        "avatar": svg_avatar(LOOKS["verde_caluroso"].prendas, todas=False),
        "looks": [(look, svg_avatar(look.prendas, todas=False)) for look in looks],
    })


# ------------------------------------------------------------ probador --

def leer_seleccion(
    superior: str = "", inferior: str = "", abrigo: str = "", calzado: str = "",
    bolso: str = "", cuello: str = "", cabeza: str = "", clima: str = "", enviado: str = "",
) -> dict:
    return {
        "seleccion": {"superior": superior, "inferior": inferior, "abrigo": abrigo, "calzado": calzado,
                      "bolso": bolso, "cuello": cuello, "cabeza": cabeza},
        "clima": clima,
        "enviado": bool(enviado),
    }


def contexto_panel(datos: dict) -> tuple:
    """Evalúa el outfit y arma todo lo que necesita el panel. Devuelve (contexto, status)."""
    seleccion, clima = datos["seleccion"], datos["clima"]
    contexto = {**datos, "evaluacion": None, "error": None}
    try:
        ev = evaluar_outfit(seleccion, clima)
    except SeleccionInvalida as e:
        contexto["error"] = str(e)
        return contexto, 400

    contexto["evaluacion"] = ev
    return contexto, 200


@router.get("/probador")
def probador(request: Request, datos: dict = Depends(leer_seleccion)):
    contexto, status = contexto_panel(datos)
    ev = contexto["evaluacion"]
    puestas = [p.id for p in ev.prendas] if ev else []
    contexto.update({
        "grupos": prendas_por_categoria(),
        "avatar": svg_avatar(puestas),
    })
    return templates.TemplateResponse(request, "probador.html", contexto, status_code=status)


@router.get("/probador/panel")
def probador_panel(request: Request, datos: dict = Depends(leer_seleccion)):
    """Solo el panel de resultados. El JavaScript lo pide cada vez que cambias de ropa."""
    contexto, status = contexto_panel(datos)
    return templates.TemplateResponse(request, "_panel.html", contexto, status_code=status)


# --------------------------------------------------------- recomendador --

@router.get("/recomendar")
def recomendar_form(request: Request):
    return templates.TemplateResponse(
        request, "recomendar.html", {"filtros": {}, "resultados": None, "error": None}
    )


@router.post("/recomendar")
def recomendar_resultado(
    request: Request,
    color: str = Form(""), estilo: str = Form(""), clima: str = Form(""),
):
    filtros = {"color": color, "estilo": estilo, "clima": clima}
    try:
        resultados = recomendar(color, estilo, clima)
    except SeleccionInvalida as e:
        return templates.TemplateResponse(
            request, "recomendar.html",
            {"filtros": filtros, "resultados": None, "error": str(e)},
            status_code=400,
        )
    for r in resultados:
        r.avatar = svg_avatar(r.look.prendas, todas=False)
    return templates.TemplateResponse(
        request, "recomendar.html", {"filtros": filtros, "resultados": resultados, "error": None}
    )


# ------------------------------------------------------------------ API --

class OutfitIn(BaseModel):
    prendas: dict[str, str]
    clima: Literal["frio", "templado", "caluroso"] | None = None


def _evaluar_o_400(datos: OutfitIn):
    try:
        return evaluar_outfit(datos.prendas, datos.clima)
    except SeleccionInvalida as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/prendas")
def api_prendas():
    return [
        {"id": p.id, "nombre": p.nombre, "categoria": p.categoria,
         "color": p.color, "estilos": list(p.estilos), "climas": list(p.climas)}
        for p in PRENDAS.values()
    ]


@router.post("/api/evaluar")
def api_evaluar(datos: OutfitIn):
    ev = _evaluar_o_400(datos)
    return {
        "puntaje": ev.puntaje,
        "etiqueta": ev.etiqueta,
        "avisos": ev.avisos,
        "detalles_color": ev.detalles_color,
        "sugerencias": {c: p.id for c, p in ev.sugerencias.items()},
        "look_parecido": ev.look.id if ev.look else None,
    }


@router.get("/api/sorpresa")
def api_sorpresa(estilo: str = "", clima: str = "", semilla: int | None = None):
    try:
        prendas, puntaje = sorprender(estilo, clima, semilla)
    except SeleccionInvalida as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"seleccion": {p.categoria: p.id for p in prendas}, "puntaje": puntaje}
