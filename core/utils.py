from __future__ import annotations
from typing import Any, Dict, List, Optional
import pandas as pd

def lps_to_m3h(lps: float) -> float:
    return lps * 3.6

def safe_df(rows: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if columns:
        for c in columns:
            if c not in df.columns:
                df[c] = None
        df = df[columns]
    return df
