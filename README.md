# Vestidor Virtual 👗

Un probador virtual que se juega como un juego de vestir. La modelo está de pie sobre una plataforma de estudio. Tocas una prenda del clóset y se la pone al instante, en su capa correcta. Mientras armas el outfit, la app te dice qué tan bien combina (de 0 a 100) y por qué, te avisa si algo choca y te sugiere qué le falta.

Hecho con **FastAPI**, **Jinja2** y **pytest**.

![Demo del probador](evidencias/demo.gif)

> La app está pensada para usarse en el computador, en el navegador, con el servidor local de Uvicorn (`http://127.0.0.1:8000`).

---

## 1. Presentación del proyecto

**Nombre:** Vestidor Virtual

**¿Por qué este proyecto?**
Casi todas las mañanas me pasa lo mismo: tengo una prenda que quiero ponerme y termino probándome tres cosas para ver con qué combina. Los colores son lo que más me cuesta. Sé que el azul con café se ve bien, pero no sabía *por qué*. Quise convertir eso en reglas que un programa entienda… y que además fuera divertido de usar, como esos juegos de vestir muñecas.

Antes de empezar revisé qué tienen las apps de estilismo que hay hoy en el mercado. Casi todas coinciden en tres cosas: un clóset digital, ver la ropa puesta sobre un cuerpo (no en una cuadrícula de productos) y tener en cuenta el clima. Mi app tiene las tres, en formato de juego didáctico.

**Problema que resuelve:**
Puedes probar combinaciones sin sacar la ropa del clóset y entender con teoría del color básica por qué funcionan (o no).

**Funcionalidad principal:**

1. **Probador tipo juego**
   - Una modelo ilustrada, esbelta y de proporciones realistas, sobre una plataforma de estudio.
   - Un clóset de **61 prendas** en 7 categorías: arriba, abajo, abrigo, zapatos, bolso, cuello y cabeza. Cada tarjeta muestra la misma prenda que se pone la modelo.
   - Al tocar una prenda, la modelo se la pone al instante con una animación. Si pasas el mouse por encima, ves una vista previa transparente.
   - Puntaje animado de 0 a 100, explicación de cada par de colores, avisos ("¿Estás segura? Pantalón sastre y tenis de running no se llevan muy bien") y sugerencias con botón **Ponérmelo**.
   - **⟳ Animar**: la modelo gira suavemente sobre la plataforma.
   - **🎲 Sorpréndeme**: arma un outfit al azar que sí combine.
   - Deshacer (también con Ctrl+Z), quitar todo, destellos y confeti cuando el outfit llega a 90 o más.
2. **Recomiéndame:** eliges color, estilo y/o clima y te muestra los 3 looks más afines.

---

## 2. Tecnologías utilizadas

| Tecnología | ¿Para qué la usé? | ¿Por qué? |
|---|---|---|
| **Python 3.10+** | Todo el proyecto | Es el lenguaje del curso. |
| **FastAPI** | Rutas web, panel parcial, SVG de la avatar y API JSON | Valida datos (Pydantic), trae `Depends`, `TestClient` y `GZipMiddleware`. |
| **Jinja2** | Plantillas HTML | Herencia, `include`, macros y variables globales. |
| **SVG** (generado con Python) | Las prendas sobre la modelo | Es texto, así que Python lo genera y pytest lo revisa. |
| **JavaScript** (sin librerías) | Vestir al instante, animaciones, deshacer | Para que se sienta como un juego sin recargar la página. |
| **Uvicorn** · **python-multipart** | Servidor y formularios | Lo que pide FastAPI. |
| **pytest** + **httpx2** | Pruebas | `httpx2` lo usa `TestClient` por dentro. |
| **OpenCV**, **Pillow**, **rembg** *(solo herramienta)* | Sacar el color y la textura real de las telas | Se usan una sola vez con `herramientas/preparar_fotos.py`; la app no los necesita para funcionar. |

---

## 3. Arquitectura y organización

```
vestidor-virtual/
├── app/
│   ├── main.py            # crea la app, GZip y /static
│   ├── routes.py          # TODAS las rutas
│   ├── catalogo.py        # colores, 61 prendas y 14 looks
│   ├── combinador.py      # lógica principal: puntaje, avisos, sugerencias
│   ├── recomendador.py    # "Recomiéndame"
│   ├── sorpresa.py        # "Sorpréndeme"
│   ├── avatar.py          # arma la modelo por capas
│   ├── prendas_svg.py     # "moldes" de cada tipo de prenda
│   ├── ajuste.py          # ajusta cada prenda al cuerpo de la modelo (thin-plate spline)
│   ├── svg.py             # utilidades de dibujo (curvas, espejo, colores)
│   ├── telas.py · telas.json   # color real de cada tela
│   ├── templates/         # base, index, probador, _panel, _macros, recomendar
│   └── static/
│       ├── css/ · js/     # estilos y probador.js
│       └── img/           # modelo/ (modelo y capa de manos), telas/
├── herramientas/
│   ├── preparar_fotos.py  # saca el color y la textura de las telas
│   ├── modelo_referencia.png  # referencia de la modelo (vista de frente)
│   └── originales/        # fotos de referencia de outfits
├── tests/                 # 5 archivos, 117 pruebas
├── evidencias/
├── requirements.txt · requirements-dev.txt · pytest.ini
└── README.md
```

- **Rutas:** en `routes.py`. **Lógica:** en `combinador.py`, `recomendador.py` y `sorpresa.py`. **Dibujo:** en `avatar.py`, `prendas_svg.py`, `ajuste.py` y `svg.py`. Las rutas no tienen ni una regla de moda.
- **Jinja2:** el panel de resultados (`_panel.html`) se usa dentro del probador con `{% include %}` y también solo, en `/probador/panel`, que es lo que pide el JavaScript cada vez que cambias de ropa. Así el HTML del panel está en un solo lugar.

### Cómo armé a la modelo (la parte que más trabajo me dio)

1. **La modelo.** Usé como referencia una hoja de personaje de cuerpo entero (vista de frente). Le quité el fondo y la centré en un lienzo de 600 × 885. El bikini hace de ropa interior: si una prenda deja ver un costado, se ve natural.
2. **Las manos en su capa.** Separé las manos en otra imagen para dibujarlas *encima* del pantalón y de la falda, como cuando uno deja caer los brazos.
3. **Moldes de prendas.** No dibujé 61 prendas a mano. Hice moldes con parámetros, como en costura: una parte superior es `manga` + `cuello` + `silueta` + textura; el blazer azul es `{"estilo": "blazer", "largo": 440, "solapa_y": 300}`. Las formas son simétricas: defino media figura y `espejo()` arma la otra mitad.
4. **Ajuste al cuerpo.** Los moldes están hechos sobre un maniquí sencillo, y la modelo tiene otras proporciones. Marqué ~100 puntos que se corresponden en los dos cuerpos (hombro con hombro, rodilla con rodilla…); como la modelo es simétrica, marco solo el lado izquierdo y el derecho sale reflejado. Con un **thin-plate spline** (`ajuste.py`) encuentro la deformación más suave que lleva un cuerpo al otro, y con ella muevo cada coordenada de cada prenda. Le doy 3 px de **holgura** para que la ropa quede por fuera de la piel, y para pantalones, faldas y zapatos no uso los puntos de los brazos (las manos están pegadas a la cadera y "jalaban" la tela hacia adentro).
5. **Telas reales.** De las fotos de referencia saqué el color real de cada prenda (la mediana de un pedacito de tela) y su textura (solo las luces y sombras del tejido). La textura se repite encima de la prenda con `mix-blend-mode: overlay`. Un filtro SVG agrega sombra interior en los bordes y una sombra suave sobre el cuerpo, que es lo que le da volumen.
6. **Orden de capas:** modelo → calzado → abajo → arriba → abrigo → manos → cuello → bolso → cabeza.

### Rutas

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/` | Inicio |
| GET | `/probador` | El juego. Lo que tienes puesto va en la URL |
| GET | `/probador/panel` | Solo el panel (HTML parcial) |
| GET · POST | `/recomendar` | Recomendador |
| POST | `/api/evaluar` | Evalúa un outfit en JSON |
| GET | `/api/sorpresa` | Outfit al azar que combina |
| GET | `/api/prendas` | Catálogo en JSON |

Si JavaScript no carga, el probador sigue funcionando con enlaces normales (cada tarjeta del clóset es un `<a>`).

---

## 4. Funcionamiento de la aplicación

```mermaid
flowchart LR
    A[Toco una prenda] --> B[JS: muestra la prenda en el SVG con animación]
    B --> C[GET /probador/panel?...]
    C --> D{validar_seleccion}
    D -->|inválida| E[_panel.html con error · 400]
    D -->|ok| F[combinador.py: colores + estilos + clima]
    F --> G[Jinja2 arma _panel.html]
    G --> H[JS lo reemplaza y anima el puntaje]
```

**¿Qué datos recibe?** El id de una prenda por categoría (todas opcionales) y el clima (`frio`, `templado`, `caluroso` o nada).

**¿Cómo se procesan?** `evaluar_outfit()` en `combinador.py`:

1. **Valida** que cada prenda exista y esté en su categoría.
2. **Colores (40 %).** Cada color tiene un ángulo en el círculo cromático. Para cada par: mismo color → *monocromático* (1.0); con un neutro → *neutro* (1.0); ≤ 60° → *análogos* (0.9); ≥ 150° → *complementarios* (0.85), como azul y café; con un tono tierra → casi neutro (0.85); lo demás → *atrevido* (0.5), con aviso. El puntaje es el promedio entre **la media y la peor pareja**, para que un choque fuerte no quede escondido. Más de dos colores protagonistas resta 0.15.
3. **Estilos (40 %).** Tabla de compatibilidad (formal + deportivo = 0.2, casual + bohemio = 0.8…).
4. **Clima (20 %, opcional).** Porcentaje de prendas aptas para ese clima.
5. **Sugerencias.** Para cada categoría que falte (y el abrigo si hace frío), prueba todo el catálogo y elige la prenda que deja el mejor puntaje.
6. **Look de referencia.** Si armaste exactamente uno de los 14 looks, el panel lo reconoce (índice de Jaccard).

**Sorpréndeme** elige una parte superior al azar y, para cada categoría, escoge al azar **entre las 3 opciones con mejor puntaje**. Si no llega a 85, lo intenta otra vez (máximo 30 veces). Con `semilla` siempre da lo mismo, y eso es lo que permite probarlo.

**¿Qué hace FastAPI?** Recibe y valida los datos (`Depends`, Pydantic, `Form`), llama a la lógica y responde con plantilla o JSON con el código HTTP correcto.

**¿Cómo presenta Jinja2 los resultados?** El puntaje es un anillo (`conic-gradient`), los colores son bolitas con su hex, los avisos y sugerencias son listas, y la plataforma giratoria es una macro reutilizada en cuatro páginas.

**¿Qué pasa si la información es incorrecta?**

| Situación | Respuesta |
|---|---|
| Prenda inventada o en otra categoría | Mensaje de error · **400** |
| Clima inventado | **400** (en la API JSON, **422** por Pydantic) |
| Ninguna prenda | No es error: modelo en ropa base y un saludo con tips |
| Una sola prenda | No da puntaje, pero sí sugiere qué agregar |
| Recomendador sin filtros | **400** |

---

## 5. Instalación y ejecución

**Requisitos:** Python 3.10 o superior.

```bash
git clone https://github.com/sthephaniecardenas1-lang/vestidor-virtual.git
cd vestidor-virtual
python -m venv venv
venv\Scripts\activate          # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre **http://127.0.0.1:8000**.

**Cómo jugar:**
1. Entra a **Probador**, elige una categoría y toca prendas. Si vuelves a tocar una (o la tocas sobre la modelo), se quita.
2. Elige el clima si quieres que lo tenga en cuenta.
3. Mira el puntaje, los avisos y las sugerencias. Dale a **⟳ Animar** o a **🎲 Sorpréndeme**.
*(Opcional)* Para volver a sacar las telas: `pip install -r requirements-dev.txt` y `python herramientas/preparar_fotos.py`.

---

## 6. Pruebas automatizadas

```bash
pytest -v
```

**Así se vio en mi computador** (Windows, Python 3.12.10):

![pytest 1](evidencias/terminal/04_pytest_1.jpg)
![pytest 2](evidencias/terminal/05_pytest_2.jpg)
![pytest 3](evidencias/terminal/06_pytest_3.jpg)
![pytest 4](evidencias/terminal/07_pytest_4_y_servidor.jpg)

**Resultado: 117 pruebas, 117 exitosas** (43 funciones; varias usan `parametrize`, por ejemplo una prueba por cada una de las 61 prendas).

### Lógica de combinación (`test_combinador.py`)

| Prueba | ¿Qué comprueba? | Datos | Esperado | Obtenido | ✔ |
|---|---|---|---|---|---|
| `test_look_monocromatico_saca_puntaje_alto` | Funcionalidad principal | Look *Negro casual* | ≥ 90, sin avisos | 100 | ✅ |
| `test_relacion_entre_colores` (×6) | Círculo cromático | 6 parejas | complementarios, complementarios, análogos, neutro, atrevido, monocromático | Igual | ✅ |
| `test_estilos_que_chocan_dan_aviso_y_bajan_puntaje` | Estilos | Sastre + tenis de running | Baja y avisa | Igual | ✅ |
| `test_muchos_colores_protagonistas_genera_aviso` | Colores | Verde + azul + rosa | < 75 y aviso | 70 | ✅ |
| `test_el_clima_cambia_el_resultado` | Clima | Ropa de invierno con frío y con calor | Más puntos con frío | Igual | ✅ |
| `test_reconoce_un_look_completo` | Look exacto | *Azul formal* | 6 coincidencias | Igual | ✅ |
| `test_avatar_busca_el_look_mas_parecido` | Jaccard | Suéter + bufanda | `color_cafe` | Igual | ✅ |
| `test_sugiere_lo_que_falta_y_abrigo_si_hace_frio` | Sugerencias | Suéter + pantalón, frío | Calzado y abrigo aptos | Igual | ✅ |
| `test_sin_prendas_…` / `test_una_sola_prenda_…` | Casos límite | Nada / 1 prenda | Sin puntaje | Igual | ✅ |
| `test_prenda_que_no_existe` / `…categoria_equivocada` / `test_clima_invalido` | Datos inválidos | Ids o clima malos | `SeleccionInvalida` | Igual | ✅ |

### La modelo y el ajuste al cuerpo (`test_avatar.py`)

| Prueba | ¿Qué comprueba? | Esperado | ✔ |
|---|---|---|---|
| `test_todas_las_prendas_tienen_molde` | Catálogo y dibujo sincronizados | Las 61 prendas con molde | ✅ |
| `test_cada_prenda_se_dibuja` (×61) | Cada prenda | SVG válido, también ya ajustada al cuerpo | ✅ |
| `test_avatar_es_svg_valido_con_todo_el_closet` | Composición | 61 grupos; solo los del look marcados como puestos | ✅ |
| `test_orden_de_las_capas` | Capas | calzado < abajo < arriba < abrigo | ✅ |
| `test_solo_puestas_cuando_todas_es_false` | Modo liviano | Solo 2 grupos | ✅ |
| `test_espejo_es_simetrico` | Utilidad de dibujo | Figura completa cerrada | ✅ |
| `test_el_ajuste_respeta_los_puntos_marcados` | Thin-plate spline | Cada punto cae a < 0.6 px de su destino | ✅ |
| `test_la_ropa_queda_un_poco_por_fuera_del_cuerpo` | Holgura | El hombro con holgura queda más afuera | ✅ |
| `test_la_modelo_es_simetrica` | Puntos reflejados | Un punto y su reflejo caen simétricos | ✅ |
| `test_deformar_svg_mueve_rectangulos_y_circulos` | Ajuste de figuras | El rect pasa a path y el círculo se mueve | ✅ |

### Rutas (`test_rutas.py`, con `TestClient`)

| Prueba | ¿Qué comprueba? | Esperado | ✔ |
|---|---|---|---|
| `test_inicio_responde` | `GET /` | 200 con la modelo | ✅ |
| `test_probador_vacio_muestra_la_modelo_en_ropa_base` | Estado inicial | Modelo sin prendas, 61 tarjetas | ✅ |
| `test_probador_viste_a_la_avatar` | Flujo completo | Prendas puestas y look reconocido | ✅ |
| `test_panel_parcial` | HTML parcial | Solo el panel | ✅ |
| `test_probador_con_prenda_inventada_responde_400` | Dato inválido | 400 | ✅ |
| `test_formulario_recomendar` / `…sin_filtros_responde_400` | Recomendador | 200 / 400 | ✅ |
| `test_api_evaluar` / `test_api_rechaza_clima_invalido` | API | 200 / 422 | ✅ |
| `test_api_sorpresa` | API | Outfit completo ≥ 80 | ✅ |
| `test_cada_tarjeta_del_closet_trae_su_dibujo` | Clóset | 61 tarjetas, cada una con su prenda dibujada | ✅ |

### Recomendador y Sorpréndeme

| Archivo | Qué comprueba | ✔ |
|---|---|---|
| `test_recomendador.py` (7) | El look exacto sale primero, máximo 3 resultados ordenados, los 14 looks dan ≥ 90, filtros inválidos | ✅ |
| `test_sorpresa.py` (11) | Con 8 semillas siempre da superior + inferior + calzado, una prenda por categoría y ≥ 80; respeta el clima; es repetible con semilla; rechaza estilos inválidos | ✅ |

---

## 7. Evidencias de funcionamiento

### La aplicación

| | |
|---|---|
| **Inicio** ![](evidencias/01_inicio.jpg) | **Modelo sin ropa encima** ![](evidencias/02_probador_base.jpg) |
| **Vistiendo a la modelo** ![](evidencias/03_vistiendo.jpg) | **Animar** ![](evidencias/04_animar.jpg) |
| **Sorpréndeme** ![](evidencias/05_sorprendeme.jpg) | **Vista previa al pasar el mouse** ![](evidencias/06_vista_previa.jpg) |
| **Avisos de estilo y clima** ![](evidencias/07_avisos.jpg) | **Dato inválido** ![](evidencias/08_error.jpg) |
| **Recomendador** ![](evidencias/09_recomendador.jpg) | |

### Instalación en mi computador

| | | |
|---|---|---|
| ![](evidencias/terminal/01_instalacion_1.jpg) | ![](evidencias/terminal/02_instalacion_2.jpg) | ![](evidencias/terminal/03_instalacion_3.jpg) |

### Ejecución de las pruebas (117 passed)

| | |
|---|---|
| ![](evidencias/terminal/04_pytest_1.jpg) | ![](evidencias/terminal/05_pytest_2.jpg) |
| ![](evidencias/terminal/06_pytest_3.jpg) | ![](evidencias/terminal/07_pytest_4_y_servidor.jpg) |

### Servidor funcionando

Cada vez que toco una prenda, el navegador le pide el panel a FastAPI (`GET /probador/panel?...`) y responde `200 OK`. Al final apagué el servidor con Ctrl + C.

| | |
|---|---|
| ![](evidencias/terminal/08_servidor_1.jpg) | ![](evidencias/terminal/09_servidor_2.jpg) |
| ![](evidencias/terminal/10_servidor_3.jpg) | ![](evidencias/terminal/11_servidor_4.jpg) |
| ![](evidencias/terminal/12_servidor_5.jpg) | ![](evidencias/terminal/13_servidor_6.jpg) |
| ![](evidencias/terminal/14_servidor_7.jpg) | ![](evidencias/terminal/15_servidor_apagado.jpg) |

---

## 8. Conclusiones

**Desafíos**

- **Pasar "esto se ve bien" a números.** Con solo el promedio, un sastre con tenis de correr salía como "Buen outfit". Combinar el promedio con la peor pareja lo arregló, y se parece más a cómo uno se mira al espejo: si una sola cosa no pega, se nota.
- **Que la modelo se viera bien y aun así se pudiera vestir con cualquier prenda.** Probé con fotos completas, pero a una foto no se le puede poner una prenda suelta sin que se vea pegada. La solución fue usar una modelo ilustrada de frente, con las manos en otra capa, y dibujar encima prendas que se ajustan a su cuerpo.
- **Ajustar la ropa a otro cuerpo.** Al principio las prendas quedaban corridas o se asomaba la piel. Aprendí qué es un *thin-plate spline* y lo programé yo misma (resolviendo el sistema de ecuaciones con eliminación gaussiana). Después agregué holgura y separé los puntos de los brazos para que no deformaran los pantalones.
- **Que no se viera "plano".** El color real de la tela, la textura del tejido y la sombra interior de los bordes fueron lo que le dio volumen.

**Lo que aprendí sobre FastAPI + Jinja2 + pytest**

- Separar la lógica de las rutas hace todo más fácil de probar: la mayoría de las pruebas no necesitan servidor.
- Una plantilla parcial sirve para la página completa y para las actualizaciones en vivo, y las macros evitan repetir HTML.
- Python puede generar SVG como texto, y Jinja2 lo inserta en la página igual que cualquier otro contenido.
- Pydantic devuelve **422** y no 400; lo aprendí escribiendo la prueba.
- `parametrize` me dejó revisar las 61 prendas con una sola función.
