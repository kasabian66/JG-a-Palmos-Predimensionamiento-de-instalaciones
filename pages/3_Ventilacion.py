import streamlit as st
from core.state import get_settings, set_settings, DEFAULTS
from core.calcs import calc_ventilation
from core.ui import warnings_box
st.title("3) Ventilación (sobre rasante + parking separado)")
s = get_settings()
u = DEFAULTS["uses"][s["use"]]
s["vent_above_lps_m2"] = st.number_input("Ventilación específica sobre rasante (L/s·m²)", min_value=0.0, step=0.05, value=float(s.get("vent_above_lps_m2",u["vent_lps_m2"])))
st.subheader("Parking (CTE) — aportación vs extracción")
modes = ["Salubridad (CTE DB-HS 3)","Control de humos (CTE DB-SI 3)"]
s["parking_mode"] = st.selectbox("Modo parking", modes, index=modes.index(s.get("parking_mode",modes[0])) if s.get("parking_mode") in modes else 0)
if s["parking_mode"].startswith("Control"):
    supply_def, extract_def = 120.0, 150.0
else:
    supply_def, extract_def = 120.0, 120.0
s["parking_override_cte"] = st.checkbox("Modificar valores CTE manualmente", value=bool(s.get("parking_override_cte", False)))
if not s["parking_override_cte"]:
    s["parking_supply_lps_per_space"] = supply_def
    s["parking_extract_lps_per_space"] = extract_def
c1,c2 = st.columns(2)
with c1:
    s["parking_supply_lps_per_space"] = st.number_input("Aportación (L/s·plaza)", min_value=0.0, step=10.0, value=float(s.get("parking_supply_lps_per_space",supply_def)), disabled=(not s["parking_override_cte"]))
with c2:
    s["parking_extract_lps_per_space"] = st.number_input("Extracción (L/s·plaza)", min_value=0.0, step=10.0, value=float(s.get("parking_extract_lps_per_space",extract_def)), disabled=(not s["parking_override_cte"]))
set_settings(s)
df,_ = calc_ventilation(s)
st.dataframe(df, use_container_width=True, hide_index=True)
warn=[]
if s["parking_spaces"] > 0 and float(s.get("gfa_below_m2",0) or 0) == 0: warn.append("Has indicado plazas de parking pero la superficie bajo rasante es 0 m².")
warnings_box(warn)
