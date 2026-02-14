# Predimensionamiento de instalaciones (Streamlit)

Dashboard para **predimensionar** (fase de anteproyecto) las principales instalaciones de un edificio, basado en el documento **“LAS INSTALACIONES A PALMOS – Manual de Predimensionado”**.

Incluye:
- **Uso único del edificio** (no multizona por usos) + **superficie sobre/bajo rasante**.
- Definición de zonas (opcional) para repartir superficie/exposición (con **densidad → ocupación automática**).
- **Reservas de espacio** (Tablas 1 y 2).
- **Climatización** (Frío: Tablas 5 y 6; Calor: Tablas 7 y 8).
- **Ventilación** (Tabla 10) y estimación de caudales en **sistema todo-aire** (Tabla 9).
- **Electricidad** (Tablas 11 y 12) + criterio BT/MT (umbral 400 kW).
- **Agua fría y ACS** (Tablas 13 y 14, mediante mapeo de usos).
- **PCI**: cálculo de volumen de reserva a partir de caudal y tiempo.
- Exportación: **Excel** y **PDF (memoria)**.

> Nota: herramienta orientativa para fase de anteproyecto. El dimensionado definitivo requiere proyecto y normativa aplicable.

---

## Estructura

```
.
├─ app.py
├─ pages/
├─ core/
├─ examples/
├─ requirements.txt
└─ README.md
```

---

## Ejecutar en local

1) Crear entorno e instalar dependencias:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

2) Lanzar Streamlit:

```bash
streamlit run app.py
```

---

## Despliegue en Streamlit Community Cloud

1) Crea un repositorio en GitHub y sube el contenido del proyecto (incluyendo `requirements.txt`).
2) En https://streamlit.io/:
   - **New app**
   - Selecciona el repo y rama
   - **Main file path:** `app.py`
3) Deploy.

---

## Uso recomendado

1) **Datos y zonas**: rellena usos, superficies, zona climática y nivel de carga.  
   - Si indicas **Densidad (pers/m²)** se calcula automáticamente Personas.
2) **Climatización**, **Ventilación**, **Electricidad**, **Agua/ACS**, **PCI**: revisa resultados y avisos.
3) **Memoria y exportación**: descarga Excel y PDF.

---

## Licencia / Disclaimer

Herramienta de predimensionado orientativo (fase anteproyecto). No sustituye cálculo final ni verificación normativa (CTE, RITE, REBT, RIPCI, ordenanzas, etc.).


## Selector de ciudad y zona climática

En la página **1) Datos y zonas** hay un desplegable de **Ciudad** que sugiere una zona climática del CTE (capital de provincia) y permite **override** manual.

Fuente de datos:
- Informe del IDAE con tabla de correspondencias de zona climática del CTE (Apéndice B) por capital de provincia. Fecha de consulta: 2026-02-08.

Archivo:
- `data/cities_es_cte.csv`
