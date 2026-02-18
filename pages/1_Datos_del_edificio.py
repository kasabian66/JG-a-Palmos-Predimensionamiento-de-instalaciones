import streamlit as st
from core.state import get_settings, set_settings, DEFAULTS, CITY_ZONE
st.title("1) Datos del edificio (uso único)")
s = get_settings()
s["mode"] = st.selectbox("Modo de cálculo", ["Conceptual","Técnico (lite)"], index=0 if s.get("mode","Conceptual")=="Conceptual" else 1)
uses = list(DEFAULTS["uses"].keys())
s["use"] = st.selectbox("Uso general del edificio", uses, index=uses.index(s.get("use", uses[0])) if s.get("use") in uses else 0)
cities = list(CITY_ZONE.keys())
s["city"] = st.selectbox("Ciudad (sugiere zona climática CTE)", cities, index=cities.index(s.get("city", cities[0])) if s.get("city") in cities else 0)
suggested = CITY_ZONE.get(s["city"], "D3")
s["zone_override"] = st.checkbox("Modificar zona climática manualmente", value=bool(s.get("zone_override", False)))
if not s["zone_override"]:
    s["ctezone"] = suggested
zones = ["A3","A4","B3","B4","C1","C2","C3","C4","D1","D2","D3","E1"]
s["ctezone"] = st.selectbox("Zona climática (CTE)", zones, index=zones.index(s.get("ctezone","D3")))
st.subheader("Superficies")
c1,c2 = st.columns(2)
with c1:
    s["gfa_above_m2"] = st.number_input("Superficie sobre rasante (m²)", min_value=0.0, step=100.0, value=float(s.get("gfa_above_m2",0.0)))
with c2:
    s["gfa_below_m2"] = st.number_input("Superficie bajo rasante (m²)", min_value=0.0, step=100.0, value=float(s.get("gfa_below_m2",0.0)))
st.metric("Superficie total (m²)", f"{(float(s['gfa_above_m2'])+float(s['gfa_below_m2'])):,.0f}")
st.subheader("Parking (bajo rasante)")
s["parking_spaces"] = st.number_input("Nº de plazas (si aplica)", min_value=0, step=1, value=int(s.get("parking_spaces",0)))
st.divider()
if st.button("Cargar valores por defecto del uso"):
    u = DEFAULTS["uses"][s["use"]]
    s["hvac_cooling_wm2"] = u["hvac_cooling_wm2"]
    s["hvac_heating_wm2"] = u["hvac_heating_wm2"]
    s["vent_above_lps_m2"] = u["vent_lps_m2"]
    s["elec_wm2"] = u["elec_wm2"]
    s["elec_diversity"] = u["elec_diversity"]
    s["elec_pf"] = u["elec_pf"]
    s["pci_bie_lps_per_1000m2_building"] = u["pci_bie_lps_per_1000m2"]
    s["pci_spr_lps_per_1000m2_building"] = u["pci_spr_lps_per_1000m2"]
    st.success("Valores cargados.")
set_settings(s)
