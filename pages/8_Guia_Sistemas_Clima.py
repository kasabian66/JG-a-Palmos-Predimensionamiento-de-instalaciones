# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

from core.state import init_state
from core.constants import TABLA_16_SISTEMAS_CLIMA

init_state()
st.title("8) Guía (sistemas de climatización)")

st.write("Matriz orientativa de aplicación de sistemas de climatización (Tabla 16 del documento).")

df = pd.DataFrame(TABLA_16_SISTEMAS_CLIMA).T
df = df.reset_index().rename(columns={"index":"Aplicación"})
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Lista de comprobación (extracto Tabla 3)")

st.markdown("""
**Climatización**
- Producción de frío: grupos de enfriamiento  
- Evacuación de calor: torres / condensadores por aire / depósitos de inercia  
- Producción de calor: calderas / depósito combustible / acometida gas / chimeneas / tomas aire ventilación  
- Tratamiento de aire: salas de climatizadores/ventiladores / tomas aire exterior / descargas expulsión / trazado general de conductos  
- Distribución de fluidos: patios de instalaciones  

**Instalaciones eléctricas**
- Acometida y contadores  
- Estación transformadora  
- Cuadro General de Baja Tensión  
- Paneles fotovoltaicos (cubierta/fachada)  
- Grupos electrógenos (depósito combustible, ventilación, escape)  
- SAI (sala de baterías, ventilación)
""")
