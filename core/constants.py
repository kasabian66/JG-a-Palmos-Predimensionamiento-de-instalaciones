# -*- coding: utf-8 -*-
"""
Tablas y criterios extraídos del documento:
"LAS INSTALACIONES A PALMOS - Manual de Predimensionado"
(archivo: JG5_Libro_Instalaciones_a_palmos.pdf)

Nota:
- Los valores están codificados tal cual aparecen en las Tablas del documento.
- Algunas tablas del PDF incluyen ambigüedades de maquetación (p.ej. Tabla 8 repite 'D1'
  en dos filas). En esos casos la app aplica criterio conservador y avisa.
"""

from __future__ import annotations

# -----------------------------
# Catálogos
# -----------------------------
NIVELES_CARGA = ["B", "M", "A"]
EXPOSICION_TODO_AIRE = ["E/S/W", "N", "Interior"]

ZONAS_CLIMATICAS = [
    "A4","B4","C4",
    "C2","D2",
    "A3","B3","C3","D3",
    "C1","D1","E1",
]

# -----------------------------
# Tabla 1: Asignación global espacios
# (PDF p.34 aprox. / pno=33)
# -----------------------------
TABLA_1_ESPACIO_GLOBAL = {
    "Industrial (asimilable)": (3.0, 6.0),
    "Administrativo/Comercial/Residencial": (6.0, 10.0),
    "Alta tecnología (hospital, CPD, laboratorios)": (15.0, 30.0),
}

# Mapeo orientativo uso->categoría global (editable en UI)
USO_A_CATEGORIA_GLOBAL = {
    # alta tecnología
    "Hospitales - Hospitalización": "Alta tecnología (hospital, CPD, laboratorios)",
    "Hospitales - General (excepto quirófanos)": "Alta tecnología (hospital, CPD, laboratorios)",
    "Laboratorios": "Alta tecnología (hospital, CPD, laboratorios)",
    "CPD / Data Center": "Alta tecnología (hospital, CPD, laboratorios)",

    # administrativo/comercial/residencial
    "Oficinas": "Administrativo/Comercial/Residencial",
    "Edificios bancarios": "Administrativo/Comercial/Residencial",
    "Comercios - Galerías comerciales": "Administrativo/Comercial/Residencial",
    "Comercios - Grandes almacenes": "Administrativo/Comercial/Residencial",
    "Comercios - Supermercados": "Administrativo/Comercial/Residencial",
    "Cafeterías y restaurantes (general)": "Administrativo/Comercial/Residencial",
    "Hoteles": "Administrativo/Comercial/Residencial",
    "Residencial - Viviendas": "Administrativo/Comercial/Residencial",
    "Residencial - General": "Administrativo/Comercial/Residencial",
    "Museos": "Administrativo/Comercial/Residencial",
    "Bibliotecas": "Administrativo/Comercial/Residencial",
    "Auditorios": "Administrativo/Comercial/Residencial",
    "Teatros": "Administrativo/Comercial/Residencial",
    "Salones de actos": "Administrativo/Comercial/Residencial",
    "Salas de fiesta / Recintos feriales": "Administrativo/Comercial/Residencial",
    "Enseñanza (aularios)": "Administrativo/Comercial/Residencial",
    "Archivos": "Administrativo/Comercial/Residencial",

    # industrial (placeholder)
    "Industrial": "Industrial (asimilable)",
}

# -----------------------------
# Tabla 2: Asignación espacios por instalación
# (PDF p.34 aprox. / pno=33)
# -----------------------------
TABLA_2_ESPACIO_POR_INSTALACION = {
    # climatización
    "Producción de frío": (1.0, 2.0),
    "Producción de calor": (0.8, 1.8),
    "Torres enfriamiento": (0.3, 1.5),
    "Almacenamiento combustible (gasóleo)": (1.0, 2.0),
    "Tratamiento aire - Caudal constante (baja velocidad)": (4.0, 6.0),
    "Tratamiento aire - Caudal variable": (3.0, 4.5),
    "Sistema fancoils": (1.5, 2.5),
    "Sistema inducción": (1.0, 3.0),
    "Bombas de calor en anillo de agua": (1.5, 2.0),

    # electricidad
    "Electricidad general (sin GE/SAI)": (0.5, 1.5),
    "Sala máquinas ascensores": (0.2, 0.5),
}

# -----------------------------
# Tabla 5: Carga específica refrigeración estándar (W/m²)
# (PDF p.50 aprox. / pno=49)
# -----------------------------
TABLA_5_FRIO_W_M2 = {
    "Archivos": {"B": 65, "M": 75, "A": 95},
    "Auditorios": {"B": 245, "M": 255, "A": 265},
    "Bibliotecas": {"B": 135, "M": 145, "A": 155},
    "Cafeterías y restaurantes (general)": {"B": 150, "M": 160, "A": 170},
    "Comercios - Galerías comerciales": {"B": 135, "M": 150, "A": 145},
    "Comercios - Grandes almacenes": {"B": 160, "M": 155, "A": 170},
    "Enseñanza (aularios)": {"B": 195, "M": 205, "A": 215},
    "Hospitales - Hospitalización": {"B": 105, "M": 85, "A": 115},
    "Hospitales - General (excepto quirófanos)": {"B": 95, "M": 125, "A": 105},
    "Hoteles": {"B": 85, "M": 95, "A": 105},
    "Museos": {"B": 135, "M": 145, "A": 155},
    "Oficinas": {"B": 90, "M": 100, "A": 110},
    "Teatros": {"B": 245, "M": 255, "A": 265},
}

# Tabla 6: Factor corrección frío por zona climática (PDF p.50 / pno=49)
TABLA_6_FACTOR_FRIO = {
    "A4": 1.15, "B4": 1.15, "C4": 1.15,
    "C2": 1.00, "D2": 1.00,
    "A3": 0.95, "B3": 0.95, "C3": 0.95, "D3": 0.95,
    "C1": 0.80, "D1": 0.80, "E1": 0.80,
}

# -----------------------------
# Tabla 7: Carga específica calefacción estándar (W/m²)
# Tabla 8: Factor corrección calefacción por zona climática
# (PDF p.52 aprox. / pno=51)
# -----------------------------
TABLA_7_CALOR_W_M2 = {
    "Archivos": {"B": 25, "M": 30, "A": 45},
    "Auditorios": {"B": 190, "M": 190, "A": 195},
    "Bibliotecas": {"B": 75, "M": 80, "A": 95},
    "Cafeterías y restaurantes (general)": {"B": 95, "M": 100, "A": 110},
    "Comercios - Galerías comerciales": {"B": 55, "M": 55, "A": 60},
    "Comercios - Grandes almacenes": {"B": 60, "M": 75, "A": 75},
    "Enseñanza (aularios)": {"B": 150, "M": 150, "A": 175},
    "Hospitales - Hospitalización": {"B": 70, "M": 70, "A": 75},
    "Hospitales - General (excepto quirófanos)": {"B": 75, "M": 90, "A": 90},
    "Hoteles": {"B": 50, "M": 55, "A": 60},
    "Museos": {"B": 90, "M": 95, "A": 105},
    "Oficinas": {"B": 45, "M": 50, "A": 60},
    "Teatros": {"B": 190, "M": 190, "A": 195},
}

# Tabla 8 tal como se extrae del texto.
# Aviso: 'D1' aparece en dos filas en el PDF (probable errata).
TABLA_8_FACTOR_CALOR_RANGOS = [
    (["A3", "A4", "B3", "B4", "C1"], 1.00),
    (["C2", "C4"], 1.20),
    (["C3", "D1", "D3"], 1.30),
    (["D2", "E1"], 1.40),
]
# -----------------------------
# Tabla 9: Caudal de aire (l/s·m²) en sistemas todo-aire por tipología y zona
# (PDF p.56 aprox. / pno=55)
# -----------------------------
TABLA_9_TODO_AIRE_LS_M2 = {
    "Auditorios / Teatros": {
        "E/S/W": {"B": None, "M": None, "A": None},
        "N": {"B": None, "M": None, "A": None},
        "Interior": {"B": 2.0, "M": 3.0, "A": 5.0},
    },
    "Enseñanza (aularios)": {
        "E/S/W": {"B": 5.0, "M": 6.0, "A": 7.0},
        "N": {"B": 2.5, "M": 3.5, "A": 7.0},
        "Interior": {"B": 2.0, "M": 2.5, "A": 3.0},
    },
    "Grandes almacenes - Planta baja": {
        "E/S/W": {"B": None, "M": None, "A": None},
        "N": {"B": None, "M": None, "A": None},
        "Interior": {"B": 2.0, "M": 2.5, "A": 4.0},
    },
    "Grandes almacenes - Pisos superiores": {
        "E/S/W": {"B": None, "M": None, "A": None},
        "N": {"B": None, "M": None, "A": None},
        "Interior": {"B": 2.0, "M": 2.5, "A": 4.0},
    },
    "Hospitales - Hospitalización": {
        "E/S/W": {"B": 5.5, "M": 6.0, "A": 7.0},
        "N": {"B": 5.5, "M": 6.0, "A": 7.0},
        "Interior": {"B": None, "M": None, "A": None},
    },
    "Hospitales - General (excepto quirófanos)": {
        "E/S/W": {"B": 5.0, "M": 5.5, "A": 6.0},
        "N": {"B": 3.0, "M": 3.5, "A": 4.0},
        "Interior": {"B": 2.0, "M": 2.0, "A": 2.5},
    },
    "Hoteles (habitaciones)": {
        "E/S/W": {"B": 5.0, "M": 5.5, "A": 6.0},
        "N": {"B": 3.0, "M": 3.5, "A": 4.0},
        "Interior": {"B": None, "M": None, "A": None},
    },
    "Museos / Bibliotecas": {
        "E/S/W": {"B": 5.0, "M": 6.0, "A": 7.0},
        "N": {"B": 3.0, "M": 3.0, "A": 4.0},
        "Interior": {"B": 2.0, "M": 2.5, "A": 3.0},
    },
    "Oficinas - Espacio abierto": {
        "E/S/W": {"B": None, "M": None, "A": None},
        "N": {"B": None, "M": None, "A": None},
        "Interior": {"B": 2.0, "M": 2.5, "A": 3.0},
    },
    "Oficinas - Despachos": {
        "E/S/W": {"B": 5.0, "M": 5.5, "A": 6.0},
        "N": {"B": 3.0, "M": 3.5, "A": 4.0},
        "Interior": {"B": None, "M": None, "A": None},
    },
    "Restaurantes / Cafeterías - Grandes": {
        "E/S/W": {"B": 9.0, "M": 10.0, "A": 13.0},
        "N": {"B": 5.5, "M": 6.0, "A": 7.0},
        "Interior": {"B": 2.0, "M": 2.0, "A": 2.5},
    },
    "Restaurantes / Cafeterías - Medianos": {
        "E/S/W": {"B": 8.0, "M": 9.0, "A": 13.0},
        "N": {"B": 3.0, "M": 3.5, "A": 4.5},
        "Interior": {"B": 2.0, "M": 2.0, "A": 2.5},
    },
    "Comercios - Galerías comerciales": {
        "E/S/W": {"B": 5.0, "M": 5.5, "A": 6.0},
        "N": {"B": 3.0, "M": 3.5, "A": 4.0},
        "Interior": {"B": 3.0, "M": 3.5, "A": 4.0},
    },
}

# -----------------------------
# Tabla 10: Ventilación (aire exterior) L/s·m²
# (PDF p.58 aprox. / pno=57)
# -----------------------------
TABLA_10_VENTILACION_LS_M2 = {
    "Archivos": 0.28,
    "Auditorios": 5.33,
    "Bibliotecas": 1.25,
    "Cafeterías y restaurantes (general)": 5.33,
    "Comercios - Galerías comerciales": 1.60,
    "Comercios - Grandes almacenes": 1.60,
    "Comercios - Supermercados": 1.60,
    "Edificios bancarios": 1.25,
    "Enseñanza (aularios)": 6.00,
    "Establecimientos deportivos con público": 4.00,
    "Hospitales - General (excepto quirófanos)": 2.70,
    "Hoteles": 0.80,
    "Laboratorios": 3.00,
    "Museos": 4.00,
    "Oficinas": 1.25,  # en tabla aparece igual para baja/media/alta carga
    "Salones de actos": 8.00,
    "Salas de fiesta / Recintos feriales": 4.00,
}

# -----------------------------
# Tabla 11: Potencia eléctrica específica W/m² (suministro normal)
# (PDF p.60 aprox. / pno=59)
# -----------------------------
TABLA_11_ELECTRICA_W_M2 = {
    "Archivos": 60,
    "Auditorios": 215,
    "Bibliotecas": 95,
    "Cafeterías y restaurantes (general)": 160,
    "Comercios - Galerías comerciales": 150,
    "Comercios - Grandes almacenes": 125,
    "Enseñanza (aularios)": 130,
    "Hospitales - Hospitalización": 75,
    "Hospitales - General (excepto quirófanos)": 70,
    "Hoteles": 75,
    "Museos": 100,
    "Oficinas": 100,
    "Salones de actos": 155,
    "Salas de fiesta / Recintos feriales": 215,
}

# -----------------------------
# Tabla 12: Potencia eléctrica específica suministro complementario W/m²
# (PDF p.61 aprox. / pno=60)
# -----------------------------
TABLA_12_ELECTRICA_COMP_W_M2 = {
    "Auditorios": 40,
    "Bibliotecas": 30,
    "Cafeterías y restaurantes (general)": 50,
    "Comercios - Galerías comerciales": 40,
    "Comercios - Grandes almacenes": 40,
    "Enseñanza (aularios)": 30,
    "Hospitales - Hospitalización": 60,
    "Hospitales - General (excepto quirófanos)": 60,
    "Hoteles": 30,
    "Museos": 40,
    "Oficinas": 30,
    "Salones de actos": 40,
}

# -----------------------------
# Tabla 13: Consumo diario agua potable
# (PDF p.63 aprox. / pno=62)
# -----------------------------
TABLA_13_AGUA_FRIA_L_DIA = {
    # unidad indicada en cada caso
    "Escuelas, institutos": ("L/persona", 20),
    "Hospitales": ("L/cama", 500),
    "Hoteles media categoría": ("L/cama", 135),
    "Hoteles alta categoría": ("L/cama", 200),
    "Internados": ("L/persona", 90),
    "Oficinas sin cafetería": ("L/persona", 15),
    "Oficinas con cafetería": ("L/persona", 18),
    "Restaurantes": ("L/cubierto", 7),
}

# -----------------------------
# Tabla 14: ACS - consumo y potencia
# (PDF p.64 aprox. / pno=63)
# -----------------------------
TABLA_14_ACS = {
    "Escuelas, institutos": ("L/persona", 5, "kW/persona", 0.16),
    "Hospitales": ("L/cama", 200, "kW/cama", 6.40),
    "Hoteles media categoría": ("L/cama", 35, "kW/cama", 1.12),
    "Hoteles alta categoría": ("L/cama", 100, "kW/cama", 3.20),
    "Internados": ("L/persona", 25, "kW/persona", 0.80),
    "Oficinas": ("L/persona", 5, "kW/persona", 0.16),
    "Restaurantes": ("L/cubierto", 6, "kW/cubierto", 0.19),
}

# -----------------------------
# Tabla 16: Aplicación sistemas de climatización (guía)
# (PDF p.99 aprox. / pno=98)
# Se codifica de forma compacta: {"Aplicación": { "Sistema": True/False } }
# -----------------------------
TABLA_16_SISTEMAS_CLIMA = {
    "Auditorios": {
        "Expansión directa": True,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": False,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": False,
    },
    "Bibliotecas": {
        "Expansión directa": True,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": False,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": True,
    },
    "Comercios": {
        "Expansión directa": True,
        "UTA con aire exterior": True,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": True,
    },
    "Bancos - Edificios corporativos": {
        "Expansión directa": False,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": True,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": True,
        "Inducción radiadores con aire primario": True,
    },
    "Bancos - Oficinas": {
        "Expansión directa": True,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": True,
        "Inducción radiadores con aire primario": True,
    },
    "Grandes almacenes": {
        "Expansión directa": True,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": False,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": False,
    },
    "Hospitales - General": {
        "Expansión directa": False,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": False,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": True,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": True,
        "Inducción radiadores con aire primario": True,
    },
    "Hospitales - Habitaciones": {
        "Expansión directa": False,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": False,
        "Techo/Suelo radiante": False,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": False,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": True,
    },
    "Hoteles - Habitaciones": {
        "Expansión directa": True,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": False,
        "Techo/Suelo radiante": False,
        "Todo-aire caudal constante": True,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": True,
        "Inducción radiadores con aire primario": True,
    },
    "Hoteles - General": {
        "Expansión directa": False,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": False,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": True,
    },
    "Laboratorios": {
        "Expansión directa": True,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": False,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": False,
    },
    "Museos": {
        "Expansión directa": False,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": False,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": False,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": True,
    },
    "Oficinas": {
        "Expansión directa": False,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": True,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": True,
        "Inducción radiadores con aire primario": True,
    },
    "Radio y TV - General": {
        "Expansión directa": True,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": True,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": True,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": True,
        "Inducción radiadores con aire primario": True,
    },
    "Radio y TV - Estudios": {
        "Expansión directa": False,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": False,
        "Techo/Suelo radiante": False,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": False,
    },
    "Residencial - Viviendas": {
        "Expansión directa": True,
        "UTA con aire exterior": True,
        "Calefacción: Radiadores": True,
        "Fancoil": False,
        "Techo/Suelo radiante": False,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": False,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": True,
    },
    "Residencial - General": {
        "Expansión directa": True,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": False,
        "Techo/Suelo radiante": True,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": True,
        "Inducción radiadores con aire primario": True,
    },
    "Teatros": {
        "Expansión directa": True,
        "UTA con aire exterior": False,
        "Calefacción: Radiadores": False,
        "Fancoil": False,
        "Techo/Suelo radiante": False,
        "Todo-aire caudal constante": False,
        "Todo-aire caudal variable": True,
        "Inducción con aire primario": False,
        "Inducción radiadores con aire primario": False,
    },
}
