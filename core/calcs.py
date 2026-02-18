from __future__ import annotations
from typing import Any, Dict, Tuple
import pandas as pd
from .utils import safe_df, lps_to_m3h

def calc_hvac(s: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    gfa = float(s.get("gfa_above_m2",0) or 0) + float(s.get("gfa_below_m2",0) or 0)
    cool = float(s.get("hvac_cooling_wm2",0) or 0)
    heat = float(s.get("hvac_heating_wm2",0) or 0)
    df = safe_df([
        {"Concepto":"Superficie total (m²)","Valor":gfa},
        {"Concepto":"Frío específico (W/m²)","Valor":cool},
        {"Concepto":"Calor específico (W/m²)","Valor":heat},
        {"Concepto":"Potencia pico frío (kW)","Valor":gfa*cool/1000.0},
        {"Concepto":"Potencia pico calor (kW)","Valor":gfa*heat/1000.0},
    ], ["Concepto","Valor"])
    return df, {"cooling_kw": gfa*cool/1000.0, "heating_kw": gfa*heat/1000.0}

def calc_ventilation(s: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    gfa_above = float(s.get("gfa_above_m2",0) or 0)
    lpsm2 = float(s.get("vent_above_lps_m2",0) or 0)
    q_above_lps = gfa_above*lpsm2
    spaces = float(s.get("parking_spaces",0) or 0)
    q_sup_lps = spaces*float(s.get("parking_supply_lps_per_space",0) or 0)
    q_ext_lps = spaces*float(s.get("parking_extract_lps_per_space",0) or 0)
    df = safe_df([
        {"Ámbito":"Sobre rasante","Caudal (L/s)":q_above_lps,"Caudal (m³/h)":lps_to_m3h(q_above_lps),"Criterio":f"{lpsm2:.2f} L/s·m²"},
        {"Ámbito":"Parking (aportación)","Caudal (L/s)":q_sup_lps,"Caudal (m³/h)":lps_to_m3h(q_sup_lps),"Criterio":f"{float(s.get('parking_supply_lps_per_space',0) or 0):.0f} L/s·plaza"},
        {"Ámbito":"Parking (extracción)","Caudal (L/s)":q_ext_lps,"Caudal (m³/h)":lps_to_m3h(q_ext_lps),"Criterio":f"{float(s.get('parking_extract_lps_per_space',0) or 0):.0f} L/s·plaza"},
    ], ["Ámbito","Caudal (L/s)","Caudal (m³/h)","Criterio"])
    return df, {"above_lps": q_above_lps, "parking_supply_lps": q_sup_lps, "parking_extract_lps": q_ext_lps}

def calc_electrical(s: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    gfa = float(s.get("gfa_above_m2",0) or 0) + float(s.get("gfa_below_m2",0) or 0)
    w_m2 = float(s.get("elec_wm2",0) or 0)
    div = float(s.get("elec_diversity",0.7) or 0.7)
    pf = float(s.get("elec_pf",0.95) or 0.95)
    installed_kw = gfa*w_m2/1000.0
    demand_kw = installed_kw*div
    demand_kva = demand_kw/pf if pf>0 else demand_kw
    df = safe_df([
        {"Concepto":"Potencia instalada (kW)","Valor":installed_kw},
        {"Concepto":"Simultaneidad","Valor":div},
        {"Concepto":"cosφ","Valor":pf},
        {"Concepto":"Demanda estimada (kW)","Valor":demand_kw},
        {"Concepto":"Demanda estimada (kVA)","Valor":demand_kva},
    ], ["Concepto","Valor"])
    return df, {"demand_kw": demand_kw, "demand_kva": demand_kva}

def _reserve_m3(flow_lps: float, hours: float) -> float:
    return flow_lps*3600.0*hours/1000.0

def calc_pci(s: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    gfa_above = float(s.get("gfa_above_m2",0) or 0)
    gfa_below = float(s.get("gfa_below_m2",0) or 0)
    auto = bool(s.get("pci_auto", True))
    bie_h = float(s.get("pci_bie_hours",1.0) or 1.0)
    spr_h = float(s.get("pci_spr_hours",1.5) or 1.5)
    if auto:
        bie_b = float(s.get("pci_bie_lps_per_1000m2_building",0) or 0)
        spr_b = float(s.get("pci_spr_lps_per_1000m2_building",0) or 0)
        bie_p = float(s.get("pci_bie_lps_per_1000m2_parking",0) or 0)
        spr_p = float(s.get("pci_spr_lps_per_1000m2_parking",0) or 0)
        bie_lps = (gfa_above/1000.0)*bie_b + (gfa_below/1000.0)*bie_p
        spr_lps = (gfa_above/1000.0)*spr_b + (gfa_below/1000.0)*spr_p
        mode = "Automático por m²"
    else:
        bie_lps = float(s.get("pci_bie_manual_lps",0) or 0)
        spr_lps = float(s.get("pci_spr_manual_lps",0) or 0)
        mode = "Manual"
    v_bie = _reserve_m3(bie_lps, bie_h) if bie_lps>0 else 0.0
    v_spr = _reserve_m3(spr_lps, spr_h) if spr_lps>0 else 0.0
    total = v_bie+v_spr
    df = safe_df([
        {"Sistema":"BIEs / mangueras","Caudal (L/s)":round(bie_lps,2),"Tiempo (h)":bie_h,"Volumen (m³)":round(v_bie,2),"Modo":mode},
        {"Sistema":"Rociadores","Caudal (L/s)":round(spr_lps,2),"Tiempo (h)":spr_h,"Volumen (m³)":round(v_spr,2),"Modo":mode},
        {"Sistema":"TOTAL","Caudal (L/s)":"","Tiempo (h)":"","Volumen (m³)":round(total,2),"Modo":""},
    ], ["Sistema","Caudal (L/s)","Tiempo (h)","Volumen (m³)","Modo"])
    return df, {"reserve_total_m3": total, "bie_lps": bie_lps, "spr_lps": spr_lps}
