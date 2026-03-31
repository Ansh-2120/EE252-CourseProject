"""
regression.py
=============
Algorithm B — Polynomial Regression + Rolling Baseline Correction.

Model:
  C_est = a0 + a1*V + a2*T + a3*RH + a4*V*T + a5*V*RH + a6*T^2 + a7*RH^2

Coefficients fitted offline using Scenario 1 (training data).
Rolling baseline tracks slow zero-drift and subtracts it.

Training / inference split ensures fair comparison with Kalman Filter.
"""

import numpy as np
import pandas as pd

# ─── ROLLING BASELINE PARAMETERS ─────────────────────────────────────────────
ALPHA_BASELINE = 0.9999     # very slow — time constant ≈ 2.8 hours at 1Hz

# ─── FEATURE BUILDER ─────────────────────────────────────────────────────────
def build_features(V, T, RH):
    """
    Builds 8-feature polynomial matrix for one channel.
    φ = [1, V, T, RH, V*T, V*RH, T^2, RH^2]
    """
    n    = len(V)
    ones = np.ones(n)
    return np.column_stack([ones, V, T, RH, V*T, V*RH, T**2, RH**2])

def fit_coefficients(Phi, y):
    """Ordinary least squares: a = (Φ^T Φ)^-1 Φ^T y"""
    return np.linalg.lstsq(Phi, y, rcond=None)[0]

# ─── ROLLING BASELINE ────────────────────────────────────────────────────────
def rolling_baseline(C_est, alpha=ALPHA_BASELINE):
    """
    Exponential moving average baseline tracker.
    Drift-corrected output = C_est - (baseline - baseline[0])
    """
    n        = len(C_est)
    baseline = np.zeros(n)
    baseline[0] = C_est[0]

    for k in range(1, n):
        baseline[k] = alpha * baseline[k-1] + (1 - alpha) * C_est[k]

    drift         = baseline - baseline[0]
    C_corrected   = C_est - drift
    return C_corrected, baseline

# ─── TRAIN MODEL ─────────────────────────────────────────────────────────────
def train(df_train):
    """
    Fit regression coefficients for CO, NO2, PM using Scenario 1 data.
    Returns coefficient dictionary.
    """
    V_CO  = df_train["V_CO_adc"].values
    V_NO2 = df_train["V_NO2_adc"].values
    V_PM  = df_train["V_PM_adc"].values
    T     = df_train["T_adc"].values
    RH    = df_train["RH_adc"].values

    coef = {}
    coef["CO"]  = fit_coefficients(build_features(V_CO,  T, RH),
                                   df_train["C_CO_true"].values)
    coef["NO2"] = fit_coefficients(build_features(V_NO2, T, RH),
                                   df_train["C_NO2_true"].values)
    coef["PM"]  = fit_coefficients(build_features(V_PM,  T, RH),
                                   df_train["PM_true"].values)
    return coef

# ─── INFERENCE ───────────────────────────────────────────────────────────────
def predict(df, coef):
    """Apply fitted coefficients to any scenario dataframe."""
    V_CO  = df["V_CO_adc"].values
    V_NO2 = df["V_NO2_adc"].values
    V_PM  = df["V_PM_adc"].values
    T     = df["T_adc"].values
    RH    = df["RH_adc"].values

    C_CO_raw,  bl_co  = rolling_baseline(build_features(V_CO,  T, RH) @ coef["CO"])
    C_NO2_raw, bl_no2 = rolling_baseline(build_features(V_NO2, T, RH) @ coef["NO2"])
    C_PM_raw,  bl_pm  = rolling_baseline(build_features(V_PM,  T, RH) @ coef["PM"])

    df["C_CO_regression"]  = np.clip(C_CO_raw,  0, 100)
    df["C_NO2_regression"] = np.clip(C_NO2_raw, 0, 2000)
    df["PM_regression"]    = np.clip(C_PM_raw,  0, 600)

    return df

def apply_regression(df, coef):
    return predict(df, coef)

if __name__ == "__main__":
    from adc_model import process_all_channels
    from environmental_correction import apply_corrections
    from cross_sensitivity import apply_cross_sensitivity

    # Train on Scenario 1
    df_train = pd.read_csv("data/scenario1_raw.csv")
    df_train = process_all_channels(df_train)
    df_train = apply_corrections(df_train)
    df_train = apply_cross_sensitivity(df_train)
    coef     = train(df_train)
    df_train = apply_regression(df_train, coef)

    rmse_co  = np.sqrt(np.mean((df_train["C_CO_regression"]  - df_train["C_CO_true"]) **2))
    rmse_no2 = np.sqrt(np.mean((df_train["C_NO2_regression"] - df_train["C_NO2_true"])**2))
    rmse_pm  = np.sqrt(np.mean((df_train["PM_regression"]    - df_train["PM_true"])   **2))

    print("=== Regression RMSE (Scenario 1 — training set) ===")
    print(f"  CO  : {rmse_co:.4f} ppm")
    print(f"  NO2 : {rmse_no2:.4f} ppb")
    print(f"  PM  : {rmse_pm:.4f} ug/m3")
    print(f"  Coefficients CO: {np.round(coef['CO'], 6)}")
