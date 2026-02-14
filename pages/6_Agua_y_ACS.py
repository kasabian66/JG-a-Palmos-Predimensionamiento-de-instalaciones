# -*- coding: utf-8 -*-
import streamlit as st

from core.state import init_state, get_zones_df, get_settings
from core.calculations import calc_agua_y_acs
from core.constants import TABLA_13_AGUA_FRIA_L_DIA, TABLA_14_ACS

init_state()
st.title("6) Fontanería: Agua potable y ACS")

zones_df = get_zones_df()
settings = get_settings()

uso_global = settings.get("uso_edificio")
if not uso_global:
    try:
        uso_global = str(zones_df["Uso"].dropna().iloc[0])
    except Exception:
        uso_global = "Oficinas"

st.write("Estimación de consumos diarios y potencia para ACS.")
st.caption("Agua fría: Tabla 13. ACS (consumo y potencia): Tabla 14.")

opt13 = ["(sin mapear)"] + list(TABLA_13_AGUA_FRIA_L_DIA.keys())
opt14 = ["(sin mapear)"] + list(TABLA_14_ACS.keys())

def default_tabla13(uso: str) -> str:
    u = (uso or "").strip()
    if u in TABLA_13_AGUA_FRIA_L_DIA:
        return u
    if u == "Oficinas":
        return "Oficinas sin cafetería"
    if u == "Enseñanza (aularios)":
        return "Escuelas, institutos"
    if u.startswith("Hospitales"):
        return "Hospitales"
    if u == "Hoteles":
        return "Hoteles media categoría"
    if "Restaur" in u or "Cafeter" in u:
        return "Restaurantes"
    return "(sin mapear)"

def default_tabla14(uso: str) -> str:
    u = (uso or "").strip()
    if u in TABLA_14_ACS:
        return u
    if u in ("Oficinas sin cafetería", "Oficinas con cafetería"):
        return "Oficinas"
    if u == "Enseñanza (aularios)":
        return "Escuelas, institutos"
    if u.startswith("Hospitales"):
        return "Hospitales"
    if u == "Hoteles":
        return "Hoteles media categoría"
    if "Restaur" in u or "Cafeter" in u:
        return "Restaurantes"
    return "(sin mapear)"

map13 = settings.get("mapa_uso_tabla13", {}) or {}
map14 = settings.get("mapa_uso_tabla14", {}) or {}

cur13 = map13.get(uso_global, None) or default_tabla13(uso_global)
cur14 = map14.get(uso_global, None) or default_tabla14(uso_global)

with st.expander("Mapeo del uso del edificio a Tablas 13 y 14", expanded=True):
    c1, c2 = st.columns(2)
    sel13 = c1.selectbox(f"{uso_global} → Tabla 13 (agua fría)", options=opt13, index=opt13.index(cur13) if cur13 in opt13 else 0)
    sel14 = c2.selectbox(f"{uso_global} → Tabla 14 (ACS)", options=opt14, index=opt14.index(cur14) if cur14 in opt14 else 0)

if sel13 == "(sin mapear)":
    settings["mapa_uso_tabla13"] = {}
else:
    settings["mapa_uso_tabla13"] = {uso_global: sel13}

if sel14 == "(sin mapear)":
    settings["mapa_uso_tabla14"] = {}
else:
    settings["mapa_uso_tabla14"] = {uso_global: sel14}

df, warnings, totals = calc_agua_y_acs(zones_df, settings)

c1, c2, c3 = st.columns(3)
c1.metric("Agua fría total (m³/día)", f"{totals['agua_fria_total_m3_dia']:.1f}")
c2.metric("ACS total (m³/día)", f"{totals['acs_total_m3_dia']:.1f}")
c3.metric("Potencia ACS (kW)", f"{totals['acs_potencia_total_kw']:.1f}")

st.dataframe(df, use_container_width=True, hide_index=True)

if warnings:
    st.subheader("Avisos")
    seen = set()
    for w in warnings:
        key = (w.module, w.message)
        if key in seen:
            continue
        seen.add(key)
        st.warning(f"[{w.module}] {w.zone}: {w.message}")

st.info("Para hoteles/hospitales usa 'Camas'. Para restaurantes usa 'Cubiertos/día'. En caso contrario usa densidad o 'Personas'.")
