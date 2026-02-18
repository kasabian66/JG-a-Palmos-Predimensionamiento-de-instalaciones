import streamlit as st
from core.state import get_settings, set_settings, DEFAULTS
from core.calcs import calc_pci
from core.ui import warnings_box
st.title("5) PCI – Reserva de agua (predimensionado)")
s = get_settings()
u = DEFAULTS["uses"][s["use"]]
s["pci_auto"] = st.checkbox("Calcular caudales automáticamente por m²", value=bool(s.get("pci_auto", True)))
c1,c2 = st.columns(2)
with c1:
    s["pci_bie_hours"] = st.number_input("Tiempo de reserva BIEs (h)", min_value=0.0, step=0.1, value=float(s.get("pci_bie_hours",1.0)))
with c2:
    s["pci_spr_hours"] = st.number_input("Tiempo de reserva rociadores (h)", min_value=0.0, step=0.1, value=float(s.get("pci_spr_hours",1.5)))
if s["pci_auto"]:
    st.subheader("Ratios (L/s por 1.000 m²)")
    cA,cB = st.columns(2)
    with cA:
        s["pci_bie_lps_per_1000m2_building"] = st.number_input("BIEs – edificio", min_value=0.0, step=0.1, value=float(s.get("pci_bie_lps_per_1000m2_building",u["pci_bie_lps_per_1000m2"])))
        s["pci_bie_lps_per_1000m2_parking"] = st.number_input("BIEs – parking", min_value=0.0, step=0.1, value=float(s.get("pci_bie_lps_per_1000m2_parking",0.0)))
    with cB:
        s["pci_spr_lps_per_1000m2_building"] = st.number_input("Rociadores – edificio", min_value=0.0, step=0.5, value=float(s.get("pci_spr_lps_per_1000m2_building",u["pci_spr_lps_per_1000m2"])))
        s["pci_spr_lps_per_1000m2_parking"] = st.number_input("Rociadores – parking", min_value=0.0, step=0.5, value=float(s.get("pci_spr_lps_per_1000m2_parking",u["pci_spr_lps_per_1000m2"])))
else:
    st.subheader("Modo manual")
    cA,cB = st.columns(2)
    with cA:
        s["pci_bie_manual_lps"] = st.number_input("Caudal BIEs (L/s)", min_value=0.0, step=0.1, value=float(s.get("pci_bie_manual_lps",0.0)))
    with cB:
        s["pci_spr_manual_lps"] = st.number_input("Caudal rociadores (L/s)", min_value=0.0, step=0.1, value=float(s.get("pci_spr_manual_lps",0.0)))
set_settings(s)
df,res = calc_pci(s)
st.dataframe(df, use_container_width=True, hide_index=True)
st.metric("Reserva total (m³)", f"{res['reserve_total_m3']:.2f}")
warn=[]
if s["pci_auto"] and (s["pci_bie_lps_per_1000m2_building"]==0 and s["pci_spr_lps_per_1000m2_building"]==0): warn.append("Ratios PCI a 0: no se calculará reserva.")
warnings_box(warn)
