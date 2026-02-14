# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

from core.state import init_state, get_zones_df, get_settings
from core.calculations import (
    calc_climatizacion, calc_ventilacion_y_todo_aire, calc_electricidad, calc_agua_y_acs, calc_reservas_espacios, calc_pci
)

st.set_page_config(
    page_title="Predimensionamiento de instalaciones",
    page_icon="🏢",
    layout="wide",
)

init_state()

st.title("🏢 Predimensionamiento de instalaciones (Anteproyecto)")
st.caption("Basado en: 'LAS INSTALACIONES A PALMOS - Manual de Predimensionado' (JG Ingenieros).")

zones_df = get_zones_df()
settings = get_settings()

col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Datos del edificio")
    st.write("Define las zonas/áreas del edificio en **Datos y zonas** (menú lateral). "
             "El resto de módulos calculan a partir de esa tabla.")

    st.dataframe(zones_df[["ID","Nombre zona","Uso","Superficie (m²)","Zona climática","Nivel carga (B/M/A)"]], use_container_width=True, hide_index=True)

with col2:
    st.subheader("Resumen rápido")
    total_m2 = pd.to_numeric(zones_df["Superficie (m²)"], errors="coerce").fillna(0).sum()
    st.metric("Superficie total (m²)", f"{total_m2:,.0f}".replace(",", " "))

    # Cálculos rápidos
    try:
        df_clima, _, tot_clima = calc_climatizacion(zones_df, settings)
        st.metric("Frío total (kW)", f"{tot_clima['frio_total_kw']:.1f}")
        st.metric("Calor total (kW)", f"{tot_clima['calor_total_kw']:.1f}")
    except Exception as e:
        st.warning("Completa datos para obtener resumen de climatización.")

    try:
        df_e, _, tot_e = calc_electricidad(zones_df, settings)
        st.metric("Potencia eléctrica (kW)", f"{tot_e['potencia_total_kw']:.1f}")
        st.caption(f"Acometida sugerida: **{tot_e['acometida_sugerida']}** (umbral 400 kW).")
    except Exception:
        pass

st.divider()
st.info("Siguiente paso: abre **Datos y zonas** para ajustar usos, superficies, zona climática y nivel de carga. Luego revisa cada módulo.")

