# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import math
import pandas as pd

def to_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        if isinstance(x, (int, float)):
            return float(x)
        s = str(x).strip().replace(",", ".")
        if s == "":
            return None
        return float(s)
    except Exception:
        return None

def nz(x: Optional[float], default: float = 0.0) -> float:
    return default if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)

def clamp_positive(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    return x if x >= 0 else None

def df_required_columns(df: pd.DataFrame, cols: list[str]) -> list[str]:
    missing = [c for c in cols if c not in df.columns]
    return missing

def human_kw(watts: float) -> float:
    return watts / 1000.0

def lps_to_m3h(lps: float) -> float:
    # 1 L/s = 3.6 m³/h
    return lps * 3.6

def m3h_to_lps(m3h: float) -> float:
    return m3h / 3.6

def lps_to_m3s(lps: float) -> float:
    return lps / 1000.0

def m3_to_liters(m3: float) -> float:
    return m3 * 1000.0

def liters_to_m3(liters: float) -> float:
    return liters / 1000.0

def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0

@dataclass
class WarningItem:
    module: str
    zone: str
    message: str
