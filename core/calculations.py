# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import math
import numpy as np

from .constants import (
    TABLA_5_FRIO_W_M2, TABLA_6_FACTOR_FRIO,
    TABLA_7_CALOR_W_M2, TABLA_8_FACTOR_CALOR_RANGOS,
    TABLA_9_TODO_AIRE_LS_M2, TABLA_10_VENTILACION_LS_M2,
    TABLA_11_ELECTRICA_W_M2, TABLA_12_ELECTRICA_COMP_W_M2,
    TABLA_13_AGUA_FRIA_L_DIA, TABLA_14_ACS,
    USO_A_CATEGORIA_GLOBAL, TABLA_1_ESPACIO_GLOBAL, TABLA_2_ESPACIO_POR_INSTALACION
)
from .utils import WarningItem, to_float, nz

# -----------------------------
# Helpers
# -----------------------------
def _factor_calor_por_zona(zona: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Devuelve (factor, aviso) para Tabla 8.
    Si hay ambigüedad (D1 repetida), usa el factor mayor (conservador) y avisa.
    """
    zona = (zona or "").strip()
    matches = []
    for zonas, f in TABLA_8_FACTOR_CALOR_RANGOS:
        if zona in zonas:
            matches.append(f)
    if not matches:
        return None, f"Zona climática '{zona}' no encontrada en Tabla 8."
    if len(matches) > 1:
        return max(matches), f"Zona '{zona}' aparece en más de una fila en Tabla 8. Se aplica factor conservador {max(matches):.2f}."
    return matches[0], None

def _get_override(row: pd.Series, col: str) -> Optional[float]:
    return to_float(row.get(col))

def _zone_name(row: pd.Series) -> str:
    n = row.get("Nombre zona")
    if n is None or str(n).strip()=="":
        return f"Zona {row.get('ID', '')}".strip()
    return str(n).strip()

def _calc_personas(row: pd.Series) -> float:
    a = nz(to_float(row.get("Superficie (m²)")))
    dens = to_float(row.get("Densidad (pers/m²)"))
    pers = to_float(row.get("Personas"))
    if dens is not None and dens > 0 and a > 0:
        return dens * a
    return nz(pers)

def _calc_unidades_ocupacion(row: pd.Series) -> Tuple[str, float]:
    """
    Determina la 'unidad' de ocupación para agua/ACS:
    - camas si Camas >0
    - cubiertos si Cubiertos/día >0
    - personas en caso contrario
    """
    camas = to_float(row.get("Camas"))
    cub = to_float(row.get("Cubiertos/día"))
    if camas is not None and camas > 0:
        return "cama", camas
    if cub is not None and cub > 0:
        return "cubierto", cub
    return "persona", _calc_personas(row)

# -----------------------------
# Normalización DF
# -----------------------------
def normalize_zones_df(zones_df: pd.DataFrame) -> pd.DataFrame:
    df = zones_df.copy()
    if "ID" not in df.columns:
        df.insert(0, "ID", range(1, len(df)+1))
    # normalizar superficies y ocupación
    df["Superficie (m²)"] = df["Superficie (m²)"].apply(to_float)
    df["Personas_calc"] = df.apply(_calc_personas, axis=1)
    return df

# -----------------------------
# Cálculos por módulo
# -----------------------------
def calc_climatizacion(zones_df: pd.DataFrame, settings: Dict[str, Any]) -> Tuple[pd.DataFrame, List[WarningItem], Dict[str, float]]:
    """
    Devuelve:
      - df con resultados por zona (frío y calor)
      - warnings
      - totales (kW)
    """
    df = normalize_zones_df(zones_df)
    warnings: List[WarningItem] = []

    oversize_frio = float(settings.get("oversize_frio", 1.00))
    oversize_calor = float(settings.get("oversize_calor", 1.10))

    out_rows = []
    total_frio_w = 0.0
    total_calor_w = 0.0

    for _, r in df.iterrows():
        zona = _zone_name(r)
        uso = str(r.get("Uso", "")).strip()
        nivel = str(r.get("Nivel carga (B/M/A)", "M")).strip() or "M"
        clima = str(r.get("Zona climática", "")).strip()
        area = nz(to_float(r.get("Superficie (m²)")))

        # frío
        frio_override = _get_override(r, "Frío override (W/m²)")
        frio_base = None
        if frio_override is not None:
            frio_base = frio_override
        else:
            if uso in TABLA_5_FRIO_W_M2 and nivel in TABLA_5_FRIO_W_M2[uso]:
                frio_base = TABLA_5_FRIO_W_M2[uso][nivel]
            else:
                warnings.append(WarningItem("Climatización", zona, f"Sin dato de frío para uso '{uso}' (Tabla 5). Usa override."))
        factor_frio = TABLA_6_FACTOR_FRIO.get(clima)
        if factor_frio is None:
            warnings.append(WarningItem("Climatización", zona, f"Zona climática '{clima}' no encontrada en Tabla 6 (frío)."))
            factor_frio = np.nan

        frio_wm2 = (frio_base * factor_frio) if (frio_base is not None and factor_frio==factor_frio) else np.nan
        frio_w = frio_wm2 * area if frio_wm2==frio_wm2 else np.nan

        # calor
        calor_override = _get_override(r, "Calor override (W/m²)")
        calor_base = None
        if calor_override is not None:
            calor_base = calor_override
        else:
            if uso in TABLA_7_CALOR_W_M2 and nivel in TABLA_7_CALOR_W_M2[uso]:
                calor_base = TABLA_7_CALOR_W_M2[uso][nivel]
            else:
                warnings.append(WarningItem("Climatización", zona, f"Sin dato de calor para uso '{uso}' (Tabla 7). Usa override."))

        factor_calor, aviso = _factor_calor_por_zona(clima)
        if aviso:
            warnings.append(WarningItem("Climatización", zona, aviso))
        if factor_calor is None:
            factor_calor = np.nan

        calor_wm2 = (calor_base * factor_calor) if (calor_base is not None and factor_calor==factor_calor) else np.nan
        calor_w = calor_wm2 * area if calor_wm2==calor_wm2 else np.nan

        if frio_w==frio_w:
            total_frio_w += float(frio_w)
        if calor_w==calor_w:
            total_calor_w += float(calor_w)

        out_rows.append({
            "ID": r.get("ID"),
            "Zona": zona,
            "Uso": uso,
            "Superficie (m²)": area,
            "Zona climática": clima,
            "Nivel": nivel,
            "Frío base (W/m²)": frio_base,
            "Factor frío (Tabla 6)": factor_frio,
            "Frío (W/m²)": frio_wm2,
            "Potencia frío (kW)": (frio_w/1000.0) if frio_w==frio_w else np.nan,
            "Calor base (W/m²)": calor_base,
            "Factor calor (Tabla 8)": factor_calor,
            "Calor (W/m²)": calor_wm2,
            "Potencia calor (kW)": (calor_w/1000.0) if calor_w==calor_w else np.nan,
        })

    res = pd.DataFrame(out_rows)
    totals = {
        "frio_total_kw": total_frio_w/1000.0,
        "calor_total_kw": total_calor_w/1000.0,
        "frio_generador_kw": (total_frio_w/1000.0)*oversize_frio,
        "calor_generador_kw": (total_calor_w/1000.0)*oversize_calor,
    }
    return res, warnings, totals

def calc_ventilacion_y_todo_aire(zones_df: pd.DataFrame, settings: Dict[str, Any]) -> Tuple[pd.DataFrame, List[WarningItem], Dict[str, float]]:
    """
    Ventilación exterior (Tabla 10) y caudal tratado para sistemas todo-aire (Tabla 9).
    """
    df = normalize_zones_df(zones_df)
    warnings: List[WarningItem] = []

    total_vent_lps = 0.0
    total_todoaire_lps = 0.0

    # Ventilación aparcamiento bajo rasante (CTE – aportación vs extracción, por plazas)
    parking_spaces = float(settings.get("parking_plazas", 0) or 0)

    # Defaults: HS3 salubridad -> 120/120; SI3 control de humos -> 120/150 (editable)
    modo = str(settings.get("parking_modo", "") or "")
    if "Control de humos" in modo:
        def_aporte = 120.0
        def_extr = 150.0
    else:
        def_aporte = 120.0
        def_extr = 120.0

    parking_supply_lps_per = float(settings.get("parking_aporte_lps_por_plaza", def_aporte) or def_aporte)
    parking_extract_lps_per = float(settings.get("parking_extraccion_lps_por_plaza", def_extr) or def_extr)

    parking_supply_lps = 0.0
    parking_extract_lps = 0.0
    try:
        gfa_below = float(settings.get("gfa_below_m2", 0) or 0)
    except Exception:
        gfa_below = 0.0

    if parking_spaces > 0:
        parking_supply_lps = parking_spaces * parking_supply_lps_per
        parking_extract_lps = parking_spaces * parking_extract_lps_per
    else:
        # Si hay bajo rasante, avisar para que indiquen plazas (si aplica garaje)
        if gfa_below > 0:
            warnings.append(WarningItem("Ventilación", "Bajo rasante", "Indica nº de plazas de parking para calcular ventilación de garaje (CTE)."))

    out_rows = []
    for _, r in df.iterrows():
        zona = _zone_name(r)
        uso = str(r.get("Uso", "")).strip()
        nivel = str(r.get("Nivel carga (B/M/A)", "M")).strip() or "M"
        expos = str(r.get("Exposición (E/S/W, N, Interior)", "Interior")).strip() or "Interior"
        area = nz(to_float(r.get("Superficie (m²)")))

        # Ventilación exterior (Tabla 10)
        vent_override = _get_override(r, "Ventilación override (L/s·m²)")
        vent_lsm2 = None
        if vent_override is not None:
            vent_lsm2 = vent_override
        else:
            vent_lsm2 = TABLA_10_VENTILACION_LS_M2.get(uso)
            if vent_lsm2 is None:
                warnings.append(WarningItem("Ventilación", zona, f"Sin dato de ventilación para uso '{uso}' (Tabla 10). Usa override."))
        vent_lps = (vent_lsm2 * area) if vent_lsm2 is not None else np.nan
        # Todo-aire (Tabla 9)
        # Mapear el uso a la tipología de Tabla 9 (si aplica)
        todo_aire_activo = bool(settings.get("todo_aire_activo", False))
        mapping = settings.get("mapa_uso_tabla9", {}) or {}

        def _auto_tipologia_tabla9(u: str) -> Optional[str]:
            uu = (u or "").strip()
            if uu in TABLA_9_TODO_AIRE_LS_M2:
                return uu
            # heurísticos para usos habituales
            if uu == "Oficinas":
                return "Oficinas - Espacio abierto"
            if uu == "Hoteles":
                return "Hoteles (habitaciones)"
            if uu in ("Museos", "Bibliotecas"):
                return "Museos / Bibliotecas"
            if uu in ("Auditorios", "Teatros"):
                return "Auditorios / Teatros"
            return None

        tip9 = mapping.get(uso) or (_auto_tipologia_tabla9(uso) if todo_aire_activo else None)
        todoaire_lsm2 = None
        if todo_aire_activo:
            if tip9:
                try:
                    todoaire_lsm2 = TABLA_9_TODO_AIRE_LS_M2[tip9][expos][nivel]
                    if todoaire_lsm2 is None:
                        warnings.append(WarningItem("Todo-aire", zona, f"Tabla 9 no aporta valor para '{tip9}' en exposición '{expos}' y nivel '{nivel}'."))
                except Exception:
                    warnings.append(WarningItem("Todo-aire", zona, f"Error consultando Tabla 9 para tipología '{tip9}'."))
            else:
                warnings.append(WarningItem("Todo-aire", zona, f"Uso '{uso}' no mapeado a Tabla 9. Selecciona tipología en la página de Ventilación/Todo-aire."))

        todoaire_lps = (todoaire_lsm2 * area) if (todoaire_lsm2 is not None) else np.nan

        if vent_lps==vent_lps:
            total_vent_lps += float(vent_lps)
        if todoaire_lps==todoaire_lps:
            total_todoaire_lps += float(todoaire_lps)

        out_rows.append({
            "ID": r.get("ID"),
            "Zona": zona,
            "Uso": uso,
            "Superficie (m²)": area,
            "Nivel": nivel,
            "Exposición": expos,
            "Ventilación (L/s·m²)": vent_lsm2,
            "Ventilación total (L/s)": vent_lps,
            "Tipología Tabla 9": tip9,
            "Todo-aire (L/s·m²)": todoaire_lsm2,
            "Todo-aire total (L/s)": todoaire_lps,
        })

    res = pd.DataFrame(out_rows)

    # Totales: mantener separada la ventilación de sobre rasante (Tabla 10) y la extracción de garaje (CTE HS 3).
    vent_sobre_rasante_lps = total_vent_lps
    vent_sobre_rasante_m3h = vent_sobre_rasante_lps * 3.6

    totals = {
        # Alias para compatibilidad: "vent_total_*" = sobre rasante (NO incluye garaje)
        "vent_total_lps": vent_sobre_rasante_lps,
        "vent_total_m3h": vent_sobre_rasante_m3h,

        # Totales explícitos
        "vent_sobre_rasante_lps": vent_sobre_rasante_lps,
        "vent_sobre_rasante_m3h": vent_sobre_rasante_m3h,

        # Garaje (bajo rasante) – por plazas
        "vent_garaje_aporte_lps": parking_supply_lps,
        "vent_garaje_extraccion_lps": parking_extract_lps,
        "vent_garaje_aporte_m3h": parking_supply_lps * 3.6,
        "vent_garaje_extraccion_m3h": parking_extract_lps * 3.6,

        "todoaire_total_lps": total_todoaire_lps,
        "todoaire_total_m3h": total_todoaire_lps * 3.6,
    }
    return res, warnings, totals


def calc_electricidad(zones_df: pd.DataFrame, settings: Dict[str, Any]) -> Tuple[pd.DataFrame, List[WarningItem], Dict[str, Any]]:
    df = normalize_zones_df(zones_df)
    warnings: List[WarningItem] = []
    out_rows = []

    total_kw = 0.0
    total_comp_kw = 0.0

    for _, r in df.iterrows():
        zona = _zone_name(r)
        uso = str(r.get("Uso", "")).strip()
        area = nz(to_float(r.get("Superficie (m²)")))
        comp = bool(r.get("Suministro complementario", False))

        # normal
        e_override = _get_override(r, "Eléctrica override (W/m²)")
        w_m2 = e_override if e_override is not None else TABLA_11_ELECTRICA_W_M2.get(uso)
        if w_m2 is None:
            warnings.append(WarningItem("Electricidad", zona, f"Sin potencia específica para uso '{uso}' (Tabla 11). Usa override."))
        p_kw = (w_m2 * area)/1000.0 if w_m2 is not None else np.nan

        # complementario
        ec_override = _get_override(r, "Eléctrica comp. override (W/m²)")
        wc_m2 = None
        if comp:
            wc_m2 = ec_override if ec_override is not None else TABLA_12_ELECTRICA_COMP_W_M2.get(uso)
            if wc_m2 is None:
                warnings.append(WarningItem("Electricidad", zona, f"Complementario activado pero sin dato para '{uso}' (Tabla 12). Usa override."))
        p_comp_kw = (wc_m2 * area)/1000.0 if wc_m2 is not None else 0.0

        if p_kw==p_kw:
            total_kw += float(p_kw)
        if p_comp_kw==p_comp_kw:
            total_comp_kw += float(p_comp_kw)

        out_rows.append({
            "ID": r.get("ID"),
            "Zona": zona,
            "Uso": uso,
            "Superficie (m²)": area,
            "W/m² normal": w_m2,
            "Potencia normal (kW)": p_kw,
            "Complementario": comp,
            "W/m² comp": wc_m2 if comp else None,
            "Potencia comp (kW)": p_comp_kw if comp else 0.0,
        })

    res = pd.DataFrame(out_rows)

    # criterio BT/MT del documento
    acometida = "BT" if total_kw < 400 else "MT"

    totals: Dict[str, Any] = {
        "potencia_normal_kw": total_kw,
        "potencia_comp_kw": total_comp_kw,
        "potencia_total_kw": total_kw + total_comp_kw,
        "acometida_sugerida": acometida,
        "nota_reserva_compania": "Conviene prever reserva de espacio si P>100 kW (texto del documento).",
    }

    # módulo opcional motores (no proviene del documento, es ampliación)
    motors = settings.get("motores", [])
    if motors:
        motor_rows = []
        for m in motors:
            p_kw = float(m.get("potencia_kw", 0) or 0)
            v = float(m.get("tension_v", 400) or 400)
            cosphi = float(m.get("cosphi", 0.85) or 0.85)
            eta = float(m.get("eta", 0.90) or 0.90)
            mult = float(m.get("multiplo_arranque", 6.0) or 6.0)
            ib = (p_kw*1000)/(np.sqrt(3)*v*cosphi*eta) if p_kw>0 else 0
            istart = ib * mult
            motor_rows.append({
                "Motor": m.get("nombre","Motor"),
                "P (kW)": p_kw,
                "V (V)": v,
                "cosφ": cosphi,
                "η": eta,
                "Ib (A)": ib,
                "Multiplo arranque": mult,
                "Iarr (A)": istart,
            })
        totals["motores_df"] = pd.DataFrame(motor_rows)

    return res, warnings, totals

def calc_agua_y_acs(zones_df: pd.DataFrame, settings: Dict[str, Any]) -> Tuple[pd.DataFrame, List[WarningItem], Dict[str, float]]:
    df = normalize_zones_df(zones_df)
    warnings: List[WarningItem] = []
    out_rows = []

    total_agua_l_dia = 0.0
    total_acs_l_dia = 0.0
    total_acs_kw = 0.0

    # mapeo simple uso->fila tabla 13/14 (editable)
    map_agua = settings.get("mapa_uso_tabla13", {})
    map_acs = settings.get("mapa_uso_tabla14", {})

    for _, r in df.iterrows():
        zona = _zone_name(r)
        uso = str(r.get("Uso", "")).strip()
        unidad, n = _calc_unidades_ocupacion(r)
        # Agua fría (Tabla 13)
        def _auto_key_tabla13(u: str) -> Optional[str]:
            uu = (u or "").strip()
            if uu in TABLA_13_AGUA_FRIA_L_DIA:
                return uu
            if uu == "Oficinas":
                return "Oficinas sin cafetería"
            if uu == "Enseñanza (aularios)":
                return "Escuelas, institutos"
            if uu.startswith("Hospitales"):
                return "Hospitales"
            if uu == "Hoteles":
                return "Hoteles media categoría"
            if "Restaur" in uu or "Cafeter" in uu:
                return "Restaurantes"
            return None

        key13 = map_agua.get(uso) or _auto_key_tabla13(uso)
        agua_l = np.nan
        if key13:
            unit13, val13 = TABLA_13_AGUA_FRIA_L_DIA.get(key13, (None, None))
            if unit13 is None:
                warnings.append(WarningItem("Agua", zona, f"Mapeo a Tabla 13 inválido: '{key13}'."))
            else:
                # comprobar unidad
                if unit13.endswith("/persona") and unidad != "persona":
                    warnings.append(WarningItem("Agua", zona, f"Tabla 13 '{key13}' usa persona, pero la zona tiene '{unidad}'. Se usa Personas_calc."))
                    n_use = nz(r.get("Personas_calc"))
                elif unit13.endswith("/cama") and unidad != "cama":
                    warnings.append(WarningItem("Agua", zona, f"Tabla 13 '{key13}' usa cama, pero la zona no informa camas."))
                    n_use = n
                elif unit13.endswith("/cubierto") and unidad != "cubierto":
                    warnings.append(WarningItem("Agua", zona, f"Tabla 13 '{key13}' usa cubierto, pero la zona no informa cubiertos/día."))
                    n_use = n
                else:
                    n_use = n
                agua_l = float(val13) * float(n_use)
        else:
            warnings.append(WarningItem("Agua", zona, f"Uso '{uso}' no mapeado a Tabla 13. Selecciona tipología en la página de Agua/ACS."))
        # ACS (Tabla 14)
        def _auto_key_tabla14(u: str) -> Optional[str]:
            uu = (u or "").strip()
            if uu in TABLA_14_ACS:
                return uu
            if uu in ("Oficinas sin cafetería", "Oficinas con cafetería"):
                return "Oficinas"
            if uu == "Enseñanza (aularios)":
                return "Escuelas, institutos"
            if uu.startswith("Hospitales"):
                return "Hospitales"
            if uu == "Hoteles":
                return "Hoteles media categoría"
            if "Restaur" in uu or "Cafeter" in uu:
                return "Restaurantes"
            return None

        key14 = map_acs.get(uso) or _auto_key_tabla14(uso)
        acs_l = np.nan
        acs_kw = np.nan
        if key14:
            rec = TABLA_14_ACS.get(key14)
            if not rec:
                warnings.append(WarningItem("ACS", zona, f"Mapeo a Tabla 14 inválido: '{key14}'."))
            else:
                unit_l, val_l, unit_kw, val_kw = rec
                if unit_l.endswith("/persona") and unidad != "persona":
                    warnings.append(WarningItem("ACS", zona, f"Tabla 14 '{key14}' usa persona, pero la zona tiene '{unidad}'. Se usa Personas_calc."))
                    n_use = nz(r.get("Personas_calc"))
                else:
                    n_use = n
                acs_l = float(val_l) * float(n_use)
                acs_kw = float(val_kw) * float(n_use)
        else:
            warnings.append(WarningItem("ACS", zona, f"Uso '{uso}' no mapeado a Tabla 14. Selecciona tipología en la página de Agua/ACS."))

        if agua_l==agua_l:
            total_agua_l_dia += float(agua_l)
        if acs_l==acs_l:
            total_acs_l_dia += float(acs_l)
        if acs_kw==acs_kw:
            total_acs_kw += float(acs_kw)

        out_rows.append({
            "ID": r.get("ID"),
            "Zona": zona,
            "Uso": uso,
            "Unidad ocupación": unidad,
            "Cantidad": n,
            "Agua fría tipología (Tabla 13)": key13,
            "Agua fría (L/día)": agua_l,
            "ACS tipología (Tabla 14)": key14,
            "ACS (L/día)": acs_l,
            "Potencia ACS (kW)": acs_kw,
        })

    res = pd.DataFrame(out_rows)
    totals = {
        "agua_fria_total_L_dia": total_agua_l_dia,
        "agua_fria_total_m3_dia": total_agua_l_dia/1000.0,
        "acs_total_L_dia": total_acs_l_dia,
        "acs_total_m3_dia": total_acs_l_dia/1000.0,
        "acs_potencia_total_kw": total_acs_kw,
    }
    return res, warnings, totals

def calc_reservas_espacios(zones_df: pd.DataFrame, settings: Dict[str, Any]) -> Tuple[pd.DataFrame, List[WarningItem], Dict[str, Any]]:
    """
    Estima reservas de espacio:
    - Global (Tabla 1), ponderando por uso/categoría
    - Por instalación (Tabla 2), según selección de sistemas
    """
    df = normalize_zones_df(zones_df)
    warnings: List[WarningItem] = []

    # categoría global por zona
    cat_override_col = "Categoría global (Tabla 1)"
    # If missing, create from default mapping; if present but empty/NaN, backfill from default mapping.
    if cat_override_col not in df.columns:
        df[cat_override_col] = df["Uso"].map(USO_A_CATEGORIA_GLOBAL)
    else:
        backfill = df["Uso"].map(USO_A_CATEGORIA_GLOBAL)
        col = df[cat_override_col]
        # treat NaN / empty strings as missing
        missing_mask = col.isna() | (col.astype(str).str.strip() == "") | (col.astype(str).str.strip().str.lower() == "nan")
        df.loc[missing_mask, cat_override_col] = backfill[missing_mask]

    # total área
    total_area = float(df["Superficie (m²)"].fillna(0).sum())

    # ponderación por categoría: sum áreas por categoría
    group = df.groupby(cat_override_col, dropna=False)["Superficie (m²)"].sum().to_dict()

    # global range
    global_min = 0.0
    global_max = 0.0
    for cat, a in group.items():
        if cat not in TABLA_1_ESPACIO_GLOBAL:
            cat_str = "" if cat is None else str(cat)
            if cat_str.strip() == "" or cat_str.strip().lower() == "nan":
                warnings.append(WarningItem("Espacios", "(missing)", "Falta 'Categoría global (Tabla 1)' en alguna zona. Rellénala en 'Datos y zonas' o revisa el mapeo del uso."))
            else:
                warnings.append(WarningItem("Espacios", cat_str, f"Categoría '{cat_str}' sin rango en Tabla 1."))
            continue
        pmin, pmax = TABLA_1_ESPACIO_GLOBAL[cat]
        global_min += a * pmin/100.0
        global_max += a * pmax/100.0

    # por instalación: seleccionar perfiles
    instalaciones_sel = settings.get("instalaciones_seleccion", list(TABLA_2_ESPACIO_POR_INSTALACION.keys()))
    inst_rows = []
    for inst in instalaciones_sel:
        if inst not in TABLA_2_ESPACIO_POR_INSTALACION:
            warnings.append(WarningItem("Espacios", "Global", f"Instalación '{inst}' no encontrada en Tabla 2."))
            continue
        pmin, pmax = TABLA_2_ESPACIO_POR_INSTALACION[inst]
        inst_rows.append({
            "Instalación": inst,
            "% min": pmin,
            "% max": pmax,
            "m² min": total_area * pmin/100.0,
            "m² max": total_area * pmax/100.0,
        })

    res = pd.DataFrame(inst_rows)
    totals = {
        "superficie_total_m2": total_area,
        "reserva_global_min_m2": global_min,
        "reserva_global_max_m2": global_max,
    }
    return res, warnings, totals

def calc_pci(settings: Dict[str, Any]) -> Tuple[pd.DataFrame, List[WarningItem], Dict[str, float]]:
    """
    PCI (pre-dimensioning):
    - Auto-calculates design flows for BIEs and sprinklers from building/parking areas using typical ratios (editable).
    - Allows manual override.
    - Computes reserve volumes (m³) from flow (L/s) and duration (h).

    Nota: Si el documento JG no proporciona ratios por m² para PCI, se aplican ratios "habituales" como valor por defecto.
    """
    warnings: List[WarningItem] = []
    out: List[Dict[str, Any]] = []

    # Areas
    gfa_above = float(settings.get("gfa_above_m2", 0) or 0)
    gfa_below = float(settings.get("gfa_below_m2", 0) or 0)

    # Durations (can be edited in UI)
    hose_time_h = float(settings.get("pci_mangueras_tiempo_h", 1.0) or 1.0)
    sprink_time_h = float(settings.get("pci_rociadores_tiempo_h", 1.5) or 1.5)

    # Auto ratios (L/s per 1000 m²) - typical defaults, editable
    # These are placeholders when JG does not provide explicit values.
    r_bie_building = float(settings.get("pci_ratio_bie_building_lps_per_1000m2", 3.33) or 3.33)
    r_bie_parking  = float(settings.get("pci_ratio_bie_parking_lps_per_1000m2", 0.00) or 0.00)
    r_spr_building = float(settings.get("pci_ratio_spr_building_lps_per_1000m2", 25.0) or 25.0)
    r_spr_parking  = float(settings.get("pci_ratio_spr_parking_lps_per_1000m2", 25.0) or 25.0)

    auto = bool(settings.get("pci_auto", True))

    def auto_flow(area_m2: float, ratio_lps_per_1000m2: float) -> float:
        return (area_m2 / 1000.0) * ratio_lps_per_1000m2 if area_m2 > 0 and ratio_lps_per_1000m2 > 0 else 0.0

    # Auto-calculated flows (building + parking)
    hose_flow_auto = auto_flow(gfa_above, r_bie_building) + auto_flow(gfa_below, r_bie_parking)
    sprink_flow_auto = auto_flow(gfa_above, r_spr_building) + auto_flow(gfa_below, r_spr_parking)

    # Manual entries (if user chooses)
    hose_flow_manual = float(settings.get("pci_mangueras_caudal_lps", 0) or 0)
    sprink_flow_manual = float(settings.get("pci_rociadores_caudal_lps", 0) or 0)

    hose_flow_lps = hose_flow_auto if auto else hose_flow_manual
    sprink_flow_lps = sprink_flow_auto if auto else sprink_flow_manual

    gas_ext = bool(settings.get("pci_extincion_gas", False))

    def vol_m3(flow_lps: float, hours: float) -> float:
        return flow_lps * 3600 * hours / 1000.0

    v_hose = vol_m3(hose_flow_lps, hose_time_h) if hose_flow_lps > 0 else 0.0
    v_spr = vol_m3(sprink_flow_lps, sprink_time_h) if sprink_flow_lps > 0 else 0.0
    v_total = v_hose + v_spr

    out.append({
        "Sistema": "BIEs / mangueras",
        "Caudal (L/s)": round(hose_flow_lps, 2),
        "Tiempo (h)": hose_time_h,
        "Volumen reserva (m³)": round(v_hose, 2),
        "Modo caudal": "Automático por m²" if auto else "Manual",
    })
    out.append({
        "Sistema": "Rociadores",
        "Caudal (L/s)": round(sprink_flow_lps, 2),
        "Tiempo (h)": sprink_time_h,
        "Volumen reserva (m³)": round(v_spr, 2),
        "Modo caudal": "Automático por m²" if auto else "Manual",
    })
    if gas_ext:
        out.append({"Sistema": "Extinción por gas (informativo)", "Caudal (L/s)": None, "Tiempo (h)": None, "Volumen reserva (m³)": None, "Modo caudal": None})

    res = pd.DataFrame(out)

    totals: Dict[str, float] = {
        "pci_reserva_total_m3": float(round(v_total, 2)),
        "pci_bies_caudal_lps": float(round(hose_flow_lps, 2)),
        "pci_rociadores_caudal_lps": float(round(sprink_flow_lps, 2)),
        "pci_gfa_sobre_m2": float(gfa_above),
        "pci_gfa_bajo_m2": float(gfa_below),
    }

    pci_activo = bool(settings.get("pci_activo", False))
    if pci_activo and hose_flow_lps == 0 and sprink_flow_lps == 0:
        warnings.append(WarningItem("PCI", "Global", "No se han podido calcular caudales de diseño (ratios=0 o áreas=0)."))

    return res, warnings, totals
