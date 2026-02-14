# -*- coding: utf-8 -*-
import streamlit as st

from core.state import init_state, get_zones_df, get_settings
from core.calculations import calc_ventilacion_y_todo_aire
from core.constants import TABLA_9_TODO_AIRE_LS_M2

init_state()
st.title("4) Ventilación y sistema todo-aire")

zones_df = get_zones_df()
settings = get_settings()

uso_global = settings.get("uso_edificio")
if not uso_global:
    # fallback: first uso in tabla si existiera
    try:
        uso_global = str(zones_df["Uso"].dropna().iloc[0])
    except Exception:
        uso_global = "Oficinas"

st.write("Ventilación exterior: Tabla 10. Caudal tratado en sistema todo-aire: Tabla 9 (si aplica).")

settings["todo_aire_activo"] = st.checkbox("Aplicar sistema todo-aire (Tabla 9)", value=bool(settings.get("todo_aire_activo", False)))

st.subheader("Garaje bajo rasante (CTE) — aportación vs extracción")
gfa_below = float(settings.get("gfa_below_m2", 0.0) or 0.0)

if gfa_below > 0:
    modo_opts = [
        "Salubridad (CTE DB-HS 3) — 120/120 L/s·plaza",
        "Control de humos (CTE DB-SI 3) — 120/150 L/s·plaza",
    ]

    default_modo = settings.get("parking_modo") or modo_opts[0]
    if default_modo not in modo_opts:
        default_modo = modo_opts[0]

    c0a, c0b = st.columns([2, 1])
    with c0a:
        new_modo = st.selectbox("Modo de ventilación del parking", modo_opts, index=modo_opts.index(default_modo))
    with c0b:
        settings["parking_plazas"] = st.number_input("Nº de plazas (bajo rasante)", min_value=0, step=1, value=int(settings.get("parking_plazas", 0) or 0))

    # Defaults by mode
    if new_modo == modo_opts[1]:
        def_aporte = 120.0
        def_extr = 150.0
    else:
        def_aporte = 120.0
        def_extr = 120.0

    # Override toggle: if OFF -> always keep CTE defaults and disable editing
    override_cte = st.checkbox("Modificar valores CTE (manual override)", value=bool(settings.get("parking_override_cte", False)))
    settings["parking_override_cte"] = override_cte

    # Persist mode and auto-update when mode changes (unless user overrides)
    prev_modo = settings.get("parking_modo") or ""
    settings["parking_modo"] = new_modo

    if (not override_cte) or (prev_modo != new_modo):
        # auto-apply defaults (also when switching modes)
        settings["parking_aporte_lps_por_plaza"] = def_aporte
        settings["parking_extraccion_lps_por_plaza"] = def_extr

    cpa, cpb = st.columns(2)
    with cpa:
        settings["parking_aporte_lps_por_plaza"] = st.number_input(
            "Caudal de APORTACIÓN (L/s·plaza) — CTE",
            min_value=0.0, step=10.0,
            value=float(settings.get("parking_aporte_lps_por_plaza", def_aporte) or def_aporte),
            disabled=(not override_cte),
        )
    with cpb:
        settings["parking_extraccion_lps_por_plaza"] = st.number_input(
            "Caudal de EXTRACCIÓN (L/s·plaza) — CTE",
            min_value=0.0, step=10.0,
            value=float(settings.get("parking_extraccion_lps_por_plaza", def_extr) or def_extr),
            disabled=(not override_cte),
        )

    plazas = float(settings.get("parking_plazas", 0) or 0)
    q_aporte = plazas * float(settings.get("parking_aporte_lps_por_plaza", def_aporte) or 0)
    q_extr = plazas * float(settings.get("parking_extraccion_lps_por_plaza", def_extr) or 0)

    st.caption("La aportación y la extracción del parking se calculan por plazas según el modo seleccionado (CTE).")
    st.write(f"**Aportación parking:** {q_aporte:,.0f} L/s  ({q_aporte*3.6:,.0f} m³/h)")
    st.write(f"**Extracción parking:** {q_extr:,.0f} L/s  ({q_extr*3.6:,.0f} m³/h)")
else:
    st.info("No hay superficie bajo rasante definida. No se aplica ventilación de garaje.")


# --- Mapeo (uso único) ---
st.subheader("Tipología de Tabla 9 (solo si aplica sistema todo-aire)")
tip_opts = ["(sin mapear)"] + list(TABLA_9_TODO_AIRE_LS_M2.keys())

def default_tipologia(uso: str) -> str:
    u = (uso or "").strip()
    if u == "Oficinas":
        return "Oficinas - Espacio abierto"
    if u in ("Auditorios", "Teatros", "Salones de actos"):
        return "Auditorios / Teatros"
    if u == "Enseñanza (aularios)":
        return "Enseñanza (aularios)"
    if u.startswith("Hospitales"):
        # elegir la opción "General" por defecto
        return "Hospitales - General (excepto quirófanos)"
    if u == "Hoteles":
        return "Hoteles (habitaciones)"
    if u in ("Museos", "Bibliotecas", "Archivos"):
        return "Museos / Bibliotecas"
    if "Restaur" in u or "Cafeter" in u:
        return "Restaurantes / Cafeterías - Medianos"
    if "Grandes almacenes" in u:
        return "Grandes almacenes - Planta baja"
    if u in ("Comercios - Galerías comerciales",):
        return "Comercios - Galerías comerciales"
    return "(sin mapear)"

mapa = settings.get("mapa_uso_tabla9", {}) or {}
cur = mapa.get(uso_global, None)
if cur is None:
    cur = default_tipologia(uso_global)

if settings.get("todo_aire_activo", False):
    sel = st.selectbox(f"{uso_global} → Tipología Tabla 9", options=tip_opts, index=tip_opts.index(cur) if cur in tip_opts else 0)
    if sel == "(sin mapear)":
        settings["mapa_uso_tabla9"] = {}
    else:
        settings["mapa_uso_tabla9"] = {uso_global: sel}
else:
    st.info("Sistema todo-aire desactivado: no se calcula Tabla 9 ni se requieren mapeos.")

df, warnings, totals = calc_ventilacion_y_todo_aire(zones_df, settings)

c1, c2, c3 = st.columns(3)
c1.metric("Ventilación sobre rasante (L/s)", f"{totals['vent_sobre_rasante_lps']:.0f}")
c2.metric("Ventilación sobre rasante (m³/h)", f"{totals['vent_sobre_rasante_m3h']:.0f}")
c3.metric("Aportación parking (L/s)", f"{totals.get('vent_garaje_aporte_lps', 0):.0f}")

c4, c5, c6 = st.columns(3)
c4.metric("Aportación parking (m³/h)", f"{totals.get('vent_garaje_aporte_m3h', 0):.0f}")
c5.metric("Extracción parking (L/s)", f"{totals.get('vent_garaje_extraccion_lps', 0):.0f}")
c6.metric("Extracción parking (m³/h)", f"{totals.get('vent_garaje_extraccion_m3h', 0):.0f}")

c7, c8 = st.columns(2)
c7.metric("Todo-aire total (L/s)", f"{totals['todoaire_total_lps']:.0f}")
c8.metric("Todo-aire total (m³/h)", f"{totals['todoaire_total_m3h']:.0f}")

if (totals.get('vent_garaje_extraccion_lps', 0) > 0) or (totals.get('vent_garaje_aporte_lps', 0) > 0):
    st.info("La aportación/extracción del parking (bajo rasante) se reporta por separado y no se suma a la ventilación de sobre rasante.")

st.dataframe(df, use_container_width=True, hide_index=True)

if warnings:
    st.subheader("Avisos")
    # agrupar avisos idénticos para no repetir
    seen = set()
    for w in warnings:
        key = (w.module, w.message)
        if key in seen:
            continue
        seen.add(key)
        st.warning(f"[{w.module}] {w.zone}: {w.message}")

st.info("Para zonas sin dato en Tabla 10, usa **Ventilación override** en 'Datos y zonas'.")
