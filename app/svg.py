"""
Herramientas pequeñas para dibujar en SVG.

La avatar está pensada en un lienzo de 400 x 920 y es simétrica respecto a
x = 200. Por eso casi todas las formas se definen solo con su MITAD IZQUIERDA y
`espejo()` arma la figura completa. Así, si muevo un hombro, se mueve el otro.

Las curvas se suavizan con Catmull-Rom (pasa por todos los puntos). Si un punto
lleva la marca "c" se vuelve esquina (útil para dobladillos y puños).
"""

CENTRO = 200
TELA_ACTUAL = None  # id del <pattern> con la textura real de la prenda que se está dibujando


def _p(punto):
    x, y = punto[0], punto[1]
    esquina = len(punto) > 2 and punto[2] == "c"
    return x, y, esquina


def ruta(puntos, cerrada=True) -> str:
    """Convierte una lista de puntos en el atributo `d` de un <path> suave."""
    pts = [_p(p) for p in puntos]
    n = len(pts)
    if n < 2:
        return ""

    def vecino(i):
        if cerrada:
            return pts[i % n]
        return pts[max(0, min(n - 1, i))]

    def tangente(i):
        x, y, esquina = vecino(i)
        if esquina:
            return 0.0, 0.0
        x0, y0, _ = vecino(i - 1)
        x1, y1, _ = vecino(i + 1)
        return (x1 - x0) / 6, (y1 - y0) / 6

    d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    tramos = n if cerrada else n - 1
    for i in range(tramos):
        x0, y0, _ = vecino(i)
        x1, y1, _ = vecino(i + 1)
        tx0, ty0 = tangente(i)
        tx1, ty1 = tangente(i + 1)
        d.append(
            f"C{x0 + tx0:.1f},{y0 + ty0:.1f} {x1 - tx1:.1f},{y1 - ty1:.1f} {x1:.1f},{y1:.1f}"
        )
    if cerrada:
        d.append("Z")
    return " ".join(d)


def reflejar(puntos):
    """Refleja puntos respecto al eje vertical x = 200."""
    return [(2 * CENTRO - p[0], *p[1:]) for p in puntos]


def espejo(mitad):
    """
    Recibe la mitad izquierda (de arriba hacia abajo, empezando y terminando
    en el eje si hace falta) y devuelve el contorno completo cerrado.
    """
    derecha = [p for p in reversed(reflejar(mitad)) if abs(p[0] - CENTRO) > 0.01]
    return list(mitad) + derecha


def ajustar(hex_color: str, factor: float) -> str:
    """factor < 1 oscurece, factor > 1 aclara (mezcla con blanco)."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    if factor <= 1:
        r, g, b = (int(c * factor) for c in (r, g, b))
    else:
        t = min(factor - 1, 1)
        r, g, b = (int(c + (255 - c) * t) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def forma(d, color, textura=None, sombra=True, borde=True, extra=""):
    """Un path con relleno + capas opcionales de textura y volumen."""
    trazo = (f' stroke="{ajustar(color, 0.7)}" stroke-opacity=".55" stroke-width="1"'
             ' stroke-linejoin="round"') if borde else ""
    partes = [f'<path d="{d}" fill="{color}"{trazo}{extra}/>']
    if textura and TELA_ACTUAL:
        partes.append(f'<path d="{d}" fill="url(#{TELA_ACTUAL})" style="mix-blend-mode:overlay" opacity=".6"/>')
    elif textura:
        partes.append(f'<path d="{d}" fill="url(#t-{textura})"/>')
    if sombra:
        partes.append(f'<path d="{d}" fill="url(#volumen)"/>')
    return "".join(partes)


def linea(d, color, ancho=1.2, extra=""):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ancho}" '
            f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')


def ambos_lados(puntos, color, ancho=1.2, extra=""):
    """Dibuja una línea abierta y su reflejo (costuras, bolsillos...)."""
    return (linea(ruta(puntos, False), color, ancho, extra)
            + linea(ruta(reflejar(puntos), False), color, ancho, extra))
