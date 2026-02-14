# -*- coding: utf-8 -*-
from __future__ import annotations

from .constants import (
    TABLA_5_FRIO_W_M2, TABLA_7_CALOR_W_M2, TABLA_10_VENTILACION_LS_M2,
    TABLA_11_ELECTRICA_W_M2, TABLA_12_ELECTRICA_COMP_W_M2, USO_A_CATEGORIA_GLOBAL
)

def all_usos() -> list[str]:
    usos = set()
    for d in [TABLA_5_FRIO_W_M2, TABLA_7_CALOR_W_M2, TABLA_10_VENTILACION_LS_M2, TABLA_11_ELECTRICA_W_M2, TABLA_12_ELECTRICA_COMP_W_M2, USO_A_CATEGORIA_GLOBAL]:
        usos |= set(d.keys())
    # añadir algunos usos frecuentes que se mapean a tablas 13/14 mediante selector
    usos |= {
        "Escuelas, institutos",
        "Internados",
        "Hoteles media categoría",
        "Hoteles alta categoría",
        "Oficinas sin cafetería",
        "Oficinas con cafetería",
        "Restaurantes",
        "CPD / Data Center",
        "Industrial",
    }
    return sorted(usos)
