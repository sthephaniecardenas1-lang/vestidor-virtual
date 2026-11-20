"""
Herramienta que usé UNA vez para sacar las telas reales de las prendas.
La app NO la necesita para funcionar (el resultado ya viene en
app/telas.json y app/static/img/telas).

Qué hace:
  1. Toma mis fotos de referencia de outfits (herramientas/originales), recorta
     la mitad donde está el look y le quita el fondo con rembg.
  2. De cada prenda toma un pedacito de tela (el punto está en app/telas.py) y
     guarda su color real (mediana) y su textura (solo luces y sombras).

Uso (opcional):
    pip install -r requirements-dev.txt
    python herramientas/preparar_fotos.py
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.telas import MUESTRAS  # noqa: E402

ORIGINALES = RAIZ / "herramientas" / "originales"
SALIDA_TELAS = RAIZ / "app" / "static" / "img" / "telas"
ARCHIVO_COLORES = RAIZ / "app" / "telas.json"
CAJA_DESPUES = (1490, 140, 2370, 1438)
ANCHO = 600


def sacar_tela(foto, punto, lado=36):
    """Color real (mediana) + textura (solo luces y sombras, sin color) de un pedazo de tela."""
    x, y = punto
    rgba = np.array(foto.convert("RGBA")).astype(np.float32)
    parche = rgba[y - lado // 2:y + lado // 2, x - lado // 2:x + lado // 2]
    visible = parche[parche[:, :, 3] > 200][:, :3]
    color = np.median(visible, axis=0) if len(visible) else np.array([128, 128, 128])

    gris = cv2.cvtColor(parche[:, :, :3].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    detalle = gris - cv2.GaussianBlur(gris, (0, 0), 2.5)      # solo el tejido, no las costuras
    detalle = np.clip(128 + np.clip(detalle * 1.8, -40, 40), 0, 255).astype(np.uint8)
    # mosaico en espejo para que no se noten las uniones al repetirse
    mosaico = np.block([[detalle, detalle[:, ::-1]], [detalle[::-1, :], detalle[::-1, ::-1]]])
    return "#%02x%02x%02x" % tuple(int(c) for c in color), Image.fromarray(mosaico)


def main():
    from rembg import new_session, remove

    sesion = new_session("isnet-general-use")
    SALIDA_TELAS.mkdir(parents=True, exist_ok=True)
    fotos = {}
    for original in sorted(ORIGINALES.glob("*.jpg")):
        imagen = Image.open(original).convert("RGB").crop(CAJA_DESPUES)
        sin_fondo = remove(imagen, session=sesion)
        alto = round(sin_fondo.height * ANCHO / sin_fondo.width)
        fotos[original.stem] = sin_fondo.resize((ANCHO, alto), Image.LANCZOS)

    colores = {}
    for prenda_id, (look_id, punto) in MUESTRAS.items():
        color, textura = sacar_tela(fotos[look_id], punto)
        colores[prenda_id] = color
        textura.save(SALIDA_TELAS / f"{prenda_id}.webp", "WEBP", quality=85)
    ARCHIVO_COLORES.write_text(json.dumps(colores, indent=1, sort_keys=True), encoding="utf-8")
    print("telas:", len(colores))


if __name__ == "__main__":
    main()
