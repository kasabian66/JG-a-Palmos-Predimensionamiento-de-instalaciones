# -*- coding: utf-8 -*-
import streamlit as st

from core.state import init_state, get_zones_df, get_settings
from core.calculations import calc_climatizacion

init_state()
st.title("3) Climatización (Frío y Calor)")

zones_df = get_zones_df()
settings = get_settings()

st.write("Cálculo de cargas por zona:")
st.caption("Frío: Tabla 5 + Factor Tabla 6. Calor: Tabla 7 + Factor Tabla 8.")

col1, col2 = st.columns(2)
with col1:
    settings["oversize_frio"] = st.number_input("Factor sobredimensionado generador frío", min_value=0.8, max_value=1.5, value=float(settings.get("oversize_frio", 1.0)), step=0.05)
with col2:
    settings["oversize_calor"] = st.number_input("Factor sobredimensionado generador calor", min_value=0.8, max_value=1.8, value=float(settings.get("oversize_calor", 1.1)), step=0.05)

df, warnings, totals = calc_climatizacion(zones_df, settings)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Frío total (kW)", f"{totals['frio_total_kw']:.1f}")
c2.metric("Gen. frío (kW)", f"{totals['frio_generador_kw']:.1f}")
c3.metric("Calor total (kW)", f"{totals['calor_total_kw']:.1f}")
c4.metric("Gen. calor (kW)", f"{totals['calor_generador_kw']:.1f}")

st.dataframe(df, use_container_width=True, hide_index=True)

if warnings:
    st.subheader("Avisos")
    for w in warnings:
        st.warning(f"[{w.module}] {w.zone}: {w.message}")

st.info("Si un uso no existe en la Tabla correspondiente, usa los campos **override** en 'Datos y zonas'.")
