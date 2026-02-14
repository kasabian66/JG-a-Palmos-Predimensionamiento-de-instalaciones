# -*- coding: utf-8 -*-
import streamlit as st
import datetime

from core.state import init_state, get_zones_df, get_settings
from core.calculations import (
    calc_climatizacion, calc_ventilacion_y_todo_aire, calc_electricidad,
    calc_agua_y_acs, calc_reservas_espacios, calc_pci
)
from core.exporters import export_excel, export_pdf_memoria

init_state()
st.title("9) Memoria y exportación")

zones_df = get_zones_df()
settings = get_settings()

st.subheader("Datos de portada")
meta = settings.get("meta_proyecto", {})
meta["proyecto"] = st.text_input("Proyecto / Edificio", value=meta.get("proyecto",""))
meta["ubicacion"] = st.text_input("Ubicación", value=meta.get("ubicacion",""))
meta["titulo"] = st.text_input("Título PDF", value=meta.get("titulo","Memoria de Predimensionamiento"))
meta["fecha"] = datetime.date.today().isoformat()
settings["meta_proyecto"] = meta

st.divider()
st.subheader("Generar resultados")

# Calcular todo
df_clima, w_clima, tot_clima = calc_climatizacion(zones_df, settings)
df_vent, w_vent, tot_vent = calc_ventilacion_y_todo_aire(zones_df, settings)
df_ele, w_ele, tot_ele = calc_electricidad(zones_df, settings)
df_agua, w_agua, tot_agua = calc_agua_y_acs(zones_df, settings)
df_esp, w_esp, tot_esp = calc_reservas_espacios(zones_df, settings)
df_pci, w_pci, tot_pci = calc_pci(settings)

all_w = w_clima + w_vent + w_ele + w_agua + w_esp + w_pci
if all_w:
    st.warning(f"Avisos totales: {len(all_w)}. Revisa antes de emitir memoria.")

results = {
    "Zonas": zones_df,
    "Climatizacion": df_clima,
    "Ventilacion_TodoAire": df_vent,
    "Electricidad": df_ele,
    "Agua_ACS": df_agua,
    "Espacios": df_esp,
    "PCI": df_pci,
    "Totales_clima": tot_clima,
    "Totales_vent": tot_vent,
    "Totales_ele": tot_ele,
    "Totales_agua": tot_agua,
    "Totales_esp": tot_esp,
    "Totales_pci": tot_pci,
}

col1, col2 = st.columns(2)

with col1:
    xbytes = export_excel(results)
    st.download_button(
        "⬇️ Descargar Excel (resultados)",
        data=xbytes,
        file_name="predimensionamiento_resultados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with col2:
    pdf_bytes = export_pdf_memoria(
        meta=meta,
        tables={
            "Zonas": zones_df,
            "Climatización": df_clima,
            "Ventilación/Todo-aire": df_vent,
            "Electricidad": df_ele,
            "Agua/ACS": df_agua,
            "Espacios": df_esp,
            "PCI": df_pci,
        },
        totals={
            "Climatización": tot_clima,
            "Ventilación/Todo-aire": tot_vent,
            "Electricidad": tot_ele,
            "Agua/ACS": tot_agua,
            "Espacios": tot_esp,
            "PCI": tot_pci,
        }
    )
    st.download_button(
        "⬇️ Descargar PDF (memoria)",
        data=pdf_bytes,
        file_name="memoria_predimensionamiento.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.divider()
st.subheader("Avisos")
if all_w:
    from collections import defaultdict
    groups = defaultdict(list)
    for w in all_w:
        groups[(w.module, w.message)].append(w.zone)

    for (mod, msg), zones in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1])):
        zuniq = [z for z in sorted(set(zones)) if str(z).strip() != ""]
        if len(zuniq) <= 1:
            ztxt = zuniq[0] if zuniq else "(global)"
            st.warning(f"[{mod}] {ztxt}: {msg}")
        else:
            shown = ", ".join(zuniq[:3])
            more = "" if len(zuniq) <= 3 else f" (+{len(zuniq)-3} más)"
            st.warning(f"[{mod}] {shown}{more}: {msg}")
else:
    st.success("Sin avisos relevantes.")
