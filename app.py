import streamlit as st
from core.state import init_state
st.set_page_config(page_title="Predimensionamiento instalaciones (Anteproyecto)", page_icon="🏢", layout="wide")
init_state()
st.title("🏢 Predimensionamiento de instalaciones (Anteproyecto)")
st.caption("Versión completa avanzada y estable para Streamlit Cloud. Un único uso; sobre/bajo rasante; exports Excel/PDF.")
st.markdown("""**Flujo**
1) Datos del edificio
2) Climatización / Ventilación / Electricidad / PCI
3) Resumen & Export
""")
