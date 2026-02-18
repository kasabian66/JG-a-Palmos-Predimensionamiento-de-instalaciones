import streamlit as st
from core.state import get_settings, set_settings, DEFAULTS
from core.calcs import calc_electrical
from core.ui import warnings_box
st.title("4) Electricidad BT (predimensionado)")
s = get_settings()
u = DEFAULTS["uses"][s["use"]]
c1,c2,c3 = st.columns(3)
with c1:
    s["elec_wm2"] = st.number_input("Potencia instalada específica (W/m²)", min_value=0.0, step=5.0, value=float(s.get("elec_wm2",u["elec_wm2"])))
with c2:
    s["elec_diversity"] = st.number_input("Factor de simultaneidad", min_value=0.1, max_value=1.0, step=0.05, value=float(s.get("elec_diversity",u["elec_diversity"])))
with c3:
    s["elec_pf"] = st.number_input("cosφ (factor de potencia)", min_value=0.5, max_value=1.0, step=0.01, value=float(s.get("elec_pf",u["elec_pf"])))
set_settings(s)
df,_ = calc_electrical(s)
st.dataframe(df, use_container_width=True, hide_index=True)
warn=[]
if s["mode"].startswith("Técnico") and s["elec_wm2"] > 200: warn.append("W/m² eléctrico muy alto (>200).")
warnings_box(warn)
