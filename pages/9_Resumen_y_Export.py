import streamlit as st
from datetime import date
from core.state import get_settings
from core.calcs import calc_hvac, calc_ventilation, calc_electrical, calc_pci
from core.exporters import export_excel, export_pdf
st.title("Resumen & Export")
s = get_settings()
df_hvac,_ = calc_hvac(s)
df_vent,_ = calc_ventilation(s)
df_elec,_ = calc_electrical(s)
df_pci,_ = calc_pci(s)
st.subheader("Resumen rápido")
c1,c2,c3 = st.columns(3)
c1.metric("Uso", s["use"])
c2.metric("Ciudad", s["city"])
c3.metric("Zona climática", s["ctezone"])
for df in [df_hvac, df_vent, df_elec, df_pci]:
    st.dataframe(df, use_container_width=True, hide_index=True)
sheets = {"HVAC": df_hvac, "Ventilación": df_vent, "Electricidad": df_elec, "PCI": df_pci}
meta = {
    "Fecha": str(date.today()),
    "Uso": s["use"],
    "Ciudad": s["city"],
    "Zona climática": s["ctezone"],
    "GFA sobre (m²)": f"{float(s.get('gfa_above_m2',0)):,.0f}",
    "GFA bajo (m²)": f"{float(s.get('gfa_below_m2',0)):,.0f}",
    "Plazas parking": str(int(s.get('parking_spaces',0) or 0)),
    "Modo": s.get("mode","Conceptual"),
}
st.subheader("Exportar")
st.download_button("📥 Descargar Excel", data=export_excel(sheets), file_name="predimensionamiento_resultados.xlsx")
st.download_button("📄 Descargar PDF", data=export_pdf("Memoria de predimensionamiento (anteproyecto)", meta=meta, sections=sheets), file_name="memoria_predimensionamiento.pdf")
