# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd

def sample_zones_office() -> pd.DataFrame:
    """
    Single-use example (Office) with two zones (above-ground / below-ground),
    aligned with the "one building = one use" approach.
    """
    data = [
        {"ID": 1, "Nombre zona": "Above-ground (Office)", "Uso": "Oficinas", "Superficie (m²)": 4500, "Zona climática": "D1", "Nivel carga (B/M/A)": "M",
         "Exposición (E/S/W, N, Interior)": "Interior", "Densidad (pers/m²)": 0.08, "Personas": None, "Camas": None, "Cubiertos/día": None,
         "Suministro complementario": False},
        {"ID": 2, "Nombre zona": "Below-ground (Office / Basement)", "Uso": "Oficinas", "Superficie (m²)": 1000, "Zona climática": "D1", "Nivel carga (B/M/A)": "B",
         "Exposición (E/S/W, N, Interior)": "Interior", "Densidad (pers/m²)": 0.02, "Personas": None, "Camas": None, "Cubiertos/día": None,
         "Suministro complementario": False},
    ]
    return pd.DataFrame(data)
