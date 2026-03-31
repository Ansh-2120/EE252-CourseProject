"""
aqi_engine.py
=============
Computes EPA standard Air Quality Index (AQI) from compensated
gas and PM concentrations.

Uses piecewise linear interpolation per EPA formula:
  AQI = ((AQI_hi - AQI_lo) / (C_hi - C_lo)) * (C - C_lo) + AQI_lo

Composite AQI = max(AQI_CO, AQI_NO2, AQI_PM25)
Composite risk score R = weighted sum (holistic alarm basis)
"""

import numpy as np
import pandas as pd

# ─── EPA AQI BREAKPOINTS ──────────────────────────────────────────────────────
# Format: (C_lo, C_hi, AQI_lo, AQI_hi)

BP_CO = [                   # ppm, 8-hour average
    (0.0,  4.4,   0,  50),
    (4.5,  9.4,  51, 100),
    (9.5, 12.4, 101, 150),
    (12.5, 15.4, 151, 200),
    (15.5, 30.4, 201, 300),
    (30.5, 50.4, 301, 500),
]

BP_NO2 = [                  # ppb, 1-hour average
    (0,    53,   0,  50),
    (54,  100,  51, 100),
    (101, 360, 101, 150),
    (361, 649, 151, 200),
    (650, 1249, 201, 300),
    (1250, 2049, 301, 500),
]

BP_PM25 = [                 # ug/m3, 24-hour average
    (0.0,  12.0,   0,  50),
    (12.1,  35.4,  51, 100),
    (35.5,  55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 500.4, 301, 500),
]

# ─── COMPOSITE RISK WEIGHTS ───────────────────────────────────────────────────
W_CO  = 0.35
W_NO2 = 0.35
W_PM  = 0.30

AQI_CATEGORIES = [
    (0,   50,  "Good"),
    (51,  100, "Moderate"),
    (101, 150, "Unhealthy for Sensitive Groups"),
    (151, 200, "Unhealthy"),
    (201, 300, "Very Unhealthy"),
    (301, 500, "Hazardous"),
]

# ─── CORE AQI FORMULA ────────────────────────────────────────────────────────
def _aqi_single(C, breakpoints):
    """Compute AQI for a single scalar concentration value."""
    for (C_lo, C_hi, AQI_lo, AQI_hi) in breakpoints:
        if C_lo <= C <= C_hi:
            return ((AQI_hi - AQI_lo) / (C_hi - C_lo)) * (C - C_lo) + AQI_lo
    if C < breakpoints[0][0]:
        return 0
    return 500   # above highest breakpoint → hazardous

def aqi_array(C_arr, breakpoints):
    """Vectorised AQI calculation over array."""
    return np.array([_aqi_single(c, breakpoints) for c in C_arr])

def get_category(aqi_val):
    for lo, hi, label in AQI_CATEGORIES:
        if lo <= aqi_val <= hi:
            return label
    return "Hazardous"

# ─── MAIN FUNCTION ───────────────────────────────────────────────────────────
def compute_aqi(df, suffix="_kalman"):
    """
    Computes AQI and risk score for a given algorithm suffix.
    suffix = '_kalman' or '_regression'
    """
    co_col  = f"C_CO{suffix}"
    no2_col = f"C_NO2{suffix}"
    pm_col  = f"PM{suffix}"

    AQI_CO  = aqi_array(df[co_col].values,  BP_CO)
    AQI_NO2 = aqi_array(df[no2_col].values, BP_NO2)
    AQI_PM  = aqi_array(df[pm_col].values,  BP_PM25)

    AQI_composite = np.maximum(np.maximum(AQI_CO, AQI_NO2), AQI_PM)
    R_score       = W_CO * (AQI_CO/100) + W_NO2 * (AQI_NO2/100) + W_PM * (AQI_PM/100)

    tag = suffix.strip("_")
    df[f"AQI_CO_{tag}"]        = AQI_CO
    df[f"AQI_NO2_{tag}"]       = AQI_NO2
    df[f"AQI_PM_{tag}"]        = AQI_PM
    df[f"AQI_{tag}"]           = AQI_composite
    df[f"risk_score_{tag}"]    = R_score
    df[f"category_{tag}"]      = [get_category(v) for v in AQI_composite]

    return df

def apply_aqi(df):
    df = compute_aqi(df, suffix="_kalman")
    df = compute_aqi(df, suffix="_regression")
    return df

if __name__ == "__main__":
    from adc_model import process_all_channels
    from environmental_correction import apply_corrections
    from cross_sensitivity import apply_cross_sensitivity
    from kalman import apply_kalman
    from regression import train, apply_regression

    df_train = pd.read_csv("data/scenario1_raw.csv")
    df_train = process_all_channels(df_train)
    df_train = apply_corrections(df_train)
    df_train = apply_cross_sensitivity(df_train)
    coef     = train(df_train)

    df = pd.read_csv("data/scenario2_raw.csv")
    df = process_all_channels(df)
    df = apply_corrections(df)
    df = apply_cross_sensitivity(df)
    df = apply_kalman(df)
    df = apply_regression(df, coef)
    df = apply_aqi(df)

    print("=== AQI Scenario 2 Summary ===")
    print(df[["AQI_kalman", "AQI_regression", "category_kalman"]].describe())
    print(f"\nMax AQI (Kalman):     {df['AQI_kalman'].max():.1f}")
    print(f"Max AQI (Regression): {df['AQI_regression'].max():.1f}")
