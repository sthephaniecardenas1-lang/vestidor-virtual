"""
Cómo se dibuja cada prenda sobre la avatar.

En vez de dibujar 63 prendas a mano, hice "moldes" (como en costura):
  superior -> manga, cuello, silueta, textura, botones...
  inferior -> pantalón (ajustado, recto, mom, acampanado, ancho), falda o licra
  calzado, abrigo, bolso, cuello y cabeza tienen sus propios moldes.

VESTUARIO dice qué molde usa cada prenda del catálogo y con qué parámetros.
Las coordenadas salen del cuerpo de avatar.py con unos píxeles de holgura
para que la piel no se asome por los bordes.
"""

from functools import lru_cache

from app import svg as _svg
from app.ajuste import deformar_svg
from app.catalogo import COLORES, PRENDAS
from app.svg import ajustar, ambos_lados, espejo, forma, linea, reflejar, ruta
from app.telas import colores_reales

# --------------------------------------------------------------- superior --

_CUELLOS = {
    "redondo": [(200, 178), (189, 175), (181, 164, "c")],
    "v":       [(200, 224, "c"), (182, 166, "c")],
    "alto":    [(200, 137, "c"), (186, 136, "c"), (186, 160)],
    "camisa":  [(200, 198, "c"), (185, 165, "c")],
    "recto":   [(200, 184), (188, 180), (181, 168, "c")],
}

_MANGAS = {
    "corta": [(127, 222), (124, 252, "c"), (151, 252, "c"), (154, 226, "c")],
    "tres_cuartos": [(127, 222), (119, 280), (114, 330), (110, 390, "c"),
                     (135, 390, "c"), (140, 330), (147, 270), (154, 226, "c")],
    "larga": [(127, 222), (119, 280), (114, 330), (109, 390), (104, 444, "c"),
              (129, 444, "c"), (133, 390), (140, 330), (147, 270), (154, 226, "c")],
    "abullonada": [(125, 214), (113, 270), (105, 340), (100, 405), (103, 432), (106, 446, "c"),
                   (129, 446, "c"), (131, 432), (136, 382), (141, 322), (148, 268), (154, 226, "c")],
}

_SILUETAS = {
    "entallada": [(152, 254), (155, 290), (162, 322), (159, 342, "c"), (200, 344, "c")],
    "corta":     [(152, 254), (156, 292), (162, 326, "c"), (200, 328, "c")],
    "recta":     [(151, 258), (153, 304), (155, 352, "c"), (200, 355, "c")],
    "amplia":    [(148, 258), (146, 312), (148, 366, "c"), (200, 370, "c")],
}


def _superior(s, c):
    cuello = s.get("cuello", "redondo")
    manga = s.get("manga", "corta")
    silueta = _SILUETAS[s.get("silueta", "entallada")]

    if manga == "tirante":
        mitad = [(200, 214), (186, 207), (174, 200, "c"), (157, 207), (148, 226, "c")]
    elif manga == "ninguna":
        mitad = _CUELLOS[cuello] + [(172, 168, "c"), (160, 192), (149, 224, "c")]
    else:
        mitad = _CUELLOS[cuello] + [(170, 167), (151, 173), (136, 185)] + _MANGAS[manga]
    # en la pose de la modelo el brazo va pegado al torso: ensancho los costados
    # para que no se asome la ropa base entre la manga y el cuerpo
    silueta = [(p[0] - 5, *p[1:]) if p[1] < 345 and p[0] < 200 else p for p in silueta]
    mitad = mitad + silueta
    d = ruta(espejo(mitad))
    oscuro, claro = ajustar(c, .75), ajustar(c, 1.25)
    tex = s.get("textura")
    partes = [forma(d, c, tex)]

    if s.get("brillo"):
        partes.append(f'<path d="{d}" fill="url(#brillo)"/>')
    if manga == "tirante":
        partes.append(ambos_lados([(177, 203), (174, 186), (172, 170)], c, 5))
    if manga in ("larga", "abullonada") and s.get("puno", True):
        partes.append(ambos_lados([(105, 436), (128, 436)], oscuro, 1.2))
    if manga == "abullonada":
        partes.append(ambos_lados([(118, 300), (124, 310), (130, 304)], oscuro, .9, ' opacity=".6"'))
    if cuello == "alto":
        partes.append(linea("M186,147 L214,147 M186,155 L214,155", oscuro, 1))
    if cuello == "camisa":
        solapa = [(199, 196, "c"), (186, 162, "c"), (173, 169, "c"), (182, 192, "c")]
        tono = ajustar(c, .94) if c.lower() > "#e0" else claro
        partes.append(forma(ruta(solapa), tono, sombra=False))
        partes.append(forma(ruta(reflejar(solapa)), tono, sombra=False))
    if s.get("cordon"):
        partes.append(linea("M196,200 L192,226 M204,200 L208,226", oscuro, 1.1))
        partes.append(f'<circle cx="192" cy="228" r="2" fill="{oscuro}"/><circle cx="208" cy="228" r="2" fill="{oscuro}"/>')
    if s.get("botones"):
        y0 = 205 if cuello == "camisa" else 232
        y1 = silueta[-1][1] - 8
        partes.append(linea(f"M200,{y0 - 6} L200,{y1}", oscuro, .8))
        paso = (y1 - y0) / 4
        partes += [f'<circle cx="200" cy="{y0 + i * paso:.0f}" r="2" fill="{claro}" stroke="{oscuro}" stroke-width=".7"/>'
                   for i in range(5)]
    if s.get("ribete"):
        y = silueta[-1][1]
        partes.append(linea(f"M{silueta[-2][0] + 1},{y - 10} L{400 - silueta[-2][0] - 1},{y - 10}", oscuro, 1))
    if s.get("trenzas"):
        for x in (182, 218):
            ondas = " ".join(f"Q{x + 6},{y + 8} {x},{y + 16}" if i % 2 == 0 else f"Q{x - 6},{y + 8} {x},{y + 16}"
                             for i, y in enumerate(range(196, 336, 16)))
            partes.append(f'<path d="M{x},196 {ondas}" fill="none" stroke="{oscuro}" stroke-width="2" opacity=".55"/>')
    if s.get("nudo"):
        partes.append(forma(ruta([(186, 346), (200, 338), (214, 346), (200, 356)]), c))
        partes.append(forma(ruta([(194, 352), (186, 380, "c"), (198, 376, "c")]), c))
        partes.append(forma(ruta([(206, 352), (214, 382, "c"), (202, 377, "c")]), c))
    if s.get("costuras"):
        partes.append(ambos_lados([(176, 200), (184, 270), (186, 330)], oscuro, .9, ' opacity=".6"'))
    return "".join(partes)


# --------------------------------------------------------------- inferior --

_PIERNAS = {
    "ajustado": [(150, 440), (156, 520), (159, 600), (160, 700), (167, 797, "c"), (188, 799, "c"),
                 (185, 700), (185, 600), (190, 520), (196, 462)],
    "recto": [(148, 440), (151, 540), (153, 650), (155, 798, "c"), (193, 800, "c"),
              (191, 650), (191, 540), (195, 470)],
    "mom": [(147, 430), (149, 520), (155, 650), (161, 798, "c"), (191, 800, "c"),
            (189, 650), (190, 530), (195, 470)],
    "acampanado": [(149, 440), (155, 560), (153, 680), (141, 803, "c"), (197, 805, "c"),
                   (189, 690), (188, 600), (192, 520), (196, 466)],
    "ancho": [(146, 430), (140, 560), (134, 700), (129, 804, "c"), (198, 806, "c"),
              (197, 700), (197, 560), (198, 480)],
}

_FALDAS = {
    "plisada": [(152, 350), (144, 450), (135, 600), (126, 772, "c"), (200, 778, "c")],
    "midi": [(150, 345), (141, 450), (135, 560), (130, 652, "c"), (200, 657, "c")],
    "escalonada": [(150, 350), (146, 470, "c"), (140, 472), (136, 620, "c"), (130, 622), (124, 772, "c"), (200, 776, "c")],
}


def _ajustar_pierna(puntos):
    """Pierna más pegada al cuerpo de la modelo: cara interna hacia el centro, externa hacia afuera."""
    salida, interna = [], False
    for p in puntos:
        x, y = p[0], p[1]
        if interna:
            x = min(x + 6, 199)
        else:
            x = x - 3
        salida.append((x, y, *p[2:]))
        if len(p) > 2 and p[2] == "c" and salida and len([q for q in salida if len(q) > 2]) == 2:
            interna = True
    return salida


_PIERNAS = {k: _ajustar_pierna(v) for k, v in _PIERNAS.items()}


def _inferior(s, c):
    tipo = s["tipo"]
    oscuro, claro = ajustar(c, .72), ajustar(c, 1.3)
    tex = s.get("textura")
    partes = []

    if tipo == "licra":
        d = ruta(espejo([(200, 316, "c"), (159, 316, "c"), (146, 360), (144, 410), (151, 514, "c"),
                         (194, 518, "c"), (197, 472), (200, 454, "c")]))
        partes.append(forma(d, c, tex))
        partes.append(ambos_lados([(162, 330), (168, 420), (170, 512)], oscuro, 1, ' opacity=".5"'))
        partes.append(linea("M161,330 L239,330", oscuro, 1))
        return "".join(partes)

    if tipo == "falda":
        corte = s.get("corte", "midi")
        d = ruta(espejo([(200, 310, "c"), (161, 310, "c")] + _FALDAS[corte]))
        partes.append(forma(d, c, tex))
        if s.get("brillo"):
            partes.append(f'<path d="{d}" fill="url(#brillo)"/>')
        partes.append(linea("M161,322 L239,322", oscuro, 1))
        if corte == "plisada":
            for i in range(-6, 7):
                x0, x1 = 200 + i * 6.3, 200 + i * 12.2
                partes.append(linea(f"M{x0:.1f},326 L{x1:.1f},774", oscuro, .8, ' opacity=".45"'))
        elif corte == "midi":
            for i in range(-5, 6):
                partes.append(linea(f"M{200 + i * 7},324 Q{200 + i * 9},380 {200 + i * 11},440", oscuro, .8, ' opacity=".4"'))
        else:  # escalonada
            for y, ancho in ((470, 54), (620, 64)):
                ondas = " ".join(f"Q{200 + x + 4},{y + 6} {200 + x + 8},{y}" for x in range(-ancho, ancho, 8))
                partes.append(f'<path d="M{200 - ancho},{y} {ondas}" fill="none" stroke="{oscuro}" stroke-width="1.1"/>')
        return "".join(partes)

    # pantalones
    corte = s.get("corte", "recto")
    mitad = [(200, 310, "c"), (158, 310, "c"), (145, 360), (142, 400)] + _PIERNAS[corte] + [(200, 456, "c")]
    d = ruta(espejo(mitad))
    partes.append(forma(d, c, tex))
    partes.append(linea("M160,322 L240,322", oscuro, 1))
    if s.get("cinturon"):
        cin = s["cinturon"]
        partes.append(f'<rect x="159" y="311" width="82" height="10" rx="2" fill="{cin}"/>'
                      f'<rect x="193" y="309" width="14" height="14" rx="2" fill="none" stroke="#d9b25b" stroke-width="2"/>')
    if s.get("jean"):
        hilo = "#d8a24a"
        partes.append(linea("M205,324 L205,384 Q205,394 196,396", hilo, .9, ' stroke-dasharray="3 2"'))
        partes.append(ambos_lados([(162, 326), (174, 344), (151, 360)], oscuro, 1))
        partes.append(ambos_lados([(160, 330), (172, 347), (150, 364)], hilo, .8, ' stroke-dasharray="3 2"'))
        partes += [f'<rect x="{x}" y="311" width="3" height="12" fill="{oscuro}"/>' for x in (170, 186, 211, 227)]
        partes.append('<circle cx="200" cy="317" r="2.6" fill="#c9a24a"/>')
    else:
        partes.append(linea("M204,324 L204,382 Q204,390 197,392", oscuro, .9))
    if s.get("raya"):
        partes.append(ambos_lados([(172, 412), (173, 600), (174, 796)], oscuro, .9, ' opacity=".55"'))
    return "".join(partes)


# ---------------------------------------------------------------- calzado --

def _calzado(s, c):
    tipo = s["tipo"]
    oscuro, claro = ajustar(c, .7), ajustar(c, 1.3)
    tex = s.get("textura")
    piezas = []  # (puntos, color, textura) del pie izquierdo; se reflejan

    if tipo == "tenis":
        piezas.append(([(169, 800), (163, 818), (162, 836), (166, 848, "c"), (193, 848, "c"),
                        (194, 826), (190, 804)], c, None))
        piezas.append(([(162, 840, "c"), (166, 852), (182, 856), (194, 850), (194, 840, "c")],
                       "#e3e3e3" if c != "#e3e3e3" else "#cfcfcf", None))
        extra = ambos_lados([(173, 812), (186, 812)], oscuro, 1) + ambos_lados([(172, 820), (187, 820)], oscuro, 1)
    elif tipo == "botin":
        piezas.append(([(166, 752, "c"), (166, 790), (163, 816), (162, 838), (166, 851), (182, 854),
                        (193, 847), (193, 820), (190, 790), (189, 752, "c")], c, tex))
        piezas.append(([(169, 852, "c"), (169, 862, "c"), (179, 862, "c"), (179, 853, "c")], ajustar(c, .55), None))
        extra = ambos_lados([(170, 754), (172, 790)], oscuro, 1.4) if s.get("chelsea") else ""
    elif tipo == "bota":
        piezas.append(([(160, 690, "c"), (162, 740), (165, 790), (162, 820), (161, 840), (167, 852),
                        (178, 860, "c"), (191, 849), (194, 822), (190, 790), (189, 740), (191, 690, "c")], c, tex))
        piezas.append(([(167, 856, "c"), (167, 868, "c"), (177, 868, "c"), (177, 858, "c")], ajustar(c, .5), None))
        extra = (ambos_lados([(166, 700), (175, 730), (184, 700)], claro, 1)
                 + ambos_lados([(166, 718), (175, 752), (184, 718)], claro, 1))
    elif tipo == "tacon":
        piezas.append(([(168, 813, "c"), (164, 830), (167, 846), (178, 861, "c"), (190, 846), (192, 829),
                        (188, 813, "c"), (178, 822)], c, None))
        extra = ambos_lados([(166, 846), (167, 868)], ajustar(c, .55), 2.4)
    elif tipo == "bailarina":
        piezas.append(([(168, 818, "c"), (164, 832), (167, 846), (180, 852), (191, 845), (192, 830),
                        (188, 818, "c"), (178, 824)], c, None))
        extra = ambos_lados([(176, 823), (180, 826), (184, 823)], oscuro, 1.4)
    elif tipo in ("sandalia", "sandalia_tacon"):
        piezas.append(([(163, 838, "c"), (166, 849), (180, 852), (193, 846), (192, 836, "c"), (178, 844)], ajustar(c, .85), None))
        extra = (linea("M166,817 Q178,825 189,815 M211,815 Q222,825 234,817", c, 3)
                 + linea("M164,830 Q178,838 191,829 M209,829 Q222,838 236,830", c, 3))
        if tipo == "sandalia_tacon":
            extra += ambos_lados([(170, 800), (186, 800)], c, 2.4) + ambos_lados([(167, 852), (168, 868)], ajustar(c, .7), 2.6)
    else:
        raise ValueError(f"tipo de calzado desconocido: {tipo}")

    partes = []
    for puntos, color, textura in piezas:
        partes.append(forma(ruta(puntos), color, textura))
        partes.append(forma(ruta(reflejar(puntos)), color, textura))
    if s.get("brillo"):
        partes.append(ambos_lados([(170, 826), (174, 838)], "#fff", 1.6, ' opacity=".5"'))
    return "".join(partes) + extra


# ----------------------------------------------------------------- abrigo --

def _abrigo(s, c):
    largo = s.get("largo", 440)
    borde = s.get("borde", 187)       # dónde termina el frente (200 = cerrado)
    solapa_y = s.get("solapa_y", 290)  # hasta dónde baja el escote
    oscuro, claro = ajustar(c, .72), ajustar(c, 1.25)
    tex = s.get("textura")

    if largo <= 470:
        lado = [(148, 262), (151, 322), (147, 385), (146, largo, "c")]
    else:
        lado = [(148, 262), (151, 322), (147, 400), (141, 520), (136, largo, "c")]

    panel = ([(184, 151, "c"), (172, 162), (150, 171), (133, 184), (124, 222), (116, 280), (111, 330),
              (105, 390), (100, 448, "c"), (131, 448, "c"), (136, 390), (142, 330), (149, 270), (157, 226, "c")]
             + lado + [(borde, largo + 2, "c"), (borde, solapa_y, "c"), (187, 160, "c")])
    izq, der = ruta(panel), ruta(reflejar(panel))
    partes = [forma(der, c, tex), forma(izq, c, tex)]

    estilo = s.get("estilo")
    if estilo in ("blazer", "abrigo", "gabardina", "biker"):
        ancho = {"blazer": 168, "abrigo": 166, "gabardina": 162, "biker": 160}[estilo]
        solapa = [(borde, solapa_y, "c"), (ancho, 212, "c"), (ancho + 6, 200, "c"), (ancho + 12, 202, "c"),
                  (178, 170, "c"), (186, 160, "c")]
        tono = ajustar(c, .88) if estilo != "biker" else ajustar(c, 1.15)
        partes.append(forma(ruta(solapa), tono, sombra=False))
        partes.append(forma(ruta(reflejar(solapa)), tono, sombra=False))
    if estilo == "biker":
        partes.append(linea("M212,206 L222,330", "#c0c0c0", 1.6))
        partes.append(f'<rect x="216" y="322" width="5" height="9" fill="#c0c0c0"/>')
        partes.append(ambos_lados([(150, 400), (183, 404)], oscuro, 3))
    if estilo == "jean":
        partes.append(forma(ruta([(186, 160, "c"), (166, 170, "c"), (172, 196, "c"), (186, 186, "c")]), ajustar(c, .9), sombra=False))
        partes.append(forma(ruta(reflejar([(186, 160, "c"), (166, 170, "c"), (172, 196, "c"), (186, 186, "c")])), ajustar(c, .9), sombra=False))
        partes.append(ambos_lados([(160, 236), (180, 236), (180, 262), (160, 262), (160, 236)], oscuro, 1.1))
        partes.append(ambos_lados([(160, 236), (170, 246), (180, 236)], oscuro, 1))
        partes.append(ambos_lados([(151, 380), (186, 380)], oscuro, 1.4))
        partes += [f'<circle cx="{x}" cy="{y}" r="2.2" fill="#b8b8b8"/>' for x in (183, 217) for y in (210, 260, 310, 360)]
    if estilo == "cardigan":
        partes.append(ambos_lados([(borde - 1, solapa_y), (borde - 1, largo)], oscuro, 1))
        partes.append(ambos_lados([(150, largo - 10), (borde, largo - 10)], oscuro, 1))
        partes += [f'<circle cx="{borde - 4}" cy="{y}" r="2.4" fill="{claro}" stroke="{oscuro}" stroke-width=".7"/>'
                   for y in range(solapa_y + 10, largo - 14, 22)]
    if estilo == "gabardina":
        partes.append(forma(ruta([(148, 330, "c"), (252, 330, "c"), (252, 342, "c"), (148, 342, "c")]), ajustar(c, .92), sombra=False))
        partes += [f'<circle cx="{x}" cy="{y}" r="2.6" fill="{oscuro}"/>' for x in (176, 224) for y in (300, 372, 420)]
        partes.append(ambos_lados([(106, 410), (130, 412)], oscuro, 3))
    if estilo in ("blazer", "abrigo"):
        partes.append(f'<circle cx="{borde - 3}" cy="{solapa_y + 14}" r="3" fill="{oscuro}"/>')
        partes.append(ambos_lados([(156, largo - 70), (178, largo - 70)], oscuro, 1.3))
    if s.get("flecos"):
        for i, (x, y) in enumerate([(124, 230), (119, 262), (116, 294), (113, 326), (110, 358), (107, 390), (104, 420)]):
            partes.append(ambos_lados([(x, y), (x - 9, y + 18)], ajustar(c, .8), 1.3))
            partes.append(ambos_lados([(x + 1, y + 8), (x - 8, y + 26)], ajustar(c, .8), 1.3))
        for x in range(152, 186, 4):
            partes.append(ambos_lados([(x, 236), (x - 2, 262)], ajustar(c, .8), 1.2))
        partes.append(ambos_lados([(150, 234), (186, 236)], oscuro, 1.2))
    return "".join(partes)


# ------------------------------------------------------------------ bolso --

CORREA = "M252,176 Q214,280 166,402"


def _bolso(s, c):
    tipo = s["tipo"]
    oscuro, claro = ajustar(c, .7), ajustar(c, 1.25)
    tex = s.get("textura")
    if tipo == "cruzado":
        forma_b = s.get("forma", "rect")
        partes = [linea(CORREA, s.get("correa", oscuro), 2.6)]
        if forma_b == "montura":
            cuerpo_b = ruta([(138, 402, "c"), (174, 402, "c"), (178, 430), (168, 454), (148, 456), (136, 432)])
            tapa = linea("M138,404 Q156,440 174,404", oscuro, 1.2)
        elif forma_b == "redondo":
            cuerpo_b = ruta([(156, 402), (178, 424), (156, 450), (134, 424)])
            tapa = ""
        elif forma_b == "pequeno":
            cuerpo_b = ruta([(142, 402, "c"), (172, 402, "c"), (172, 430, "c"), (142, 430, "c")])
            tapa = linea("M142,412 L172,412", oscuro, 1)
        else:
            cuerpo_b = ruta([(136, 400, "c"), (178, 400, "c"), (178, 444, "c"), (136, 444, "c")])
            tapa = linea("M136,414 L178,414", oscuro, 1.2) + f'<rect x="153" y="412" width="8" height="6" rx="1" fill="#d9b25b"/>'
        partes += [forma(cuerpo_b, c, tex), tapa]
        if s.get("brillo"):
            partes.append(f'<path d="{cuerpo_b}" fill="url(#brillo)"/>')
        return "".join(partes)

    # tote en la mano derecha (la que queda a la derecha de la pantalla)
    ancho = s.get("ancho", 30)
    cuerpo_b = ruta([(286 - ancho, 492, "c"), (286 + ancho, 492, "c"), (290 + ancho, 566, "c"), (282 - ancho, 566, "c")])
    asas = linea(f"M{274 - ancho / 3:.0f},494 Q286,452 {298 + ancho / 3:.0f},494", s.get("correa", oscuro), 3)
    return asas + forma(cuerpo_b, c, tex) + linea(f"M{286 - ancho},506 L{286 + ancho},506", oscuro, 1)


# ----------------------------------------------------------------- cuello --

def _cuello(s, c):
    tipo = s["tipo"]
    if tipo == "bufanda":
        oscuro = ajustar(c, .8)
        vuelta = ruta([(172, 150), (200, 160), (228, 150), (234, 170), (200, 188), (166, 170)])
        cola1 = ruta([(178, 172, "c"), (200, 182, "c"), (202, 330, "c"), (180, 334, "c")])
        cola2 = ruta([(204, 176, "c"), (226, 168, "c"), (228, 292, "c"), (208, 296, "c")])
        flecos = "".join(linea(f"M{x},{332 + (x % 3)} L{x},{344}", oscuro, 1.2) for x in range(182, 202, 3))
        return (forma(cola2, ajustar(c, .95), "punto") + forma(cola1, c, "punto")
                + forma(vuelta, c, "punto") + flecos)
    if tipo == "collar":
        partes = []
        for i, (dy, r) in enumerate(((198, 2.2), (214, 2.8), (232, 3.2))):
            partes.append(linea(f"M{182 - i * 2},170 Q200,{dy} {218 + i * 2},170", c, 1.1))
            partes.append(f'<circle cx="200" cy="{(170 + dy) / 2 + 1:.0f}" r="{r}" fill="{c}"/>')
        return "".join(partes)
    raise ValueError(tipo)


# ----------------------------------------------------------------- cabeza --

def _cabeza(s, c):
    tipo = s["tipo"]
    oscuro = ajustar(c, .75)
    if tipo == "gorro":
        copa = ruta([(160, 90, "c"), (158, 62), (170, 30), (200, 12), (230, 30), (242, 62), (240, 90, "c")])
        doblez = ruta([(158, 74, "c"), (242, 74, "c"), (243, 96, "c"), (157, 96, "c")])
        return forma(copa, c, "acanalado") + forma(doblez, ajustar(c, .96), "acanalado")
    if tipo == "gorra":
        copa = ruta([(162, 74, "c"), (162, 48), (176, 26), (200, 18), (224, 26), (238, 48), (238, 74, "c")])
        visera = ruta([(158, 74), (200, 68), (242, 74), (234, 84), (200, 88), (166, 84)])
        return (forma(copa, c) + linea("M200,18 L200,72 M182,24 Q176,48 178,72 M218,24 Q224,48 222,72", oscuro, .9)
                + f'<circle cx="200" cy="19" r="3" fill="{oscuro}"/>' + forma(visera, ajustar(c, .9)))
    if tipo == "gafas":
        if s.get("redondas", True):
            lentes = ('<circle cx="185" cy="100" r="11" fill="#7a4a22" fill-opacity=".55"/>'
                      '<circle cx="215" cy="100" r="11" fill="#7a4a22" fill-opacity=".55"/>')
            marco = (f'<circle cx="185" cy="100" r="11" fill="none" stroke="{c}" stroke-width="2.4"/>'
                     f'<circle cx="215" cy="100" r="11" fill="none" stroke="{c}" stroke-width="2.4"/>')
        else:
            lentes = ""
            marco = (f'<rect x="171" y="91" width="26" height="18" rx="7" fill="#1d1d1f" stroke="{c}" stroke-width="2.4"/>'
                     f'<rect x="203" y="91" width="26" height="18" rx="7" fill="#1d1d1f" stroke="{c}" stroke-width="2.4"/>')
        brillo = linea("M175,95 L181,93 M207,95 L213,93", "#fff", 1.4, ' opacity=".55"')
        puente = linea("M196,98 Q200,95 204,98", c, 2)
        return lentes + marco + puente + brillo
    raise ValueError(tipo)


_MOLDES = {
    "superior": _superior, "inferior": _inferior, "calzado": _calzado, "abrigo": _abrigo,
    "bolso": _bolso, "cuello": _cuello, "cabeza": _cabeza,
}

# ------------------------------------------------------------- vestuario --
# "color" solo cuando quiero un tono distinto al de la paleta general
# (por ejemplo, el jean mom es azul medio, no azul marino).

VESTUARIO = {
    # superior
    "blusa_campesina": {"manga": "abullonada", "cuello": "v", "silueta": "recta", "cordon": True, "color": "#f3e7d0"},
    "camisola_satin_rosa": {"manga": "tirante", "silueta": "corta", "brillo": True, "textura": "satin", "color": "#efb6bb"},
    "camisa_lino_verde": {"manga": "tres_cuartos", "cuello": "camisa", "silueta": "recta", "botones": True, "textura": "lino", "color": "#1f8a57"},
    "blusa_satin_marfil": {"manga": "larga", "cuello": "camisa", "silueta": "entallada", "botones": True, "brillo": True, "color": "#f4ead6"},
    "sueter_cuello_alto_blanco": {"manga": "larga", "cuello": "alto", "silueta": "amplia", "textura": "punto", "trenzas": True, "ribete": True, "color": "#f7f3ea"},
    "camiseta_negra": {"manga": "corta", "cuello": "redondo", "silueta": "entallada", "color": "#202022"},
    "blusa_blanca": {"manga": "larga", "cuello": "v", "silueta": "entallada", "color": "#fbfaf6"},
    "sueter_trenzado_cafe": {"manga": "larga", "cuello": "redondo", "silueta": "amplia", "textura": "punto", "trenzas": True, "ribete": True, "color": "#6a3f2a"},
    "camisa_anudada_blanca": {"manga": "corta", "cuello": "camisa", "silueta": "corta", "botones": True, "nudo": True, "textura": "lino", "color": "#fbfaf6"},
    "blusa_encaje_crema": {"manga": "abullonada", "cuello": "v", "silueta": "recta", "textura": "encaje", "color": "#f1e3c8"},
    "esqueleto_salvia": {"manga": "ninguna", "cuello": "recto", "silueta": "recta", "costuras": True, "color": "#8fb79a"},
    "cuello_alto_negro": {"manga": "larga", "cuello": "alto", "silueta": "entallada", "textura": "acanalado", "color": "#1e1e20"},
    "camiseta_blanca": {"manga": "corta", "cuello": "redondo", "silueta": "recta", "color": "#fdfcf9"},
    # inferior
    "pantalon_acampanado_camel": {"tipo": "pantalon", "corte": "acampanado", "textura": "pana", "color": "#a96a3b", "cinturon": "#6a3f2a"},
    "falda_plisada_rosa": {"tipo": "falda", "corte": "plisada", "brillo": True, "color": "#d9a1a8"},
    "falda_midi_oliva": {"tipo": "falda", "corte": "midi", "textura": "lino", "color": "#6c7142"},
    "pantalon_sastre_beige": {"tipo": "pantalon", "corte": "recto", "raya": True, "color": "#d6bf9e"},
    "pantalon_pana_blanco": {"tipo": "pantalon", "corte": "recto", "textura": "pana", "color": "#f4efe4"},
    "jean_negro": {"tipo": "pantalon", "corte": "ajustado", "jean": True, "textura": "denim", "color": "#232326"},
    "pantalon_sastre_azul": {"tipo": "pantalon", "corte": "recto", "raya": True, "color": "#22325a"},
    "pantalon_recto_camel": {"tipo": "pantalon", "corte": "recto", "color": "#b07a45"},
    "pantalon_sastre_gris": {"tipo": "pantalon", "corte": "recto", "raya": True, "color": "#a9a9a7"},
    "pantalon_lino_blanco": {"tipo": "pantalon", "corte": "ancho", "textura": "lino", "color": "#f6f2e8"},
    "falda_escalonada_beige": {"tipo": "falda", "corte": "escalonada", "color": "#d3b48f"},
    "licra_ciclista_verde": {"tipo": "licra", "color": "#8fb79a"},
    "pantalon_sastre_negro": {"tipo": "pantalon", "corte": "recto", "raya": True, "color": "#1f1f22"},
    "jean_mom_azul": {"tipo": "pantalon", "corte": "mom", "jean": True, "textura": "denim", "color": "#41689c"},
    # calzado
    "botas_vaqueras_cafe": {"tipo": "bota", "color": "#7a4a2a"},
    "sandalias_doradas": {"tipo": "sandalia", "color": "#d1ac5c"},
    "sandalias_planas_camel": {"tipo": "sandalia", "color": "#b07a45"},
    "bailarinas_nude": {"tipo": "bailarina", "color": "#e2c3a6"},
    "tenis_blancos": {"tipo": "tenis", "color": "#fbfbf9"},
    "botines_negros": {"tipo": "botin", "brillo": True, "color": "#1d1d1f"},
    "tacones_azules": {"tipo": "tacon", "brillo": True, "color": "#22325a"},
    "botines_cafe": {"tipo": "botin", "chelsea": True, "brillo": True, "color": "#4f2f1e"},
    "bailarinas_rosa": {"tipo": "bailarina", "color": "#efb3b9"},
    "sandalias_tacon_nude": {"tipo": "sandalia_tacon", "color": "#dcbf9f"},
    "botines_gamuza_camel": {"tipo": "botin", "textura": "gamuza", "color": "#b47a45"},
    "tenis_running": {"tipo": "tenis", "color": "#f4f6f7"},
    # abrigo
    "chaqueta_flecos": {"estilo": "flecos", "largo": 430, "borde": 186, "solapa_y": 300, "textura": "gamuza", "flecos": True, "color": "#5a3622"},
    "gabardina_beige": {"estilo": "gabardina", "largo": 650, "borde": 188, "solapa_y": 290, "color": "#d4b48c"},
    "chaqueta_cuero_negra": {"estilo": "biker", "largo": 410, "borde": 184, "solapa_y": 300, "textura": "cuero", "color": "#1f1f22"},
    "blazer_azul": {"estilo": "blazer", "largo": 440, "borde": 195, "solapa_y": 300, "color": "#22325a"},
    "cardigan_rosa": {"estilo": "cardigan", "largo": 410, "borde": 199, "solapa_y": 250, "textura": "punto", "color": "#f2b6bf"},
    "abrigo_largo_negro": {"estilo": "abrigo", "largo": 660, "borde": 189, "solapa_y": 310, "textura": "pano", "color": "#1d1d20"},
    "chaqueta_jean": {"estilo": "jean", "largo": 395, "borde": 186, "solapa_y": 196, "textura": "denim", "color": "#8eaed4"},
    # bolso
    "bolso_montura_cafe": {"tipo": "cruzado", "forma": "montura", "color": "#7b4a2a"},
    "bolso_champagne": {"tipo": "cruzado", "forma": "pequeno", "brillo": True, "correa": "#c9a24a", "color": "#e6cfa6"},
    "bolso_paja": {"tipo": "tote", "ancho": 36, "textura": "paja", "correa": "#7b4a2a", "color": "#d9bd86"},
    "tote_beige": {"tipo": "tote", "ancho": 30, "color": "#d3b48c"},
    "bandolera_negra": {"tipo": "cruzado", "forma": "rect", "color": "#1f1f22"},
    "tote_azul": {"tipo": "tote", "ancho": 32, "color": "#22325a"},
    "bolso_blanco": {"tipo": "cruzado", "forma": "rect", "color": "#f7f5f0"},
    "bolso_crema": {"tipo": "cruzado", "forma": "montura", "color": "#eadcc0"},
    "bolso_crochet": {"tipo": "cruzado", "forma": "redondo", "textura": "crochet", "color": "#efe2c8"},
    "bolso_negro": {"tipo": "cruzado", "forma": "rect", "brillo": True, "color": "#1d1d20"},
    # cuello
    "bufanda_crema": {"tipo": "bufanda", "color": "#f1e6d0"},
    "collar_dorado": {"tipo": "collar", "color": "#d1ab55"},
    # cabeza
    "gorro_tejido_blanco": {"tipo": "gorro", "color": "#f6f2ea"},
    "gorra_menta": {"tipo": "gorra", "color": "#a8d8c2"},
    "gafas_carey": {"tipo": "gafas", "redondas": True, "color": "#6b3d1e"},
}

# Telas con relieve: a estas se les pone encima la textura real sacada de la foto
TEXTURAS_REALES = {"punto", "denim", "pana", "encaje", "paja", "crochet", "gamuza", "lino", "acanalado"}


def _mezclar(a: str, b: str, peso_a: float) -> str:
    ca = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x * peso_a + y * (1 - peso_a)):02x}" for x, y in zip(ca, cb))


def color_de(prenda_id: str) -> str:
    """
    Color de la prenda. Si tengo el color real (sacado de la foto), lo mezclo
    60/40 con el del molde: la foto trae sombras y sola oscurecería la prenda.
    """
    spec = VESTUARIO[prenda_id]
    dibujado = spec.get("color") or COLORES[PRENDAS[prenda_id].color]["hex"]
    real = colores_reales().get(prenda_id)
    return _mezclar(real, dibujado, 0.6) if real else dibujado


def dibujar(prenda_id: str) -> str:
    """SVG de una prenda en el maniquí (sin ajustar al cuerpo de la modelo)."""
    prenda = PRENDAS[prenda_id]
    spec = VESTUARIO[prenda_id]
    usar_tela = prenda_id in colores_reales() and spec.get("textura") in TEXTURAS_REALES
    _svg.TELA_ACTUAL = f"tela-{prenda_id}" if usar_tela else None
    try:
        dibujo = _MOLDES[prenda.categoria](spec, color_de(prenda_id))
    finally:
        _svg.TELA_ACTUAL = None
    if usar_tela:
        dibujo = (f'<defs><pattern id="tela-{prenda_id}" width="22" height="22" patternUnits="userSpaceOnUse">'
                  f'<image href="/static/img/telas/{prenda_id}.webp" width="22" height="22"/></pattern></defs>'
                  + dibujo)
    return dibujo


@lru_cache(maxsize=None)
def dibujar_ajustada(prenda_id: str) -> str:
    """La prenda ya deformada para que calce en el cuerpo de la modelo ilustrada."""
    categoria = PRENDAS[prenda_id].categoria
    return deformar_svg(dibujar(prenda_id), cabeza=categoria == "cabeza",
                        piernas=categoria in ("inferior", "calzado"))
