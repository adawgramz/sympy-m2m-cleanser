import numpy as np
import pandas as pd
from typing import Union


def compute_pyramid_geometry(input_data: Union[pd.DataFrame, dict]) -> dict:
    """
    Derives and validates the intrinsic geometric ratios and constants
    embedded in a right-square pyramid, using only dimensionless relationships
    and universal mathematical constants.

    No human-scale measurements are used. All values are expressed as
    pure ratios, angles, and mathematical constants observable from the
    structure's own proportional geometry.
    """

    # -------------------------------------------------------------------------
    # SECTION 1 — PURE GEOMETRIC CONSTANTS DERIVED FROM STRUCTURE PROPORTIONS
    # -------------------------------------------------------------------------

    # Apothem-to-half-base ratio (slope ratio of the face)
    # Observed seked: rise=5.5 palms per cubit of run → ratio = 14/11
    seked_ratio = 14.0 / 11.0                           # ≈ 1.2727...

    # This ratio encodes PI: 4 / seked_ratio ≈ π
    pi_encoded = 4.0 / seked_ratio                      # ≈ 3.14285...

    # Face slope angle (in radians and degrees)
    face_angle_rad = np.arctan(seked_ratio)             # apothem angle to base
    face_angle_deg = np.degrees(face_angle_rad)         # ≈ 51.84°

    # Apex half-angle (complement of face angle)
    apex_half_angle_deg = 90.0 - face_angle_deg

    # -------------------------------------------------------------------------
    # SECTION 2 — GOLDEN RATIO RELATIONSHIP
    # -------------------------------------------------------------------------

    phi = (1.0 + np.sqrt(5.0)) / 2.0                   # Golden ratio ≈ 1.6180...

    # Slant height to half-base ratio encodes phi²
    # slant_height / half_base = sqrt(phi)  (observed geometric relationship)
    slant_to_half_base = np.sqrt(phi)                   # ≈ 1.2720...

    # Cross-check: deviation between seked-derived slope and phi-derived slope
    phi_seked_delta = abs(seked_ratio - slant_to_half_base)  # ≈ 0.0007 (near-identity)

    # -------------------------------------------------------------------------
    # SECTION 3 — DIMENSIONLESS STRUCTURAL RATIOS (pure shape descriptors)
    # -------------------------------------------------------------------------

    # height-to-base ratio derived from face angle
    # If base = 1 unit, height = tan(face_angle) * 0.5  (apothem geometry)
    # Normalised: height / base_half = tan(face_angle_rad)
    height_to_half_base = np.tan(face_angle_rad)        # ≈ seked_ratio

    # Perimeter-to-height ratio  →  encodes 2π
    # perimeter = 4 * base; height = base * height_to_half_base / 0.5
    # perimeter / height = 4 / (height_to_half_base / 0.5 * 0.5)
    # Simplified with unit base = 1:
    perimeter_to_height = 4.0 / (height_to_half_base * 0.5)  # ≈ 2π (6.2832...)

    # Diagonal of base (unit square) to height ratio
    base_diagonal_to_height = np.sqrt(2.0) / (height_to_half_base * 0.5)

    # -------------------------------------------------------------------------
    # SECTION 4 — SURFACE & VOLUME RATIOS (shape-only, unit-normalised)
    # -------------------------------------------------------------------------

    # Normalised to base = 1 unit
    b = 1.0
    h = height_to_half_base * (b / 2.0)                # height from seked ratio

    # Apothem (slant height of triangular face)
    apothem = np.sqrt((b / 2.0) ** 2 + h ** 2)

    # Lateral face area / base area  (dimensionless)
    lateral_area = 4.0 * 0.5 * b * apothem
    base_area    = b ** 2
    lateral_to_base_ratio = lateral_area / base_area   # ≈ 1.468...

    # Total surface area / base area
    total_surface_area = lateral_area + base_area
    total_to_base_ratio = total_surface_area / base_area

    # Volume / (base_area * height)  — for a pyramid = 1/3
    volume = (1.0 / 3.0) * base_area * h
    volume_ratio = volume / (base_area * h)             # always 1/3 by definition

    # Solid angle at apex (steradians)
    # Ω = 2π(1 − cos(apex_half_angle))
    apex_half_rad = np.radians(apex_half_angle_deg)
    solid_angle_apex = 2.0 * np.pi * (1.0 - np.cos(apex_half_rad))

    # -------------------------------------------------------------------------
    # SECTION 5 — PROCESS INPUT DATA (scale ratios to any provided base length)
    # -------------------------------------------------------------------------

    results = {
        # --- Universal constants encoded in the geometry ---
        "pi_geometric_approx":       pi_encoded,
        "phi_golden_ratio":          phi,
        "phi_seked_delta":           phi_seked_delta,

        # --- Angles ---
        "face_slope_angle_deg":      face_angle_deg,
        "apex_half_angle_deg":       apex_half_angle_deg,
        "face_slope_angle_rad":      face_angle_rad,
        "solid_angle_apex_sr":       solid_angle_apex,

        # --- Dimensionless ratios ---
        "seked_ratio":               seked_ratio,
        "height_to_half_base":       height_to_half_base,
        "perimeter_to_height":       perimeter_to_height,
        "base_diagonal_to_height":   base_diagonal_to_height,
        "slant_to_half_base":        slant_to_half_base,

        # --- Surface / volume ratios (unit base = 1) ---
        "lateral_to_base_area_ratio": lateral_to_base_ratio,
        "total_to_base_area_ratio":   total_to_base_ratio,
        "volume_ratio_1_over_3":      volume_ratio,
        "apothem_unit_base":          apothem,
        "height_unit_base":           h,
    }

    # If caller passes a DataFrame or dict with a 'base_length' column/key,
    # scale the derived lengths proportionally and attach as extra columns.
    if isinstance(input_data, pd.DataFrame) and "base_length" in input_data.columns:
        df_out = input_data.copy()
        df_out["height"]          = df_out["base_length"] * h
        df_out["apothem"]         = df_out["base_length"] * apothem
        df_out["lateral_area"]    = df_out["base_length"] ** 2 * lateral_to_base_ratio
        df_out["volume"]          = (1.0 / 3.0) * df_out["base_length"] ** 2 * df_out["height"]
        results["scaled_dataframe"] = df_out

    elif isinstance(input_data, dict) and "base_length" in input_data:
        bl = float(input_data["base_length"])
        results["scaled_height"]       = bl * h
        results["scaled_apothem"]      = bl * apothem
        results["scaled_lateral_area"] = bl ** 2 * lateral_to_base_ratio
        results["scaled_volume"]       = (1.0 / 3.0) * bl ** 2 * (bl * h)

    return results
