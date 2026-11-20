"""
Ajuste de las prendas al cuerpo de la modelo ilustrada.

Los moldes de prendas_svg.py se diseñaron sobre un maniquí sencillo (lienzo de
400 x 920). La modelo es una ilustración (lienzo de 600 x 885) con otras
proporciones. En vez de redibujar 61
prendas, las deformo con un "thin-plate spline" (TPS):

  - Marco puntos que se corresponden en los dos cuerpos (hombro con hombro,
    cintura con cintura, rodilla con rodilla...): PARES.
  - El TPS encuentra la deformación más suave que lleva cada punto del maniquí
    a su lugar en la modelo, y con esa función muevo todas las coordenadas de
    cada prenda.

Lo implementé en Python puro (sin numpy) porque son ~100 puntos: resolver el
sistema una vez al arrancar tarda milisegundos.
"""

import math
import re
from functools import lru_cache

# (maniquí x, y) -> (modelo x, y). Contorno izquierdo de la imagen (de la
# nuca a la mano, sube por el costado y baja por la pierna hasta el pie); el
# derecho es su reflejo, porque la modelo es simétrica respecto a x = 300.
_IZQ = [
    ((200, 132), (300, 140)), ((189, 134), (285, 138)), ((187, 158), (280, 150)),
    ((176, 167), (262, 158)), ((152, 175), (222, 166)), ((139, 186), (206, 182)),
    ((130, 222), (205, 230)), ((122, 280), (204, 290)), ((117, 330), (196, 330)),
    ((112, 390), (186, 390)), ((107, 440), (176, 440)), ((102, 462), (170, 465)),
    ((105, 485), (170, 490)), ((113, 495), (180, 512)), ((121, 489), (195, 505)),
    ((126, 468), (199, 470)), ((125, 440), (193, 440)), ((130, 390), (208, 392)),
    ((137, 330), (234, 330)), ((144, 270), (237, 272)), ((151, 222), (230, 215)),
    ((148, 252), (239, 255)), ((152, 290), (244, 292)), ((162, 322), (248, 320)),
    ((157, 360), (231, 360)), ((147, 395), (214, 400)), ((149, 440), (208, 440)),
    ((155, 515), (215, 515)), ((160, 592), (234, 592)), ((158, 645), (240, 640)),
    ((161, 705), (237, 705)), ((168, 770), (250, 770)), ((171, 800), (257, 800)),
    ((165, 822), (251, 840)), ((167, 840), (242, 867)), ((180, 846), (265, 885)),
    ((190, 838), (290, 870)), ((187, 806), (287, 812)), ((186, 760), (285, 760)),
    ((183, 690), (288, 690)), ((186, 600), (293, 600)), ((191, 520), (294, 520)),
    ((196, 462), (299, 472)),
]
_DER = [((400 - ox, oy), (600 - dx, dy)) for (ox, oy), (dx, dy) in _IZQ if ox != 200]
_DER.append(((200, 448), (300, 465)))
_CENTRO = [
    ((200, 200), (300, 205)), ((200, 260), (300, 262)), ((200, 320), (300, 322)),
    ((200, 390), (300, 400)), ((175, 600), (263, 600)), ((225, 600), (337, 600)),
    ((175, 790), (270, 790)), ((225, 790), (330, 790)),
]
# Cabeza: coordenadas del maniquí YA con la escala 1.12 que tenía la cabeza
_CABEZA = [
    ((200, 15), (300, 12)), ((200, 36), (300, 25)), ((158, 70), (250, 50)),
    ((242, 70), (350, 50)), ((156, 100), (255, 85)), ((244, 100), (345, 85)),
    ((183, 94), (282, 78)), ((217, 94), (318, 78)), ((200, 118), (300, 95)),
    ((200, 144), (300, 128)), ((176, 132), (278, 118)), ((224, 132), (322, 118)),
]
PARES = _IZQ + _DER + _CENTRO + _CABEZA
HOLGURA = 3  # píxeles que la ropa queda por fuera de la piel


def _con_holgura(pares, signo):
    """Empuja cada punto del contorno hacia afuera del cuerpo (normal del contorno)."""
    nuevos = []
    for i, (origen, (x, y)) in enumerate(pares):
        ax, ay = pares[max(i - 1, 0)][1]
        bx, by = pares[min(i + 1, len(pares) - 1)][1]
        tx, ty = bx - ax, by - ay
        largo = math.hypot(tx, ty) or 1
        nx, ny = (-ty / largo, tx / largo) if signo > 0 else (ty / largo, -tx / largo)
        nuevos.append((origen, (x + nx * HOLGURA, y + ny * HOLGURA)))
    return nuevos


PARES_ROPA = _con_holgura(_IZQ, 1) + _con_holgura(_DER, -1) + _CENTRO + _CABEZA

# Para pantalones, faldas y zapatos no uso los puntos de los brazos: las manos
# quedan muy pegadas a la cadera y "jalaban" la tela hacia adentro.
def _es_brazo(origen):
    x, y = origen
    return 260 <= y <= 500 and (x < 141 or x > 259)


PARES_PIERNAS = [par for par in PARES_ROPA if not _es_brazo(par[0])]


def _u(r2: float) -> float:
    return 0.0 if r2 == 0 else r2 * math.log(r2) * 0.5  # r² log r


def _resolver(matriz, vector):
    """Eliminación gaussiana con pivoteo parcial (Ax = b)."""
    n = len(vector)
    a = [fila[:] + [vector[i]] for i, fila in enumerate(matriz)]
    for col in range(n):
        piv = max(range(col, n), key=lambda f: abs(a[f][col]))
        a[col], a[piv] = a[piv], a[col]
        for f in range(col + 1, n):
            factor = a[f][col] / a[col][col]
            if factor:
                for c in range(col, n + 1):
                    a[f][c] -= factor * a[col][c]
    x = [0.0] * n
    for f in range(n - 1, -1, -1):
        x[f] = (a[f][n] - sum(a[f][c] * x[c] for c in range(f + 1, n))) / a[f][f]
    return x


@lru_cache(maxsize=4)
def _modelo_tps(holgura=True, piernas=False):
    pares = PARES_PIERNAS if piernas else (PARES_ROPA if holgura else PARES)
    origen = [p for p, _ in pares]
    n = len(origen)
    k = [[_u((xi - xj) ** 2 + (yi - yj) ** 2) for (xj, yj) in origen] for (xi, yi) in origen]
    for i in range(n):
        k[i][i] += 0.5  # un poquito de "suavizado" para que no haya ondas raras
    matriz = []
    for i, (x, y) in enumerate(origen):
        matriz.append(k[i] + [1.0, x, y])
    matriz.append([1.0] * n + [0.0, 0.0, 0.0])
    matriz.append([x for x, _ in origen] + [0.0, 0.0, 0.0])
    matriz.append([y for _, y in origen] + [0.0, 0.0, 0.0])
    pesos_x = _resolver(matriz, [d[0] for _, d in pares] + [0.0, 0.0, 0.0])
    pesos_y = _resolver(matriz, [d[1] for _, d in pares] + [0.0, 0.0, 0.0])
    return origen, pesos_x, pesos_y


def deformar(x: float, y: float, holgura: bool = True, piernas: bool = False) -> tuple:
    """Lleva un punto del maniquí al cuerpo de la modelo (con o sin holgura de ropa)."""
    origen, wx, wy = _modelo_tps(holgura, piernas)
    n = len(origen)
    nx = wx[n] + wx[n + 1] * x + wx[n + 2] * y
    ny = wy[n] + wy[n + 1] * x + wy[n + 2] * y
    for i, (ox, oy) in enumerate(origen):
        u = _u((x - ox) ** 2 + (y - oy) ** 2)
        nx += wx[i] * u
        ny += wy[i] * u
    return nx, ny


def escalar_cabeza(x: float, y: float) -> tuple:
    """La cabeza del maniquí estaba agrandada 1.12 alrededor del mentón."""
    return 200 + (x - 200) * 1.12, 144 + (y - 144) * 1.12


_PAR = re.compile(r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)")
_CIRCULO = re.compile(r'<(circle|ellipse)([^>]*?)/>')
_RECT = re.compile(r'<rect([^>]*?)/>')
_ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')


def deformar_svg(svg: str, cabeza: bool = False, piernas: bool = False) -> str:
    """Aplica deformar() a todas las coordenadas del SVG de una prenda."""
    def mover(x, y):
        if cabeza:
            x, y = escalar_cabeza(x, y)
        return deformar(x, y, piernas=piernas)

    def par(m):
        x, y = mover(float(m.group(1)), float(m.group(2)))
        return f"{x:.1f},{y:.1f}"

    def circulo(m):
        attrs = dict(_ATTR.findall(m.group(2)))
        cx, cy = float(attrs["cx"]), float(attrs["cy"])
        nx, ny = mover(cx, cy)
        bx, _ = mover(cx + 10, cy)
        escala = abs(bx - nx) / 10
        resto = " ".join(f'{k}="{v}"' for k, v in attrs.items() if k not in ("cx", "cy", "r", "rx", "ry"))
        if m.group(1) == "circle":
            radio = f'r="{float(attrs["r"]) * escala:.1f}"'
        else:
            radio = f'rx="{float(attrs["rx"]) * escala:.1f}" ry="{float(attrs["ry"]) * escala:.1f}"'
        return f'<{m.group(1)} cx="{nx:.1f}" cy="{ny:.1f}" {radio} {resto}/>'

    def rect(m):
        attrs = dict(_ATTR.findall(m.group(1)))
        x, y = float(attrs["x"]), float(attrs["y"])
        w, h = float(attrs["width"]), float(attrs["height"])
        esquinas = [mover(x, y), mover(x + w, y), mover(x + w, y + h), mover(x, y + h)]
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in esquinas) + " Z"
        resto = " ".join(f'{k}="{v}"' for k, v in attrs.items() if k not in ("x", "y", "width", "height", "rx"))
        return f'<path d="{d}" {resto}/>'

    # primero los paths; después círculos y rectángulos (un rect se vuelve path ya movido)
    partes = re.split(r'(d="[^"]*")', svg)
    for i, parte in enumerate(partes):
        if parte.startswith('d="'):
            partes[i] = _PAR.sub(par, parte)
    svg = "".join(partes)
    svg = _CIRCULO.sub(circulo, svg)
    return _RECT.sub(rect, svg)
