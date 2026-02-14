# -*- coding: utf-8 -*-
import streamlit as st
from core.state import init_state, get_zones_df, get_settings
from core.calculations import calc_reservas_espacios
from core.constants import TABLA_2_ESPACIO_POR_INSTALACION

init_state()
st.title("2) Reservas de espacio")

zones_df = get_zones_df()
settings = get_settings()

st.write("Estimación de superficie a reservar para salas de máquinas/equipos.")
st.caption("Tabla 1 (global) y Tabla 2 (por instalación) del documento.")

st.subheader("Selección de instalaciones (Tabla 2)")
inst_opts = list(TABLA_2_ESPACIO_POR_INSTALACION.keys())
sel = st.multiselect("Incluye en el cálculo", options=inst_opts, default=settings.get("instalaciones_seleccion") or inst_opts)
settings["instalaciones_seleccion"] = sel

df, warnings, totals = calc_reservas_espacios(zones_df, settings)

c1, c2, c3 = st.columns(3)
c1.metric("Superficie total (m²)", f"{totals['superficie_total_m2']:.0f}")
c2.metric("Reserva global mín (m²)", f"{totals['reserva_global_min_m2']:.0f}")
c3.metric("Reserva global máx (m²)", f"{totals['reserva_global_max_m2']:.0f}")

st.dataframe(df, use_container_width=True, hide_index=True)

if warnings:
    st.subheader("Avisos")
    for w in warnings:
        st.warning(f"[{w.module}] {w.zone}: {w.message}")
