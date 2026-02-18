import streamlit as st
from core.state import get_settings, set_settings, DEFAULTS
from core.calcs import calc_hvac
from core.ui import warnings_box
st.title("2) Climatización (predimensionado)")
s = get_settings()
u = DEFAULTS["uses"][s["use"]]
c1,c2 = st.columns(2)
with c1:
    s["hvac_cooling_wm2"] = st.number_input("Frío específico (W/m²)", min_value=0.0, step=5.0, value=float(s.get("hvac_cooling_wm2",u["hvac_cooling_wm2"])))
with c2:
    s["hvac_heating_wm2"] = st.number_input("Calor específico (W/m²)", min_value=0.0, step=5.0, value=float(s.get("hvac_heating_wm2",u["hvac_heating_wm2"])))
set_settings(s)
df,_ = calc_hvac(s)
st.dataframe(df, use_container_width=True, hide_index=True)
warn=[]
if s["mode"].startswith("Técnico"):
    if s["hvac_cooling_wm2"] < 30 or s["hvac_cooling_wm2"] > 200: warn.append("Frío específico fuera de rango típico (30–200 W/m²).")
    if s["hvac_heating_wm2"] < 20 or s["hvac_heating_wm2"] > 180: warn.append("Calor específico fuera de rango típico (20–180 W/m²).")
warnings_box(warn)
