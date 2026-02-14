# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
from .sample_data import sample_zones_office
from .constants import ZONAS_CLIMATICAS, NIVELES_CARGA, EXPOSICION_TODO_AIRE

DEFAULT_COLUMNS = [
    "ID",
    "Nombre zona",
    "Uso",
    "Superficie (m²)",
    "Zona climática",
    "Nivel carga (B/M/A)",
    "Exposición (E/S/W, N, Interior)",
    "Densidad (pers/m²)",
    "Personas",
    "Camas",
    "Cubiertos/día",
    "Suministro complementario",
    "Frío override (W/m²)",
    "Calor override (W/m²)",
    "Ventilación override (L/s·m²)",
    "Eléctrica override (W/m²)",
    "Eléctrica comp. override (W/m²)",
    "Categoría global (Tabla 1)",
]

def init_state():
    import streamlit as st
    if "zones_df" not in st.session_state:
        st.session_state["zones_df"] = sample_zones_office()
        # añadir columnas faltantes
        for c in DEFAULT_COLUMNS:
            if c not in st.session_state["zones_df"].columns:
                st.session_state["zones_df"][c] = None

    if "settings" not in st.session_state:
        st.session_state["settings"] = {
            "oversize_frio": 1.00,
            "oversize_calor": 1.10,
            "uso_edificio": "Oficinas",
            "gfa_above_m2": 4500.0,
            "gfa_below_m2": 1000.0,
            "todo_aire_activo": False,
            "mapa_uso_tabla9": {},
            "mapa_uso_tabla13": {},
            "mapa_uso_tabla14": {},
            "instalaciones_seleccion": [],
                        "pci_mangueras_caudal_lps": 0.0,
            "pci_mangueras_tiempo_h": 1.0,
            "pci_rociadores_caudal_lps": 0.0,
            "pci_rociadores_tiempo_h": 1.5,
            "pci_extincion_gas": False,
            "pci_activo": False,
            "meta_proyecto": {"proyecto": "", "ubicacion": "", "titulo": "Memoria de Predimensionamiento"},
        }

def get_zones_df() -> pd.DataFrame:
    init_state()
    df = st.session_state["zones_df"]
    settings = st.session_state.get("settings", {})
    # Enforce "one building = one use" and "one climate zone" across all zone rows
    uso = settings.get("uso_edificio")
    zona = settings.get("zona_climatica_global")
    if uso or zona:
        df2 = df.copy()
        if uso:
            df2["Uso"] = uso
        if zona:
            df2["Zona climática"] = zona
        st.session_state["zones_df"] = df2
        return df2
    return df

def set_zones_df(df: pd.DataFrame):
    import streamlit as st
    st.session_state["zones_df"] = df

def get_settings() -> dict:
    init_state()
    return st.session_state["settings"]

def set_settings(settings: dict) -> None:
    import streamlit as st
    init_state()
    st.session_state["settings"] = settings
