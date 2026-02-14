import streamlit as st

from core.state import get_settings, set_settings
from core.calculations import calc_pci
from core.ui import render_warnings


st.title("PCI – Reserva de agua (según JG 'Instalaciones a palmos')")
st.caption("Módulo simplificado: caudales automáticos por m² (edificio + aparcamiento) con ratios habituales editables. Permite ajuste manual.")

settings = get_settings()
settings["pci_activo"] = True

gfa_above = float(settings.get("gfa_above_m2", 0) or 0)
gfa_below = float(settings.get("gfa_below_m2", 0) or 0)

cA, cB, cC = st.columns(3)
cA.metric("GFA sobre rasante (m²)", f"{gfa_above:,.0f}")
cB.metric("GFA bajo rasante (m²)", f"{gfa_below:,.0f}")
cC.metric("GFA total (m²)", f"{(gfa_above+gfa_below):,.0f}")

st.subheader("Caudales de diseño")
settings["pci_auto"] = st.checkbox("Calcular caudales automáticamente por m² (recomendado)", value=bool(settings.get("pci_auto", True)))

if settings["pci_auto"]:
    st.markdown("**Ratios (habituales) por superficie**  _(L/s por cada 1.000 m²)_")
    r1, r2 = st.columns(2)
    with r1:
        settings["pci_ratio_bie_building_lps_per_1000m2"] = st.number_input(
            "BIEs – edificio (L/s·1000m²)", min_value=0.0, step=0.1,
            value=float(settings.get("pci_ratio_bie_building_lps_per_1000m2", 3.33)),
        )
        settings["pci_ratio_bie_aparcamiento_lps_per_1000m2"] = st.number_input(
            "BIEs – aparcamiento (L/s·1000m²)", min_value=0.0, step=0.1,
            value=float(settings.get("pci_ratio_bie_aparcamiento_lps_per_1000m2", 0.0)),
        )
    with r2:
        settings["pci_ratio_spr_building_lps_per_1000m2"] = st.number_input(
            "Rociadores – edificio (L/s·1000m²)", min_value=0.0, step=0.5,
            value=float(settings.get("pci_ratio_spr_building_lps_per_1000m2", 25.0)),
        )
        settings["pci_ratio_spr_aparcamiento_lps_per_1000m2"] = st.number_input(
            "Rociadores – aparcamiento (L/s·1000m²)", min_value=0.0, step=0.5,
            value=float(settings.get("pci_ratio_spr_aparcamiento_lps_per_1000m2", 25.0)),
        )
else:
    st.markdown("**Entrada manual de caudales**")
    c1, c2 = st.columns(2)
    with c1:
        settings["pci_mangueras_caudal_lps"] = st.number_input(
            "Caudal de diseño BIEs (L/s) – manual",
            min_value=0.0, step=0.1,
            value=float(settings.get("pci_mangueras_caudal_lps", 0.0)),
        )
    with c2:
        settings["pci_rociadores_caudal_lps"] = st.number_input(
            "Caudal de diseño rociadores (L/s) – manual",
            min_value=0.0, step=0.1,
            value=float(settings.get("pci_rociadores_caudal_lps", 0.0)),
        )

st.subheader("Tiempos de reserva")
t1, t2 = st.columns(2)
with t1:
    settings["pci_mangueras_tiempo_h"] = st.number_input(
        "Tiempo de reserva BIEs (h)", min_value=0.0, step=0.1,
        value=float(settings.get("pci_mangueras_tiempo_h", 1.0)),
    )
with t2:
    settings["pci_rociadores_tiempo_h"] = st.number_input(
        "Tiempo de reserva rociadores (h)", min_value=0.0, step=0.1,
        value=float(settings.get("pci_rociadores_tiempo_h", 1.5)),
    )

settings["pci_extincion_gas"] = st.checkbox("Considerar extinción automática por gas (solo informativo)", value=bool(settings.get("pci_extincion_gas", False)))

set_settings(settings)

df, warnings, totals = calc_pci(settings)

st.subheader("Resultados")
st.metric("Reserva total estimada (m³)", f"{totals['pci_reserva_total_m3']:.1f}")
cR1, cR2 = st.columns(2)
cR1.metric("Caudal BIEs (L/s)", f"{totals.get('pci_bies_caudal_lps', 0):.2f}")
cR2.metric("Caudal rociadores (L/s)", f"{totals.get('pci_rociadores_caudal_lps', 0):.2f}")

st.dataframe(df, use_container_width=True, hide_index=True)

render_warnings(warnings)
