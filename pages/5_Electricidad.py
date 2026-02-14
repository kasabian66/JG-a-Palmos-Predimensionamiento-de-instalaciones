# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

from core.state import init_state, get_zones_df, get_settings
from core.calculations import calc_electricidad

init_state()
st.title("5) Electricidad")

zones_df = get_zones_df()
settings = get_settings()

st.write("Potencia eléctrica específica (suministro normal): Tabla 11. Suministro complementario: Tabla 12.")
st.caption("Criterio del documento: <400 kW -> acometida BT; >400 kW -> considerar MT.")

df, warnings, totals = calc_electricidad(zones_df, settings)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Normal (kW)", f"{totals['potencia_normal_kw']:.1f}")
c2.metric("Complementario (kW)", f"{totals['potencia_comp_kw']:.1f}")
c3.metric("Total (kW)", f"{totals['potencia_total_kw']:.1f}")
c4.metric("Acometida sugerida", totals["acometida_sugerida"])

st.dataframe(df, use_container_width=True, hide_index=True)

if warnings:
    st.subheader("Avisos")
    for w in warnings:
        st.warning(f"[{w.module}] {w.zone}: {w.message}")

# Motors/inrush module removed per requirements.
