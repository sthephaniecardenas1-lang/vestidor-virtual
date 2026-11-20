/*
  Probador tipo juego.

  Todo el clóset ya viene dibujado (y ajustado al cuerpo) dentro del SVG de
  la avatar, oculto. Vestir = mostrar/ocultar grupos <g id="g-ID"> con una
  animación, al instante. Lo único que se le pide a FastAPI es el panel de
  resultados (/probador/panel), que Jinja2 arma con el puntaje, los avisos y
  las sugerencias.

  Si JavaScript no carga, todo sigue funcionando con enlaces normales.
*/
(() => {
  "use strict";

  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];

  const CATEGORIAS = ["superior", "inferior", "abrigo", "calzado", "bolso", "cuello", "cabeza"];
  // altura aproximada (en % del espejo) donde salen los destellos de cada categoría
  const ALTURA = { cabeza: 8, cuello: 21, superior: 30, abrigo: 36, bolso: 49, inferior: 62, calzado: 92 };
  const COLORES_CONFETI = ["#e3a6b0", "#b98b5e", "#8fb79a", "#22345c", "#d1ab55", "#f6f3ec"];

  const inicial = JSON.parse($("#estado").textContent);
  let sel = limpiar(inicial.seleccion);
  let clima = inicial.clima || "";
  let ultimoPuntaje = null;
  let peticion = 0;
  const historial = [];

  const panel = $("#panel");
  const escenario = $("#escenario");
  const efectos = $("#efectos");
  const btnDeshacer = $("#btn-deshacer");
  const conHover = window.matchMedia("(hover: hover)").matches;

  // ------------------------------------------------------------- utilidades

  function limpiar(obj) {
    const out = {};
    CATEGORIAS.forEach((c) => { if (obj && obj[c]) out[c] = obj[c]; });
    return out;
  }

  function query(extra = {}) {
    const datos = { ...sel, ...extra };
    const p = new URLSearchParams();
    CATEGORIAS.forEach((c) => { if (datos[c]) p.set(c, datos[c]); });
    if (clima) p.set("clima", clima);
    p.set("enviado", "1");
    return p.toString();
  }

  const grupo = (id) => document.getElementById("g-" + id);

  function toast(mensaje) {
    const t = document.createElement("div");
    t.className = "toast";
    t.textContent = mensaje;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2600);
  }

  // ------------------------------------------------------- vestir / quitar

  function mostrarPrenda(id, animar = true) {
    const g = grupo(id);
    if (!g) return;
    g.dataset.v = String(Number(g.dataset.v || 0) + 1); // cancela un "quitar" pendiente
    g.classList.remove("sale", "previa");
    g.classList.add("puesta");
    if (animar) {
      g.classList.remove("entra");
      void g.getBoundingClientRect(); // reinicia la animación
      g.classList.add("entra");
      g.addEventListener("animationend", () => g.classList.remove("entra"), { once: true });
      destellos(g.dataset.categoria);
    }
  }

  function ocultarPrenda(id, animar = true) {
    const g = grupo(id);
    if (!g) return;
    const v = String(Number(g.dataset.v || 0) + 1);
    g.dataset.v = v;
    const fin = () => { if (g.dataset.v === v) g.classList.remove("puesta", "sale", "entra"); };
    if (!animar) return fin();
    g.classList.remove("entra");
    g.classList.add("sale");
    g.addEventListener("animationend", fin, { once: true });
    setTimeout(fin, 450);
  }

  function aplicar(nueva, { animar = true, guardar = true, escalonar = 0 } = {}) {
    quitarPrevia();
    nueva = limpiar(nueva);
    if (guardar) {
      historial.push({ ...sel });
      if (historial.length > 50) historial.shift();
    }
    const anterior = sel;
    sel = nueva;

    let retraso = 0;
    CATEGORIAS.forEach((cat) => {
      const antes = anterior[cat];
      const despues = sel[cat];
      if (antes === despues) return;
      if (antes) ocultarPrenda(antes, animar);
      if (despues) {
        if (escalonar) {
          setTimeout(() => { if (sel[cat] === despues) mostrarPrenda(despues, animar); }, retraso);
          retraso += escalonar;
        } else {
          mostrarPrenda(despues, animar);
        }
      }
    });

    actualizarVista();
    refrescarPanel();
  }

  function alternar(id, cat) {
    const nueva = { ...sel };
    nueva[cat] = sel[cat] === id ? "" : id;
    aplicar(nueva);
  }

  function actualizarVista() {
    $(".base-top")?.classList.toggle("oculta", Boolean(sel.superior));
    $(".base-short")?.classList.toggle("oculta", Boolean(sel.inferior));

    $$("[data-tarjeta]").forEach((tarjeta) => {
      const enlace = $(".poner", tarjeta);
      const id = tarjeta.dataset.tarjeta;
      const cat = enlace.dataset.categoria;
      const puesta = sel[cat] === id;
      tarjeta.classList.toggle("puesta", puesta);
      enlace.setAttribute("aria-pressed", String(puesta));
      enlace.href = "/probador?" + query({ [cat]: puesta ? "" : id });
    });
    $$(".pestana").forEach((p) => p.classList.toggle("con-prenda", Boolean(sel[p.dataset.pestana])));

    const vacio = Object.keys(sel).length === 0;
    $("#pista")?.classList.toggle("oculta", !vacio);
    btnDeshacer.disabled = historial.length === 0;
    history.replaceState(null, "", "/probador?" + query());
  }

  // ------------------------------------------------------ vista previa (hover)

  function previa(id, cat) {
    if (!conHover || sel[cat] === id) return;
    quitarPrevia();
    grupo(id)?.classList.add("previa");
    if (sel[cat]) grupo(sel[cat])?.classList.add("tapada");
  }

  function quitarPrevia() {
    $$(".prenda.previa").forEach((g) => g.classList.remove("previa"));
    $$(".prenda.tapada").forEach((g) => g.classList.remove("tapada"));
  }

  // ------------------------------------------------------------ panel

  async function refrescarPanel() {
    const n = ++peticion;
    panel.classList.add("cargando");
    try {
      const r = await fetch("/probador/panel?" + query());
      const html = await r.text();
      if (n !== peticion) return; // llegó tarde, ya hay una más nueva
      panel.innerHTML = html;
      animarPuntaje();
    } catch {
      toast("No pude actualizar el panel. ¿El servidor sigue encendido?");
    } finally {
      if (n === peticion) panel.classList.remove("cargando");
    }
  }

  function animarPuntaje(celebrar = true) {
    const caja = $(".puntaje", panel);
    const dato = $(".panel-interno", panel)?.dataset.puntaje;
    if (!caja || dato === "" || dato === undefined) { ultimoPuntaje = null; return; }

    const fin = Number(dato);
    const ini = ultimoPuntaje ?? 0;
    const numero = $("[data-numero]", caja);
    const t0 = performance.now();
    const paso = (t) => {
      const k = Math.min((t - t0) / 650, 1);
      const suave = 1 - Math.pow(1 - k, 3);
      const v = Math.round(ini + (fin - ini) * suave);
      caja.style.setProperty("--p", v);
      numero.textContent = v;
      if (k < 1) requestAnimationFrame(paso);
    };
    requestAnimationFrame(paso);

    if (celebrar && fin >= 90 && (ultimoPuntaje === null || ultimoPuntaje < 90) && Object.keys(sel).length >= 3) confeti();
    if (fin >= 90) caja.classList.add("brilla");
    ultimoPuntaje = fin;
  }

  // ---------------------------------------------------------- efectos

  function destellos(cat) {
    const base = ALTURA[cat] ?? 40;
    for (let i = 0; i < 7; i++) {
      const s = document.createElement("span");
      s.className = "destello";
      s.style.left = 50 + (Math.random() * 36 - 18) + "%";
      s.style.top = base + (Math.random() * 12 - 6) + "%";
      s.style.animationDelay = Math.random() * 180 + "ms";
      s.style.setProperty("--tam", 8 + Math.random() * 10 + "px");
      efectos.appendChild(s);
      setTimeout(() => s.remove(), 1100);
    }
  }

  function confeti() {
    for (let i = 0; i < 42; i++) {
      const c = document.createElement("span");
      c.className = "confeti";
      c.style.left = Math.random() * 100 + "%";
      c.style.background = COLORES_CONFETI[i % COLORES_CONFETI.length];
      c.style.animationDelay = Math.random() * 400 + "ms";
      c.style.setProperty("--giro", Math.random() * 720 - 360 + "deg");
      c.style.setProperty("--x", Math.random() * 80 - 40 + "px");
      efectos.appendChild(c);
      setTimeout(() => c.remove(), 2400);
    }
  }

  // ------------------------------------------------------------ pestañas

  function activarPestana(cat, enfocar = false) {
    $$(".pestana").forEach((p) => {
      const activa = p.dataset.pestana === cat;
      p.classList.toggle("activa", activa);
      p.setAttribute("aria-selected", String(activa));
      p.tabIndex = activa ? 0 : -1;
      if (activa && enfocar) p.focus();
    });
    $$(".estante").forEach((e) => e.classList.toggle("activo", e.dataset.estante === cat));
  }

  // -------------------------------------------------------------- eventos

  document.addEventListener("click", (e) => {
    const poner = e.target.closest("[data-poner]");
    if (poner) {
      e.preventDefault();
      alternar(poner.dataset.poner, poner.dataset.categoria);
      return;
    }
    const enAvatar = e.target.closest(".juego .avatar-svg .prenda.puesta");
    if (enAvatar) {
      alternar(enAvatar.dataset.id, enAvatar.dataset.categoria);
      toast("Quitaste: " + ($(`[data-tarjeta="${enAvatar.dataset.id}"] .nombre`)?.textContent || "prenda"));
      return;
    }
    const pestana = e.target.closest("[data-pestana]");
    if (pestana) return activarPestana(pestana.dataset.pestana);

  });

  $("#btn-animar").addEventListener("click", (e) => {
    const activo = escenario.classList.toggle("animando");
    e.currentTarget.setAttribute("aria-pressed", String(activo));
  });



  // vista previa al pasar el mouse por el clóset
  document.addEventListener("pointerover", (e) => {
    const enlace = e.target.closest(".tarjeta-prenda .poner");
    if (enlace) previa(enlace.dataset.poner, enlace.dataset.categoria);
  });
  $(".closet").addEventListener("pointerleave", quitarPrevia);
  document.addEventListener("pointerout", (e) => {
    const enlace = e.target.closest(".tarjeta-prenda .poner");
    if (enlace && !enlace.contains(e.relatedTarget)) quitarPrevia();
  });

  // teclado: flechas en las pestañas y Ctrl+Z para deshacer
  $(".pestanas").addEventListener("keydown", (e) => {
    if (!["ArrowLeft", "ArrowRight"].includes(e.key)) return;
    const pestanas = $$(".pestana");
    const actual = pestanas.findIndex((p) => p.classList.contains("activa"));
    const sig = (actual + (e.key === "ArrowRight" ? 1 : -1) + pestanas.length) % pestanas.length;
    activarPestana(pestanas[sig].dataset.pestana, true);
  });
  document.addEventListener("keydown", (e) => {
    const escribiendo = ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName);
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && !btnDeshacer.disabled && !escribiendo) {
      e.preventDefault();
      btnDeshacer.click();
    }
  });

  btnDeshacer.addEventListener("click", () => {
    const anterior = historial.pop();
    if (anterior) aplicar(anterior, { guardar: false });
  });

  $("#btn-quitar").addEventListener("click", (e) => {
    e.preventDefault();
    if (Object.keys(sel).length) aplicar({});
  });

  $("#btn-sorpresa").addEventListener("click", async (e) => {
    const boton = e.currentTarget;
    boton.classList.add("girando");
    boton.disabled = true;
    try {
      const estilo = $("#sorpresa-estilo").value;
      const r = await fetch(`/api/sorpresa?${new URLSearchParams({ estilo, clima })}`);
      const datos = await r.json();
      if (!r.ok) throw new Error(datos.detail);
      aplicar(datos.seleccion, { escalonar: 160 });
    } catch (err) {
      toast(err.message || "No se me ocurrió nada 😅 intenta otra vez.");
    } finally {
      setTimeout(() => { boton.classList.remove("girando"); boton.disabled = false; }, 600);
    }
  });

  $("#clima").addEventListener("change", (e) => {
    clima = e.target.value;
    actualizarVista();
    refrescarPanel();
  });


  // ------------------------------------------------------------- inicio
  $$(".pestana").forEach((p, i) => { p.tabIndex = i === 0 ? 0 : -1; });
  actualizarVista();
  animarPuntaje(false); // al cargar solo cuenta el número, sin confeti
})();
