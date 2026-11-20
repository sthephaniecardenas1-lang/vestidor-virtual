"""
La avatar: una ilustración de la modelo de frente, con las prendas encima,
por capas.

Capas (de atrás hacia adelante), como uno se viste de verdad:
    modelo (en bikini, que hace de ropa interior) -> calzado -> parte inferior -> parte superior -> abrigo
    -> manos -> cuello -> bolso -> cabeza

El calzado va ANTES que el pantalón para que la bota del pantalón caiga sobre
el zapato, y las manos van después del abrigo para que no queden tapadas por
el pantalón o la falda.

Cada prenda se dibuja con su molde (prendas_svg.py) y se ajusta al cuerpo de
la modelo con ajuste.py.
"""

CAPAS = ["calzado", "inferior", "superior", "abrigo", "manos", "cuello", "bolso", "cabeza"]
ILUSTRACION = "/static/img/modelo/modelo.webp"
MANOS = "/static/img/modelo/manos.webp"

VISTA = "110 0 380 885"

DEFS = """
<defs>
  <!-- volumen de la tela: sombra suave hacia adentro en los bordes + sombra sobre el cuerpo -->
  <filter id="tela" x="-8%" y="-4%" width="116%" height="108%" color-interpolation-filters="sRGB">
    <feGaussianBlur in="SourceAlpha" stdDeviation="3.2" result="difuso"/>
    <feComposite in="SourceAlpha" in2="difuso" operator="arithmetic" k2="1" k3="-1" result="borde"/>
    <feFlood flood-color="#2a1a10" flood-opacity=".38"/>
    <feComposite in2="borde" operator="in" result="sombra_interna"/>
    <feGaussianBlur in="SourceAlpha" stdDeviation="2.2" result="caida"/>
    <feOffset in="caida" dy="2.5" result="caida2"/>
    <feFlood flood-color="#3a2416" flood-opacity=".28"/>
    <feComposite in2="caida2" operator="in" result="sombra_externa"/>
    <feMerge>
      <feMergeNode in="sombra_externa"/>
      <feMergeNode in="SourceGraphic"/>
      <feMergeNode in="sombra_interna"/>
    </feMerge>
  </filter>
  <linearGradient id="volumen" x1="0" x2="1">
    <stop offset="0" stop-color="#000" stop-opacity=".16"/>
    <stop offset=".22" stop-color="#000" stop-opacity="0"/>
    <stop offset=".72" stop-color="#fff" stop-opacity=".06"/>
    <stop offset="1" stop-color="#000" stop-opacity=".14"/>
  </linearGradient>
  <linearGradient id="brillo" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".45" stop-color="#fff" stop-opacity=".32"/>
    <stop offset=".55" stop-color="#fff" stop-opacity=".05"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="rubor"><stop offset="0" stop-color="#ef8f86" stop-opacity=".5"/><stop offset="1" stop-color="#ef8f86" stop-opacity="0"/></radialGradient>
  <pattern id="t-denim" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
    <rect width="4" height="4" fill="none"/><line x1="0" y1="0" x2="0" y2="4" stroke="#fff" stroke-opacity=".10" stroke-width="1.4"/>
  </pattern>
  <pattern id="t-punto" width="7" height="6" patternUnits="userSpaceOnUse">
    <path d="M0,0 L3.5,4 L7,0" fill="none" stroke="#000" stroke-opacity=".10" stroke-width="1"/>
  </pattern>
  <pattern id="t-acanalado" width="4" height="10" patternUnits="userSpaceOnUse">
    <line x1="2" y1="0" x2="2" y2="10" stroke="#000" stroke-opacity=".12" stroke-width="1"/>
  </pattern>
  <pattern id="t-pana" width="5" height="10" patternUnits="userSpaceOnUse">
    <line x1="2.5" y1="0" x2="2.5" y2="10" stroke="#000" stroke-opacity=".08" stroke-width="2"/>
  </pattern>
  <pattern id="t-lino" width="6" height="6" patternUnits="userSpaceOnUse">
    <line x1="0" y1="3" x2="6" y2="3" stroke="#000" stroke-opacity=".05" stroke-width="1"/>
    <line x1="3" y1="0" x2="3" y2="6" stroke="#fff" stroke-opacity=".07" stroke-width="1"/>
  </pattern>
  <pattern id="t-encaje" width="10" height="10" patternUnits="userSpaceOnUse">
    <circle cx="5" cy="5" r="2.6" fill="none" stroke="#000" stroke-opacity=".12" stroke-width=".8"/>
    <circle cx="0" cy="0" r="1.1" fill="#000" fill-opacity=".10"/><circle cx="10" cy="10" r="1.1" fill="#000" fill-opacity=".10"/>
  </pattern>
  <pattern id="t-paja" width="8" height="8" patternUnits="userSpaceOnUse">
    <path d="M0,4 L4,0 M4,8 L8,4 M0,4 L4,8 M4,0 L8,4" stroke="#7a5a2e" stroke-opacity=".35" stroke-width="1.2"/>
  </pattern>
  <pattern id="t-crochet" width="9" height="9" patternUnits="userSpaceOnUse">
    <circle cx="4.5" cy="4.5" r="3" fill="none" stroke="#8a7350" stroke-opacity=".4" stroke-width="1.1"/>
  </pattern>
  <pattern id="t-cuero" width="20" height="20" patternUnits="userSpaceOnUse">
    <path d="M0,20 Q10,8 20,0" fill="none" stroke="#fff" stroke-opacity=".06" stroke-width="3"/>
  </pattern>
  <pattern id="t-gamuza" width="3" height="3" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r=".6" fill="#000" fill-opacity=".10"/>
  </pattern>
  <pattern id="t-satin" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="rotate(-20)">
    <rect width="14" height="40" fill="#fff" fill-opacity=".10"/>
  </pattern>
  <pattern id="t-pano" width="3" height="3" patternUnits="userSpaceOnUse">
    <rect width="1" height="1" fill="#fff" fill-opacity=".05"/>
  </pattern>
</defs>
"""


def svg_avatar(puestas, todas=True) -> str:
    """
    Arma la avatar completa.

    puestas -> ids de las prendas que lleva puestas.
    todas   -> True: incluye TODO el clóset y solo muestra las puestas (así el
               JavaScript cambia de ropa al instante, sin pedirle nada al
               servidor). False: incluye únicamente las puestas.
    """
    from app.catalogo import PRENDAS
    from app.prendas_svg import dibujar_ajustada

    puestas = list(puestas)
    capas = {c: [] for c in CAPAS}
    for prenda_id in (PRENDAS if todas else puestas):
        prenda = PRENDAS[prenda_id]
        clase = "prenda puesta" if prenda_id in puestas else "prenda"
        capas[prenda.categoria].append(
            f'<g id="g-{prenda_id}" class="{clase}" data-id="{prenda_id}" '
            f'data-categoria="{prenda.categoria}" filter="url(#tela)">{dibujar_ajustada(prenda_id)}</g>'
        )

    contenido = [f'<image class="modelo-base" href="{ILUSTRACION}" x="0" y="0" width="600" height="885"/>']
    for capa in CAPAS:
        if capa == "manos":
            contenido.append(f'<image class="manos" href="{MANOS}" x="0" y="0" width="600" height="885"/>')
        else:
            contenido.append(f'<g class="capa" data-capa="{capa}">{"".join(capas[capa])}</g>')

    return (
        f'<svg class="avatar-svg" xmlns="http://www.w3.org/2000/svg" viewBox="{VISTA}" '
        'role="img" aria-label="Avatar con el outfit elegido">'
        f'{DEFS}<g class="respira">{"".join(contenido)}</g></svg>'
    )


# Recorte de la miniatura de cada prenda en el clóset (viewBox sobre el cuerpo)
_VISTAS = {
    "superior": "188 128 224 300",
    "inferior": "185 370 230 500",
    "abrigo": "178 128 244 600",
    "calzado": "232 760 136 130",
    "bolso": "150 150 330 520",
    "cuello": "235 130 130 230",
    "cabeza": "232 -12 136 136",
}


def svg_miniatura(prenda_id: str) -> str:
    """La misma prenda que se pone la modelo, sola, para la tarjeta del clóset."""
    from app.catalogo import PRENDAS
    from app.prendas_svg import dibujar_ajustada

    vista = _VISTAS[PRENDAS[prenda_id].categoria]
    return (f'<svg viewBox="{vista}" aria-hidden="true" preserveAspectRatio="xMidYMid meet">'
            f'<g filter="url(#tela)">{dibujar_ajustada(prenda_id)}</g></svg>')
