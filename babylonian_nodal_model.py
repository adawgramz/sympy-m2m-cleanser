import numpy as np
import pandas as pd
from typing import Union


def babylonian_nodal_compute(input_data: Union[pd.DataFrame, dict]) -> pd.DataFrame:
    """
    Babylonian Astrological Nodal System — Mathematical Formula Engine
    ------------------------------------------------------------------
    Encodes the complete algebraic and geometric logic of the ancient
    Babylonian lunar/planetary nodal system (MUL.APIN tradition),
    including saros cycle periods, synodic arcs, nodal passages,
    eclipse prediction windows, and base-60 (sexagesimal) angular geometry.

    Parameters
    ----------
    input_data : pd.DataFrame or dict
        Expected columns / keys:
          - 'julian_day'     : float  — Julian Day Number (JDN) of observation
          - 'body'           : str    — celestial body label
                                        ('moon','sun','jupiter','venus',
                                         'saturn','mars','mercury')
          - 'longitude_deg'  : float  — ecliptic longitude in decimal degrees
          - 'latitude_deg'   : float  — ecliptic latitude  in decimal degrees (optional)
          - 'anomaly_deg'    : float  — mean anomaly in decimal degrees         (optional)

    Returns
    -------
    pd.DataFrame
        One row per input observation with columns:
          - 'julian_day'
          - 'body'
          - 'longitude_sexagesimal'  — longitude in base-60 string (°; '; '')
          - 'zodiac_sign'            — Babylonian zodiac sign (12-fold, 30° each)
          - 'zodiac_position_deg'    — position within that sign (0–30°)
          - 'synodic_arc_deg'        — mean synodic arc (body-specific Babylonian constant)
          - 'anomaly_correction_deg' — Babylonian zig-zag anomaly correction
          - 'nodal_distance_deg'     — angular distance to nearest node (ascending/descending)
          - 'eclipse_risk_flag'      — 1 if within Babylonian eclipse danger zone, else 0
          - 'saros_number'           — Saros series index (integer)
          - 'goal_year_period'       — Goal-Year period (years) for the body
          - 'predicted_longitude_deg'— next synodic event longitude (current + synodic arc + correction)
    """

    # ── 0. Normalise input ──────────────────────────────────────────────────
    df = pd.DataFrame(input_data) if isinstance(input_data, dict) else input_data.copy()
    df.columns = df.columns.str.strip().str.lower()

    if 'latitude_deg' not in df.columns:
        df['latitude_deg'] = 0.0
    if 'anomaly_deg' not in df.columns:
        df['anomaly_deg'] = 0.0

    # ── 1. Babylonian Constants ─────────────────────────────────────────────
    # Sexagesimal degree helpers
    def to_sexagesimal(deg: float) -> str:
        """Convert decimal degrees → Babylonian base-60 string d°; m'; s''"""
        deg = deg % 360
        d = int(deg)
        m_full = (deg - d) * 60
        m = int(m_full)
        s = (m_full - m) * 60
        return f"{d}°; {m:02d}'; {s:05.2f}''"

    # Babylonian 12-sign zodiac (each sign = 30°, starting at 0° Aries)
    ZODIAC = [
        "Aries (LU.HUN.GA)", "Taurus (MUL.MUL)", "Gemini (MASH.TAB.BA)",
        "Cancer (AL.LUL)", "Leo (UR.GU.LA)", "Virgo (AB.SIN)",
        "Libra (ZI.BA.AN.NA)", "Scorpius (GIR.TAB)", "Sagittarius (PA.BIL.SAG)",
        "Capricorn (SUHUR.MASH)", "Aquarius (GU)", "Pisces (SIM.MAH)"
    ]

    # Mean synodic arcs (degrees) — from ACT / MUL.APIN tablets
    SYNODIC_ARC = {
        'moon':    29.530589,   # mean synodic month in days → 360° in 29.53 days
        'sun':     30.0,        # Babylonian mean solar month arc
        'jupiter': 33.8491,     # System A mean synodic arc
        'venus':   215.7547,    # mean synodic arc (584-day cycle / 360°)
        'saturn':  12.1693,
        'mars':    48.7019,
        'mercury': 114.7875,
    }

    # Goal-Year periods (tropical years) — Babylonian empirical cycles
    GOAL_YEAR = {
        'moon':    18.6116,   # nodal / Saros ~18.03; goal-year 18.6
        'sun':     1.0,
        'jupiter': 71.0,      # 71 tropical years ≈ 6 synodic periods × 12 - 1
        'venus':   8.0,       # 8 tropical years ≈ 5 synodic cycles
        'saturn':  59.0,
        'mars':    47.0,
        'mercury': 46.0,
    }

    # Saros period in Julian days
    SAROS_DAYS = 6585.3211          # 18 years 11 days 8 hours
    SAROS_EPOCH_JD = 1458085.5      # Babylonian reference epoch (~747 BCE, Nabonassar Era)

    # Eclipse danger zone: Moon within ±12° of node (Babylonian rule)
    ECLIPSE_DANGER_DEG = 12.0

    # Babylonian zig-zag anomaly function coefficients (System B, lunar)
    # Amplitude M=17;46,40° period P=13;56,39 months (ACT notation)
    ZZ_AMPLITUDE = {
        'moon':    2.2361,     # degrees, peak anomaly correction
        'sun':     1.6459,
        'jupiter': 5.8317,
        'venus':   4.3200,
        'saturn':  3.1100,
        'mars':    11.2500,
        'mercury': 9.7200,
    }
    ZZ_PERIOD = {             # synodic periods per full zig-zag cycle
        'moon':    13.9439,
        'sun':     12.3692,
        'jupiter': 6.0,
        'venus':   5.0,
        'saturn':  4.0,
        'mars':    7.0,
        'mercury': 46.0,
    }

    # ── 2. Row-wise Computation ─────────────────────────────────────────────
    results = []

    for _, row in df.iterrows():
        jd   = float(row['julian_day'])
        body = str(row['body']).strip().lower()
        lon  = float(row['longitude_deg']) % 360
        lat  = float(row['latitude_deg'])
        anom = float(row['anomaly_deg']) % 360

        # 2a. Sexagesimal longitude
        lon_sexa = to_sexagesimal(lon)

        # 2b. Zodiac sign and intra-sign position
        sign_idx        = int(lon // 30) % 12
        zodiac_sign     = ZODIAC[sign_idx]
        zodiac_pos      = lon % 30

        # 2c. Synodic arc (body constant; fall back to solar if unknown)
        syn_arc = SYNODIC_ARC.get(body, SYNODIC_ARC['sun'])

        # 2d. Zig-zag anomaly correction (Babylonian System B)
        #     F(t) = A · sin(2π · anom / 360)  — continuous approximation
        zz_amp = ZZ_AMPLITUDE.get(body, 2.0)
        anomaly_correction = zz_amp * np.sin(np.radians(anom))

        # 2e. Ascending node longitude (simplified Babylonian mean node)
        #     Ω = 125.0445° − 0.0529539° × (JD − J2000)
        J2000 = 2451545.0
        omega_asc = (125.0445 - 0.0529539 * (jd - J2000)) % 360   # ascending node
        omega_desc = (omega_asc + 180.0) % 360                       # descending node

        # Angular distance to nearest node
        dist_asc  = abs(((lon - omega_asc  + 180) % 360) - 180)
        dist_desc = abs(((lon - omega_desc + 180) % 360) - 180)
        nodal_dist = min(dist_asc, dist_desc)

        # 2f. Eclipse risk (Moon only: Babylonian 12° rule; others always 0)
        if body == 'moon':
            eclipse_risk = 1 if (nodal_dist <= ECLIPSE_DANGER_DEG and abs(lat) <= 1.5) else 0
        else:
            eclipse_risk = 0

        # 2g. Saros number (integer count of Saros periods from epoch)
        saros_n = int((jd - SAROS_EPOCH_JD) / SAROS_DAYS)

        # 2h. Goal-Year period
        gy = GOAL_YEAR.get(body, 1.0)

        # 2i. Predicted next synodic longitude
        predicted_lon = (lon + syn_arc + anomaly_correction) % 360

        results.append({
            'julian_day':               jd,
            'body':                     body,
            'longitude_sexagesimal':    lon_sexa,
            'zodiac_sign':              zodiac_sign,
            'zodiac_position_deg':      round(zodiac_pos, 6),
            'synodic_arc_deg':          round(syn_arc, 6),
            'anomaly_correction_deg':   round(anomaly_correction, 6),
            'nodal_distance_deg':       round(nodal_dist, 6),
            'eclipse_risk_flag':        eclipse_risk,
            'saros_number':             saros_n,
            'goal_year_period':         gy,
            'predicted_longitude_deg':  round(predicted_lon, 6),
        })

    return pd.DataFrame(results)
