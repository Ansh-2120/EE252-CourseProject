"""
environmental_correction.py
============================
Applies temperature and humidity correction to raw ADC voltages,
converting them to physically meaningful concentrations.

Mathematical models derived in Phase 1:
  CO  : C_CO  = (V_CO/Rf_CO  - I_zero_CO)  / (S_CO  * K_T_CO  * K_RH_CO)
  NO2 : C_NO2 = (V_NO2/Rf_NO2 - I_zero_NO2) / (S_NO2 * K_T_NO2 * K_RH_NO2)
  PM  : PM    = (V_PM / G_PM) / (f_hygro * f_temp_PM)
"""

import numpy as np
import pandas as pd

# ─── AFE CONSTANTS ────────────────────────────────────────────────────────────
Rf_CO      = 750e3
Rf_NO2     = 2e6
S_CO       = 90e-9      # A/ppm
S_NO2      = 0.8e-9     # A/ppb
I_zero_CO  = 40e-9      # A
I_zero_NO2 = 100e-9     # A
G_PM       = 6.6e-3     # V per ug/m3

T_REF      = 20.0       # °C reference
RH_REF     = 50.0       # %  reference

# ─── CORRECTION COEFFICIENTS (from Phase 1) ───────────────────────────────────
ALPHA_T_CO   = -0.005   # per °C
ALPHA_RH_CO  =  0.003   # per %RH
ALPHA_T_NO2  = -0.008
ALPHA_RH_NO2 =  0.005
BETA_HYGRO   =  0.025   # per %RH above 65%
ALPHA_T_PM   =  0.002

# ─── CORRECTION FACTOR FUNCTIONS ─────────────────────────────────────────────
def K_T_CO(T):
    return 1 + ALPHA_T_CO * (T - T_REF)

def K_RH_CO(RH):
    return 1 + ALPHA_RH_CO * (RH - RH_REF)

def K_T_NO2(T):
    return 1 + ALPHA_T_NO2 * (T - T_REF)

def K_RH_NO2(RH):
    return 1 + ALPHA_RH_NO2 * (RH - RH_REF)

def f_hygro(RH):
    return np.where(RH > 65, 1 + BETA_HYGRO * (RH - 65), 1.0)

def f_temp_PM(T):
    return 1 + ALPHA_T_PM * (T - T_REF)

# ─── CORRECTION FUNCTIONS ────────────────────────────────────────────────────
def correct_CO(V_CO_adc, T, RH):
    I_measured = V_CO_adc / Rf_CO
    C_raw      = (I_measured - I_zero_CO) / S_CO
    K          = K_T_CO(T) * K_RH_CO(RH)
    K          = np.where(np.abs(K) < 1e-6, 1e-6, K)   # guard divide-by-zero
    return np.clip(C_raw / K, 0, 100)                   # ppm, physical bounds

def correct_NO2(V_NO2_adc, T, RH):
    I_measured = V_NO2_adc / Rf_NO2
    C_raw      = (I_measured - I_zero_NO2) / S_NO2
    K          = K_T_NO2(T) * K_RH_NO2(RH)
    K          = np.where(np.abs(K) < 1e-6, 1e-6, K)
    return np.clip(C_raw / K, 0, 2000)                  # ppb

def correct_PM(V_PM_adc, T, RH):
    PM_raw = V_PM_adc / G_PM
    F      = f_hygro(RH) * f_temp_PM(T)
    F      = np.where(np.abs(F) < 1e-6, 1e-6, F)
    return np.clip(PM_raw / F, 0, 600)                  # ug/m3

def apply_corrections(df):
    """
    Takes dataframe with *_adc columns and T_adc, RH_adc.
    Adds corrected concentration columns.
    """
    T  = df["T_adc"].values
    RH = df["RH_adc"].values

    df["C_CO_corrected"]  = correct_CO(df["V_CO_adc"].values,  T, RH)
    df["C_NO2_corrected"] = correct_NO2(df["V_NO2_adc"].values, T, RH)
    df["PM_corrected"]    = correct_PM(df["V_PM_adc"].values,   T, RH)

    return df

if __name__ == "__main__":
    from adc_model import process_all_channels
    df = pd.read_csv("data/scenario1_raw.csv")
    df = process_all_channels(df)
    df = apply_corrections(df)

    print("\n=== Environmental Correction Results (first 5 samples) ===")
    cols = ["C_CO_true", "C_CO_corrected", "C_NO2_true", "C_NO2_corrected"]
    print(df[cols].head(5).to_string(index=False))

    rmse_co = np.sqrt(np.mean((df["C_CO_corrected"] - df["C_CO_true"])**2))
    print(f"\nRMSE CO  after env correction: {rmse_co:.4f} ppm")
