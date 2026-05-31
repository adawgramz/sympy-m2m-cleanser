"""
babylonian_nodal_model.py
─────────────────────────────────────────────────────────────────────────────
Pure computation module – no I/O, no printing.
Designed to be imported by ocean_router.py and called with a pre-loaded
Pandas DataFrame.  Returns a DataFrame ready for Ocean's output writer.
 
Babylonian Systems implemented
──────────────────────────────
  System A  – step-function ("Zig-Zag") model for lunar / planetary longitude
  System B  – linear-zigzag (sawtooth) model for the same phenomena
  Saros     – eclipse cycle predictor (223 synodic months)
  Goal-Year – synodic period resonance table
  Nodal     – ascending / descending node longitudes + eclipse-limit test
  Synodic   – mean synodic arc for Moon, Sun, and the five classical planets
  Anomaly   – anomalistic correction (first & second difference tables)
  Visibility– first / last appearance latitude test (Arcus Visionis)
 
Reference frames use the Babylonian sidereal zodiac
(epoch approx -600, ayanamsha approx 4d30m subtracted from the tropical frame).
All angular quantities are in decimal degrees (0-360).
All time quantities are in tithis (1 tithi = 1/30 synodic month approx 0.9843 d).
"""
 
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
 
# =============================================================================
# 1.  CONSTANTS  (sourced from cuneiform tablet reconstructions)
# =============================================================================
 
AYANAMSHA: float = 4.5                    # tropical -> sidereal offset (deg)
MEAN_SYNODIC_MONTH: float = 29.530594     # days  (29;31,50,8,20 sexagesimal)
MEAN_ANOMALISTIC_MONTH: float = 27.554551 # days
MEAN_DRACONIC_MONTH: float = 27.212221    # days  (nodal period)
SAROS_SYNODIC: int = 223                  # synodic months per Saros
SAROS_DAYS: float = SAROS_SYNODIC * MEAN_SYNODIC_MONTH   # 6585.32 d
METONIC_SYNODIC: int = 235               # synodic months per Metonic cycle
 
# System A – step-function (fast/slow zone) parameters
SYS_A: Dict[str, float] = {
    "fast_arc":   30.0,    # F1 – monthly arc in fast zone (deg)
    "slow_arc":   28.0,    # F2 – monthly arc in slow zone (deg)
    "fast_limit": 180.0,   # ecliptic boundary of fast zone (deg)
    "slow_limit": 360.0,
}
 
# System B – linear zigzag parameters
SYS_B: Dict[str, float] = {
    "mean":      29.530594, # M – mean value (deg/month)
    "amplitude":  2.0,      # Delta – half-amplitude
    "delta":      0.36,     # d – step increment per synodic month
}
 
# Goal-year synodic periods (synodic months per complete synodic cycle)
GOAL_YEAR_PERIODS: Dict[str, int] = {
    "Moon":    1,
    "Sun":     12,
    "Mercury": 46,
    "Venus":   8,
    "Mars":    79,
    "Jupiter": 83,
    "Saturn":  57,
}
 
# Mean synodic arcs (degrees advanced per synodic month)
MEAN_SYNODIC_ARC: Dict[str, float] = {
    "Moon":    29.530594,
    "Sun":     360.0 / 12.368,
    "Mercury": 360.0 / 0.317,
    "Venus":   360.0 / 1.599,
    "Mars":    360.0 / 2.135,
    "Jupiter": 360.0 / 11.862,
    "Saturn":  360.0 / 29.458,
}
 
# Arcus Visionis – minimum elongation from Sun for first/last visibility (deg)
ARCUS_VISIONIS: Dict[str, float] = {
    "Mercury": 10.0,
    "Venus":    5.0,
    "Mars":    14.5,
    "Jupiter": 11.0,
    "Saturn":  13.0,
}
 
ECLIPSE_LIMIT_SOLAR: float = 18.5   # Moon must be within this of a node
ECLIPSE_LIMIT_LUNAR: float = 12.0
 
 
# =============================================================================
# 2.  LOW-LEVEL ALGEBRAIC PRIMITIVES
# =============================================================================
 
def _normalise(angle: float) -> float:
    """Reduce any angle to [0, 360)."""
    return angle % 360.0
 
 
def _system_a_arc(longitude: float) -> float:
    """
    System A step function.
    Returns the synodic arc F(lambda) for a given sidereal longitude.
 
    Algebraic rule:
        F(lambda) = F1   if  0 <= lambda < 180  (fast zone)
                  = F2   if 180 <= lambda < 360  (slow zone)
    """
    lon = _normalise(longitude)
    return SYS_A["fast_arc"] if lon < SYS_A["fast_limit"] else SYS_A["slow_arc"]
 
 
def _system_b_zigzag(n: int, phi_0: float = SYS_B["mean"]) -> float:
    """
    System B linear zigzag function.
    Returns the nth value of the zigzag sequence starting from phi_0.
 
    Algebraic recurrence:
        phi_{n+1} = phi_n + d    if ascending
        phi_{n+1} = phi_n - d    if descending
    Reflects at:
        phi_max = M + Delta
        phi_min = M - Delta
    """
    M   = SYS_B["mean"]
    amp = SYS_B["amplitude"]
    d   = SYS_B["delta"]
    phi_max = M + amp
    phi_min = M - amp
 
    phi = phi_0
    direction = 1   # +1 ascending, -1 descending
    for _ in range(abs(n)):
        phi += direction * d
        if phi >= phi_max:
            phi = 2 * phi_max - phi
            direction = -1
        elif phi <= phi_min:
            phi = 2 * phi_min - phi
            direction = 1
    return phi
 
 
def _nodal_longitude(jdn: float, node_epoch_jdn: float = 1448638.0,
                     node_epoch_long: float = 0.0) -> Tuple[float, float]:
    """
    Compute ascending and descending node longitudes at a given JDN.
 
    The ascending node regresses westward at:
        omega_dot = -360 / (nodal period in days)
                  = -360 / (18.6 * 365.25)
                  = -0.052954 deg/day
 
    Geometric model:
        Omega(t) = Omega_0 - omega_dot * (t - t0)   [mod 360]
 
    Returns
    -------
    (ascending_node_long, descending_node_long)  both in [0, 360)
    """
    NODAL_REGRESSION_RATE = 360.0 / (18.6 * 365.25)   # deg/day westward
    dt = jdn - node_epoch_jdn
    ascending  = _normalise(node_epoch_long - NODAL_REGRESSION_RATE * dt)
    descending = _normalise(ascending + 180.0)
    return ascending, descending
 
 
def _angular_distance_from_node(longitude: float,
                                 node_long: float) -> float:
    """
    Minimum angular distance between a body's ecliptic longitude
    and the nearest node (ascending or descending).
 
    Uses the half-circle fold:
        dist = min( |lambda - Omega| mod 360,
                    |lambda - (Omega+180)| mod 360 )
    then folded to [0, 180].
    """
    asc  = _normalise(node_long)
    desc = _normalise(node_long + 180.0)
    d1   = min(abs(longitude - asc),   360 - abs(longitude - asc))
    d2   = min(abs(longitude - desc),  360 - abs(longitude - desc))
    return min(d1, d2)
 
 
def _eclipse_flag(node_dist: float, eclipse_type: str = "lunar") -> int:
    """
    Babylonian eclipse-possibility test.
 
    Returns
    -------
    0 : no eclipse possible
    1 : eclipse possible (within outer limit)
    2 : eclipse certain  (within inner limit ~ half the outer)
    """
    limit = (ECLIPSE_LIMIT_LUNAR if eclipse_type == "lunar"
             else ECLIPSE_LIMIT_SOLAR)
    if node_dist <= limit / 2:
        return 2
    elif node_dist <= limit:
        return 1
    return 0
 
 
def _anomaly_correction(anomaly_index: int,
                         body: str = "Moon") -> Tuple[float, float]:
    """
    First and second difference anomaly correction tables.
 
    The Babylonian anomaly column (column Phi) uses a zigzag function
    whose amplitude and step are body-specific.  Here we implement the
    Moon's Column G (daily motion correction).
 
    col1 = first-difference correction  (additive, degrees)
    col2 = second-difference correction (additive, degrees)
 
    Approximate closed-form (derived from ACT tablet reconstructions):
        col1(n) = A1 * sin(2*pi*n / P_anom)
        col2(n) = A2 * sin(4*pi*n / P_anom)
 
    where P_anom = anomalistic period in synodic months.
    """
    PARAMS = {
        "Moon":    {"A1": 2.5,  "A2": 0.25,  "P": 13.944},
        "Sun":     {"A1": 1.0,  "A2": 0.05,  "P": 12.368},
        "Mercury": {"A1": 5.0,  "A2": 1.0,   "P": 46.0},
        "Venus":   {"A1": 1.5,  "A2": 0.15,  "P": 8.0},
        "Mars":    {"A1": 12.0, "A2": 3.0,   "P": 79.0},
        "Jupiter": {"A1": 5.5,  "A2": 0.5,   "P": 83.0},
        "Saturn":  {"A1": 6.0,  "A2": 0.8,   "P": 57.0},
    }
    p = PARAMS.get(body, PARAMS["Moon"])
    theta = 2.0 * np.pi * anomaly_index / p["P"]
    col1  = p["A1"] * np.sin(theta)
    col2  = p["A2"] * np.sin(2.0 * theta)
    return col1, col2
 
 
def _saros_series_index(jdn: float,
                         saros_epoch_jdn: float = 1448638.0) -> int:
    """
    Returns the Saros series number for a given JDN.
    Saros series repeat every SAROS_DAYS days.
 
        saros_n = floor( (jdn - epoch) / SAROS_DAYS )
    """
    return int(np.floor((jdn - saros_epoch_jdn) / SAROS_DAYS))
 
 
def _goal_year_residual(longitude: float,
                         body: str,
                         synodic_count: int) -> float:
    """
    Goal-Year residual arc.
 
    After GOAL_YEAR_PERIODS[body] synodic months the body nearly
    returns to the same ecliptic longitude.  The residual is:
 
        epsilon = lambda - ( lambda_0 + N * mean_arc )   [mod 360]
 
    This is the correction that Babylonian scribes tabulated and
    applied to extrapolate future positions.
    """
    N    = GOAL_YEAR_PERIODS.get(body, 1)
    arc  = MEAN_SYNODIC_ARC.get(body, 30.0)
    expected = _normalise(synodic_count * arc)
    residual  = _normalise(longitude - expected)
    if residual > 180:
        residual -= 360.0      # signed residual in (-180, 180]
    return residual
 
 
def _visibility_test(elongation: float, body: str,
                      latitude: float = 0.0) -> str:
    """
    Arcus Visionis test for first / last appearance.
 
    The body is visible if its elongation from the Sun exceeds the
    Arcus Visionis threshold (adjusted for ecliptic latitude):
 
        effective_elongation = sqrt(elongation^2 + latitude^2)
 
    Returns 'rising', 'setting', 'invisible', or 'n/a'.
    """
    if body not in ARCUS_VISIONIS:
        return "n/a"
    av = ARCUS_VISIONIS[body]
    eff = np.sqrt(elongation**2 + latitude**2)
    if eff < av:
        return "invisible"
    if elongation > 0:
        return "rising"
    return "setting"
 
 
# =============================================================================
# 3.  MAIN EXPORTED FUNCTION
# =============================================================================
 
def compute_babylonian_nodal_system(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the full Babylonian algebraic-geometric nodal model for every
    row in the input DataFrame.
 
    Input DataFrame – required columns
    ───────────────────────────────────
    jdn          : float  – Julian Day Number of the observation epoch
    body         : str    – celestial body name (see MEAN_SYNODIC_ARC keys)
    lambda_trop  : float  – tropical ecliptic longitude  (degrees 0-360)
    beta         : float  – ecliptic latitude             (degrees)
    elongation   : float  – angular distance from Sun     (degrees, signed:
                            positive = east of Sun / evening star,
                            negative = west  of Sun / morning star)
    synodic_n    : int    – synodic event count since reference epoch
    anomaly_n    : int    – anomalistic event count since reference epoch
 
    Optional columns (filled with defaults if absent)
    ──────────────────────────────────────────────────
    node_epoch_jdn  : float – JDN of the reference node epoch  (default 1448638.0)
    node_epoch_long : float – ascending node longitude at epoch (default 0.0)
 
    Output DataFrame – all input columns preserved, plus
    ─────────────────────────────────────────────────────
    lambda_sid      : float – sidereal longitude (tropical - AYANAMSHA)
    sys_a_arc       : float – System A synodic arc (deg/month)
    sys_b_arc       : float – System B zigzag arc  (deg/month)
    node_asc        : float – ascending node longitude  (deg)
    node_desc       : float – descending node longitude (deg)
    node_dist       : float – angular distance to nearest node (deg)
    eclipse_flag    : int   – 0/1/2 eclipse possibility code
    col1_anomaly    : float – first-difference anomaly correction  (deg)
    col2_anomaly    : float – second-difference anomaly correction (deg)
    lambda_corrected: float – sidereal longitude + anomaly corrections (deg)
    saros_n         : int   – Saros series index
    goal_year_res   : float – goal-year residual arc (deg, signed)
    visibility      : str   – 'rising' | 'setting' | 'invisible' | 'n/a'
    tithi           : float – elapsed tithis since J2000.0 epoch
    """
 
    REQUIRED_COLS = {"jdn", "body", "lambda_trop", "beta",
                     "elongation", "synodic_n", "anomaly_n"}
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Input DataFrame is missing columns: {missing}")
 
    # Work on a copy to avoid mutating caller's data
    out = df.copy()
 
    # Fill optional columns with defaults
    if "node_epoch_jdn"  not in out.columns:
        out["node_epoch_jdn"]  = 1448638.0
    if "node_epoch_long" not in out.columns:
        out["node_epoch_long"] = 0.0
 
    # J2000.0 = JDN 2451545.0 ; tithi denominator
    J2000 = 2451545.0
 
    # Vectorised computation row by row (dataset sizes are small for ephemeris)
    results = {
        "lambda_sid":       [],
        "sys_a_arc":        [],
        "sys_b_arc":        [],
        "node_asc":         [],
        "node_desc":        [],
        "node_dist":        [],
        "eclipse_flag":     [],
        "col1_anomaly":     [],
        "col2_anomaly":     [],
        "lambda_corrected": [],
        "saros_n":          [],
        "goal_year_res":    [],
        "visibility":       [],
        "tithi":            [],
    }
 
    for _, row in out.iterrows():
        jdn        = float(row["jdn"])
        body       = str(row["body"])
        lam_trop   = float(row["lambda_trop"])
        beta       = float(row["beta"])
        elongation = float(row["elongation"])
        syn_n      = int(row["synodic_n"])
        anom_n     = int(row["anomaly_n"])
        ne_jdn     = float(row["node_epoch_jdn"])
        ne_long    = float(row["node_epoch_long"])
 
        # 1. Sidereal longitude
        lam_sid = _normalise(lam_trop - AYANAMSHA)
 
        # 2. System A arc
        sa_arc = _system_a_arc(lam_sid)
 
        # 3. System B arc (zigzag at this synodic count)
        sb_arc = _system_b_zigzag(syn_n)
 
        # 4. Node longitudes
        node_asc, node_desc = _nodal_longitude(jdn, ne_jdn, ne_long)
 
        # 5. Distance from nearest node
        nd = _angular_distance_from_node(lam_sid, node_asc)
 
        # 6. Eclipse flag
        eclipse_type = "lunar" if body == "Moon" else "solar"
        ef = _eclipse_flag(nd, eclipse_type)
 
        # 7. Anomaly corrections
        c1, c2 = _anomaly_correction(anom_n, body)
 
        # 8. Corrected longitude
        lam_corr = _normalise(lam_sid + c1 + c2)
 
        # 9. Saros series
        sn = _saros_series_index(jdn, ne_jdn)
 
        # 10. Goal-year residual
        gy = _goal_year_residual(lam_sid, body, syn_n)
 
        # 11. Visibility
        vis = _visibility_test(elongation, body, beta)
 
        # 12. Elapsed tithis since J2000.0
        #     1 tithi = MEAN_SYNODIC_MONTH / 30 days
        tithi_len = MEAN_SYNODIC_MONTH / 30.0
        tithi     = (jdn - J2000) / tithi_len
 
        results["lambda_sid"].append(lam_sid)
        results["sys_a_arc"].append(sa_arc)
        results["sys_b_arc"].append(sb_arc)
        results["node_asc"].append(node_asc)
        results["node_desc"].append(node_desc)
        results["node_dist"].append(nd)
        results["eclipse_flag"].append(ef)
        results["col1_anomaly"].append(c1)
        results["col2_anomaly"].append(c2)
        results["lambda_corrected"].append(lam_corr)
        results["saros_n"].append(sn)
        results["goal_year_res"].append(gy)
        results["visibility"].append(vis)
        results["tithi"].append(tithi)
 
    for col, values in results.items():
        out[col] = values
 
    return out
 
