from __future__ import annotations
from typing import Any, Dict
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_json(name: str) -> Dict[str, Any]:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))

DEFAULTS = _load_json("defaults.json")
CITY_ZONE = _load_json("cities_cte.json")

def init_state() -> None:
    import streamlit as st
    if "settings" in st.session_state:
        return
    first_use = list(DEFAULTS["uses"].keys())[0]
    st.session_state["settings"] = {
        "mode": "Conceptual",
        "use": first_use,
        "city": "Madrid",
        "zone_override": False,
        "ctezone": CITY_ZONE.get("Madrid", "D3"),
        "gfa_above_m2": 10000.0,
        "gfa_below_m2": 0.0,
        "parking_spaces": 0,
        "hvac_cooling_wm2": DEFAULTS["uses"][first_use]["hvac_cooling_wm2"],
        "hvac_heating_wm2": DEFAULTS["uses"][first_use]["hvac_heating_wm2"],
        "vent_above_lps_m2": DEFAULTS["uses"][first_use]["vent_lps_m2"],
        "parking_mode": DEFAULTS["parking"]["mode"],
        "parking_override_cte": False,
        "parking_supply_lps_per_space": DEFAULTS["parking"]["supply_lps_per_space"],
        "parking_extract_lps_per_space": DEFAULTS["parking"]["extract_lps_per_space_hs3"],
        "elec_wm2": DEFAULTS["uses"][first_use]["elec_wm2"],
        "elec_diversity": DEFAULTS["uses"][first_use]["elec_diversity"],
        "elec_pf": DEFAULTS["uses"][first_use]["elec_pf"],
        "pci_auto": True,
        "pci_bie_hours": DEFAULTS["pci"]["bie_hours"],
        "pci_spr_hours": DEFAULTS["pci"]["spr_hours"],
        "pci_bie_lps_per_1000m2_building": DEFAULTS["uses"][first_use]["pci_bie_lps_per_1000m2"],
        "pci_spr_lps_per_1000m2_building": DEFAULTS["uses"][first_use]["pci_spr_lps_per_1000m2"],
        "pci_bie_lps_per_1000m2_parking": 0.0,
        "pci_spr_lps_per_1000m2_parking": DEFAULTS["uses"][first_use]["pci_spr_lps_per_1000m2"],
        "pci_bie_manual_lps": 0.0,
        "pci_spr_manual_lps": 0.0,
    }

def get_settings() -> Dict[str, Any]:
    import streamlit as st
    init_state()
    return st.session_state["settings"]

def set_settings(s: Dict[str, Any]) -> None:
    import streamlit as st
    st.session_state["settings"] = s
