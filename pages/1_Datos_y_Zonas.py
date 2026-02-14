# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from pathlib import Path

from core.state import init_state, get_zones_df, set_zones_df, get_settings
from core.catalog import all_usos
from core.constants import ZONAS_CLIMATICAS, NIVELES_CARGA, EXPOSICION_TODO_AIRE, TABLA_1_ESPACIO_GLOBAL
from core.sample_data import sample_zones_office

init_state()
st.title("1) Datos del edificio (uso único) y zonas")

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
settings = get_settings()

# -----------------------------
# Ciudad -> zona climática CTE sugerida
# -----------------------------
try:
    cities_df = pd.read_csv(DATA_DIR / "cities_es_cte.csv")
    city_names = cities_df["city"].astype(str).tolist()
except Exception:
    cities_df = pd.DataFrame(columns=["city", "climate_zone_cte"])
    city_names = []

with st.expander("Ubicación: ciudad y zona climática (valor único para TODO el edificio)", expanded=True):
    if city_names:
        default_city = settings.get("city", city_names[0])
        if default_city not in city_names:
            default_city = city_names[0]
        city = st.selectbox("Ciudad", options=city_names, index=city_names.index(default_city))
        suggested = str(cities_df.loc[cities_df["city"] == city, "climate_zone_cte"].iloc[0])
    else:
        city = st.text_input("Ciudad", value=str(settings.get("city", "")))
        suggested = ""

    st.caption("La ciudad sugiere una zona climática (capital de provincia) basada en el Apéndice B del CTE. Verifica la localidad exacta si aplica.")
    default_zone = suggested if suggested in ZONAS_CLIMATICAS else settings.get("zona_climatica_global", ZONAS_CLIMATICAS[0])
    zone_global = st.selectbox(
        "Zona climática (auto / override)",
        options=ZONAS_CLIMATICAS,
        index=ZONAS_CLIMATICAS.index(default_zone) if default_zone in ZONAS_CLIMATICAS else 0,
    )

    settings["city"] = city
    settings["zona_climatica_global"] = zone_global

# -----------------------------
# Uso + superficies sobre/bajo rasante
# -----------------------------
with st.expander("Definición del edificio (1 uso general + superficies sobre/bajo rasante)", expanded=True):
    usos = all_usos()
    default_use = settings.get("uso_edificio", "Oficinas")
    if default_use not in usos:
        default_use = usos[0] if usos else "Oficinas"
    uso_edificio = st.selectbox("Uso general del edificio (aplica a TODAS las zonas)", options=usos, index=usos.index(default_use) if default_use in usos else 0)
    settings["uso_edificio"] = uso_edificio

    c1, c2, c3 = st.columns(3)
    with c1:
        gfa_above = st.number_input("Superficie sobre rasante (m²)", min_value=0.0, step=10.0, value=float(settings.get("gfa_above_m2", 0.0)))
    with c2:
        gfa_below = st.number_input("Superficie bajo rasante (m²)", min_value=0.0, step=10.0, value=float(settings.get("gfa_below_m2", 0.0)))
    with c3:
        st.metric("Superficie total (m²)", f"{(gfa_above + gfa_below):.0f}")

    settings["gfa_above_m2"] = float(gfa_above)
    settings["gfa_below_m2"] = float(gfa_below)

    st.caption("Puedes mantener el modelo con 2 zonas (sobre/bajo) o añadir más zonas (exposición/nivel de carga). En cualquier caso, el uso y la zona climática son únicos para todo el edificio.")

# -----------------------------
# Tabla de zonas (multizona permitida, pero con uso y zona climática bloqueados)
# -----------------------------
st.write("Define las **zonas/áreas** del edificio (detalle opcional).")
st.caption("La app fuerza: **1 edificio = 1 uso** y **1 zona climática**. Las filas de zona solo sirven para repartir superficie, exposición y nivel de carga.")

zones_df = get_zones_df().copy()

colA, colB, colC = st.columns([1, 1, 2])
with colA:
    if st.button("Cargar ejemplo (Oficinas – 2 zonas)", use_container_width=True):
        zones_df = sample_zones_office()
with colB:
    uploaded = st.file_uploader("Importar CSV (zonas)", type=["csv"])
with colC:
    st.caption("Consejo: si indicas **Densidad (pers/m²)**, se calcula automáticamente Personas = densidad·superficie.")

if uploaded is not None:
    try:
        df_in = pd.read_csv(uploaded)
        zones_df = df_in
        st.success("CSV importado.")
    except Exception as e:
        st.error(f"No se pudo leer el CSV: {e}")

required_cols = [
    "ID", "Nombre zona", "Uso", "Superficie (m²)", "Zona climática", "Nivel carga (B/M/A)",
    "Exposición (E/S/W, N, Interior)", "Densidad (pers/m²)", "Personas", "Camas", "Cubiertos/día",
    "Suministro complementario",
    "Frío override (W/m²)", "Calor override (W/m²)", "Ventilación override (L/s·m²)",
    "Eléctrica override (W/m²)", "Eléctrica comp. override (W/m²)",
    "Categoría global (Tabla 1)",
]
for c in required_cols:
    if c not in zones_df.columns:
        zones_df[c] = None

# FORZAR uso único + zona climática única
zones_df["Uso"] = settings.get("uso_edificio", "Oficinas")
zones_df["Zona climática"] = settings.get("zona_climatica_global", ZONAS_CLIMATICAS[0])

st.divider()
st.subheader("Plantillas rápidas (opcional)")

t1, t2 = st.columns(2)
if t1.button("Zonas = 2 filas (sobre rasante / bajo rasante)", use_container_width=True):
    zones_df = pd.DataFrame([
        {"ID": 1, "Nombre zona": "Sobre rasante", "Superficie (m²)": float(settings.get("gfa_above_m2", 0.0)),
         "Nivel carga (B/M/A)": "M", "Exposición (E/S/W, N, Interior)": "Interior", "Densidad (pers/m²)": 0.08,
         "Suministro complementario": False},
        {"ID": 2, "Nombre zona": "Bajo rasante", "Superficie (m²)": float(settings.get("gfa_below_m2", 0.0)),
         "Nivel carga (B/M/A)": "B", "Exposición (E/S/W, N, Interior)": "Interior", "Densidad (pers/m²)": 0.02,
         "Suministro complementario": False},
    ])
    for c in required_cols:
        if c not in zones_df.columns:
            zones_df[c] = None
    zones_df["Uso"] = settings.get("uso_edificio", "Oficinas")
    zones_df["Zona climática"] = settings.get("zona_climatica_global", ZONAS_CLIMATICAS[0])
    st.success("Plantilla aplicada.")

if t2.button("Zonas = 1 fila (edificio completo)", use_container_width=True):
    total_gfa = float(settings.get("gfa_above_m2", 0.0)) + float(settings.get("gfa_below_m2", 0.0))
    zones_df = pd.DataFrame([
        {"ID": 1, "Nombre zona": "Edificio completo", "Superficie (m²)": total_gfa,
         "Nivel carga (B/M/A)": "M", "Exposición (E/S/W, N, Interior)": "Interior", "Densidad (pers/m²)": 0.08,
         "Suministro complementario": False},
    ])
    for c in required_cols:
        if c not in zones_df.columns:
            zones_df[c] = None
    zones_df["Uso"] = settings.get("uso_edificio", "Oficinas")
    zones_df["Zona climática"] = settings.get("zona_climatica_global", ZONAS_CLIMATICAS[0])
    st.success("Plantilla aplicada.")

st.divider()
st.subheader("Tabla de zonas")

categorias = list(TABLA_1_ESPACIO_GLOBAL.keys())

edited = st.data_editor(
    zones_df[required_cols],
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    disabled=["Uso", "Zona climática"],  # bloquea uso y zona climática por edificio
    column_config={
        "ID": st.column_config.NumberColumn("ID", min_value=1, step=1, required=True),
        "Nombre zona": st.column_config.TextColumn("Nombre zona"),
        "Uso": st.column_config.TextColumn("Uso (bloqueado)"),
        "Superficie (m²)": st.column_config.NumberColumn("Superficie (m²)", min_value=0.0, step=1.0, required=True, format="%.2f"),
        "Zona climática": st.column_config.TextColumn("Zona climática (bloqueada)"),
        "Nivel carga (B/M/A)": st.column_config.SelectboxColumn("Nivel carga (B/M/A)", options=NIVELES_CARGA, required=True),
        "Exposición (E/S/W, N, Interior)": st.column_config.SelectboxColumn("Exposición (E/S/W, N, Interior)", options=EXPOSICION_TODO_AIRE, required=True),
        "Densidad (pers/m²)": st.column_config.NumberColumn("Densidad (pers/m²)", min_value=0.0, step=0.01, format="%.3f"),
        "Personas": st.column_config.NumberColumn("Personas (override)", min_value=0.0, step=1.0, format="%.0f"),
        "Camas": st.column_config.NumberColumn("Camas", min_value=0.0, step=1.0, format="%.0f"),
        "Cubiertos/día": st.column_config.NumberColumn("Cubiertos/día", min_value=0.0, step=1.0, format="%.0f"),
        "Suministro complementario": st.column_config.CheckboxColumn("Suministro complementario"),
        "Frío override (W/m²)": st.column_config.NumberColumn("Frío override (W/m²)", min_value=0.0, step=1.0),
        "Calor override (W/m²)": st.column_config.NumberColumn("Calor override (W/m²)", min_value=0.0, step=1.0),
        "Ventilación override (L/s·m²)": st.column_config.NumberColumn("Ventilación override (L/s·m²)", min_value=0.0, step=0.01),
        "Eléctrica override (W/m²)": st.column_config.NumberColumn("Eléctrica override (W/m²)", min_value=0.0, step=1.0),
        "Eléctrica comp. override (W/m²)": st.column_config.NumberColumn("Eléctrica comp. override (W/m²)", min_value=0.0, step=1.0),
        "Categoría global (Tabla 1)": st.column_config.SelectboxColumn("Categoría global (Tabla 1)", options=categorias),
    },
)

# reforzar tras edición
edited["Uso"] = settings.get("uso_edificio", "Oficinas")
edited["Zona climática"] = settings.get("zona_climatica_global", ZONAS_CLIMATICAS[0])

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Guardar cambios", type="primary", use_container_width=True):
        set_zones_df(edited)
        st.success("Zonas guardadas.")
with col2:
    csv_bytes = edited.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv_bytes, file_name="zonas.csv", mime="text/csv", use_container_width=True)

st.divider()
st.subheader("Validaciones rápidas")

errs = []
if pd.to_numeric(edited["Superficie (m²)"], errors="coerce").fillna(0).le(0).any():
    errs.append("Hay filas con superficie 0 o no válida.")

total_area = float(pd.to_numeric(edited["Superficie (m²)"], errors="coerce").fillna(0).sum())
target_total = float(settings.get("gfa_above_m2", 0.0)) + float(settings.get("gfa_below_m2", 0.0))
if target_total > 0 and abs(total_area - target_total) / max(target_total, 1.0) > 0.05:
    errs.append(f"La suma de zonas ({total_area:.0f} m²) difiere de la superficie total ({target_total:.0f} m²) en más de un 5%.")

if errs:
    for e in errs:
        st.warning(e)
else:
    st.success("OK: tabla coherente para cálculo.")
