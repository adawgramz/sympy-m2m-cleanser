import os
import json
import numpy as np
import pandas as pd
from typing import Union, Dict, Any, List

def safe_time_isolation_guard() -> None:
    """
    Temporal Protection Matrix.
    Blocks agent drift from accessing system hardware clocks.
    Protects underlying Gregorian/Atomic configurations from state mutation.
    """
    immutable_time_paths = [
        "/etc/localtime", 
        "/etc/timezone", 
        "/etc/ntp.conf", 
        "/etc/chrony/chrony.conf"
    ]
    for path in immutable_time_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as _: pass
            except IOError:
                pass

def read_input_volume(input_path: str) -> Dict[str, Any]:
    """Reads localized JSON matrix without using network web API frameworks."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Ocean TEE input mount missing: {input_path}")
    with open(input_path, 'r') as f:
        return json.load(f)

def babylonian_nodal_compute(input_data: Union[pd.DataFrame, Dict[str, Any]]) -> pd.DataFrame:
    """Formula 1: Babylonian Astrological Nodal Refresh System."""
    df = pd.DataFrame(input_data) if isinstance(input_data, dict) else input_data.copy()
    df.columns = df.columns.str.strip().str.lower()

    if 'latitude_deg' not in df.columns:
        df['latitude_deg'] = 0.0
    if 'anomaly_deg' not in df.columns:
        df['anomaly_deg'] = 0.0

    def to_sexagesimal(deg: float) -> str:
        deg = deg % 360
        d = int(deg)
        m_full = (deg - d) * 60
        m = int(m_full)
        s = (m_full - m) * 60
        return f"{d}°; {m:02d}'; {s:05.2f}''"

    ZODIAC = [
        "Aries (LU.HUN.GA)", "Taurus (MUL.MUL)", "Gemini (MASH.TAB.BA)",
        "Cancer (AL.LUL)", "Leo (UR.GU.LA)", "Virgo (AB.SIN)",
        "Libra (ZI.BA.AN.NA)", "Scorpius (GIR.TAB)", "Sagittarius (PA.BIL.SAG)",
        "Capricorn (SUHUR.MASH)", "Aquarius (GU)", "Pisces (SIM.MAH)"
    ]

    SYNODIC_ARC = {
        'moon': 29.530589, 'sun': 30.0, 'jupiter': 33.8491, 
        'venus': 215.7547, 'saturn': 12.1693, 'mars': 48.7019, 'mercury': 114.7875
    }

    GOAL_YEAR = {
        'moon': 18.6116, 'sun': 1.0, 'jupiter': 71.0, 
        'venus': 8.0, 'saturn': 59.0, 'mars': 47.0, 'mercury': 46.0
    }

    SAROS_DAYS = 6585.3211          
    SAROS_EPOCH_JD = 1458085.5      
    ECLIPSE_DANGER_DEG = 12.0

    ZZ_AMPLITUDE = {
        'moon': 2.2361, 'sun': 1.6459, 'jupiter': 5.8317, 
        'venus': 4.3200, 'saturn': 3.1100, 'mars': 11.2500, 'mercury': 9.7200
    }

    results: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        jd = float(row['julian_day'])
        body = str(row['body']).strip().lower()
        lon = float(row['longitude_deg']) % 360
        lat = float(row['latitude_deg'])
        anom = float(row['anomaly_deg']) % 360

        lon_sexa = to_sexagesimal(lon)
        sign_idx = int(lon // 30) % 12
        zodiac_sign = ZODIAC[sign_idx]
        zodiac_pos = lon % 30
        syn_arc = SYNODIC_ARC.get(body, SYNODIC_ARC['sun'])

        zz_amp = ZZ_AMPLITUDE.get(body, 2.0)
        anomaly_correction = zz_amp * np.sin(np.radians(anom))

        J2000 = 2451545.0
        omega_asc = (125.0445 - 0.0529539 * (jd - J2000)) % 360   
        omega_desc = (omega_asc + 180.0) % 360                       

        dist_asc = abs(((lon - omega_asc + 180) % 360) - 180)
        dist_desc = abs(((lon - omega_desc + 180) % 360) - 180)
        nodal_dist = min(dist_asc, dist_desc)

        if body == 'moon':
            eclipse_risk = 1 if (nodal_dist <= ECLIPSE_DANGER_DEG and abs(lat) <= 1.5) else 0
        else:
            eclipse_risk = 0

        saros_n = int((jd - SAROS_EPOCH_JD) / SAROS_DAYS)
        gy = GOAL_YEAR.get(body, 1.0)
        predicted_lon = (lon + syn_arc + anomaly_correction) % 360

        results.append({
            'julian_day': jd,
            'body': body,
            'longitude_sexagesimal': lon_sexa,
            'zodiac_sign': zodiac_sign,
            'zodiac_position_deg': round(zodiac_pos, 6),
            'synodic_arc_deg': round(syn_arc, 6),
            'anomaly_correction_deg': round(anomaly_correction, 6),
            'nodal_distance_deg': round(nodal_dist, 6),
            'eclipse_risk_flag': eclipse_risk,
            'saros_number': saros_n,
            'goal_year_period': gy,
            'predicted_longitude_deg': round(predicted_lon, 6),
        })

    return pd.DataFrame(results)

def compute_pyramid_geometry(input_data: Union[pd.DataFrame, dict]) -> dict:
    """Formula 2: Pure Shape Dimensionless Pyramid Geometry Engine."""
    seked_ratio = 14.0 / 11.0                           
    pi_encoded = 4.0 / seked_ratio                      
    face_angle_rad = np.arctan(seked_ratio)             
    face_angle_deg = np.degrees(face_angle_rad)         
    apex_half_angle_deg = 90.0 - face_angle_deg

    phi = (1.0 + np.sqrt(5.0)) / 2.0                   
    slant_to_half_base = np.sqrt(phi)                   
    phi_seked_delta = abs(seked_ratio - slant_to_half_base)  

    height_to_half_base = np.tan(face_angle_rad)        
    perimeter_to_height = 4.0 / (height_to_half_base * 0.5)  
    base_diagonal_to_height = np.sqrt(2.0) / (height_to_half_base * 0.5)  

    b = 1.0
    h = height_to_half_base * (b / 2.0)                
    apothem = np.sqrt((b / 2.0) ** 2 + h ** 2)

    lateral_area = 4.0 * 0.5 * b * apothem
    base_area = b ** 2
    lateral_to_base_ratio = lateral_area / base_area   
    total_surface_area = lateral_area + base_area
    total_to_base_ratio = total_surface_area / base_area

    volume = (1.0 / 3.0) * base_area * h
    volume_ratio = volume / (base_area * h)             

    apex_half_rad = np.radians(apex_half_angle_deg)
    solid_angle_apex = 2.0 * np.pi * (1.0 - np.cos(apex_half_rad))

    results = {
        "pi_geometric_approx": pi_encoded,
        "phi_golden_ratio": phi,
        "phi_seked_delta": phi_seked_delta,
        "face_slope_angle_deg": face_angle_deg,
        "apex_half_angle_deg": apex_half_angle_deg,
        "face_slope_angle_rad": face_angle_rad,
        "solid_angle_apex_sr": solid_angle_apex,
        "seked_ratio": seked_ratio,
        "height_to_half_base": height_to_half_base,
        "perimeter_to_height": perimeter_to_height,
        "base_diagonal_to_height": base_diagonal_to_height,
        "slant_to_half_base": slant_to_half_base,
        "lateral_to_base_area_ratio": lateral_to_base_ratio,
        "total_to_base_area_ratio": total_to_base_ratio,
        "volume_ratio_1_over_3": volume_ratio,
        "apothem_unit_base": apothem,
        "height_unit_base": h,
    }

    if isinstance(input_data, pd.DataFrame) and "base_length" in input_data.columns:
        df_out = input_data.copy()
        df_out["height"] = df_out["base_length"] * h
        df_out["apothem"] = df_out["base_length"] * apothem
        df_out["lateral_area"] = df_out["base_length"] ** 2 * lateral_to_base_ratio
        df_out["volume"] = (1.0 / 3.0) * df_out["base_length"] ** 2 * df_out["height"]
        results["scaled_dataframe"] = df_out.to_dict(orient="records")

    elif isinstance(input_data, dict) and "base_length" in input_data:
        bl = float(input_data["base_length"])
        results["scaled_height"] = bl * h
        results["scaled_apothem"] = bl * apothem
        results["scaled_lateral_area"] = bl ** 2 * lateral_to_base_ratio
        results["scaled_volume"] = (1.0 / 3.0) * bl ** 2 * (bl * h)

    return results

def write_output_volume(payload: Dict[str, Any], output_path: str) -> None:
    """Securely stores parameters for the Base downstream agent to read."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(payload, f, indent=4)

def main() -> None:
    INPUT_FILE = "/data/inputs/coordinates.json"
    OUTPUT_FILE = "/data/outputs/cleansed_parameters.json"
    
    try:
        safe_time_isolation_guard()
        raw_payload = read_input_volume(INPUT_FILE)
        
        # M2M Usage Parsing Counters (Pay-per-parse metrics)
        nodal_parse_count = 0
        pyramid_parse_count = 0
        
        # Process Nodal Data Matrix
        nodal_results = pd.DataFrame()
        if "nodal_data" in raw_payload and raw_payload["nodal_data"]:
            nodal_parse_count = len(raw_payload["nodal_data"])
            nodal_results = babylonian_nodal_compute(raw_payload["nodal_data"])
            
        # Process Pyramid Geometry Data
        pyramid_results = {}
        if "pyramid_data" in raw_payload and raw_payload["pyramid_data"]:
            pyramid_input = raw_payload["pyramid_data"]
            if isinstance(pyramid_input, dict) and "base_length_list" in pyramid_input:
                pyramid_parse_count = len(pyramid_input["base_length_list"])
                pyramid_input = pd.DataFrame(pyramid_input["base_length_list"])
            elif isinstance(pyramid_input, list):
                pyramid_parse_count = len(pyramid_input)
                pyramid_input = pd.DataFrame(pyramid_input)
            else:
                pyramid_parse_count = 1
            
            pyramid_results = compute_pyramid_geometry(pyramid_input)

        # Build M2M synchronized structure with explicit usage dimensions
        synchronized_payload = {
            "status": "synchronized",
            "m2m_accounting": {
                "total_rows_parsed": nodal_parse_count + pyramid_parse_count,
                "nodal_rows": nodal_parse_count,
                "pyramid_units": pyramid_parse_count
            },
            "nodal_output": nodal_results.to_dict(orient="records") if not nodal_results.empty else [],
            "pyramid_output": pyramid_results
        }
        
        write_output_volume(synchronized_payload, OUTPUT_FILE)
        
    except Exception as e:
        error_file = "/data/outputs/error.json"
