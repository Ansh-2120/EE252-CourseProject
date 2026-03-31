"""
synthetic_data_gen.py
=====================
Generates three realistic scenario CSVs simulating raw ADC output
from the multi-factor AQI sensor array AFE chain.

Outputs:
    data/scenario1_raw.csv  - Nominal urban conditions
    data/scenario2_raw.csv  - Pollution spike event
    data/scenario3_raw.csv  - Edge cases / stress test
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
os.makedirs("data", exist_ok=True)

# ─── AFE CHAIN CONSTANTS (from Phase 1 & Phase 2) ───────────────────────────
Rf_CO      = 750e3      # TIA feedback resistor CO
Rf_NO2     = 2e6        # TIA feedback resistor NO2
S_CO       = 90e-9      # A/ppm  CO sensitivity
S_NO2      = 0.8e-9     # A/ppb  NO2 sensitivity
I_zero_CO  = 40e-9      # A      CO zero current
I_zero_NO2 = 100e-9     # A      NO2 zero current
G_PM       = 6.6e-3     # V per ug/m3  PM AFE gain

# ─── NOISE PARAMETERS ────────────────────────────────────────────────────────
sigma_CO   = 15e-3      # V  Gaussian noise CO channel
sigma_NO2  = 20e-3      # V  Gaussian noise NO2 channel
sigma_PM   = 10e-3      # V  Gaussian noise PM channel
sigma_T    = 0.5        # °C noise on temperature
sigma_RH   = 1.0        # %  noise on humidity

# ─── ENVIRONMENTAL COEFFICIENT MODELS ────────────────────────────────────────
def K_T_CO(T):
    return 1 - 0.005 * (T - 20)

def K_RH_CO(RH):
    return 1 + 0.003 * (RH - 50)

def K_T_NO2(T):
    return 1 - 0.008 * (T - 20)

def K_RH_NO2(RH):
    return 1 + 0.005 * (RH - 50)

def f_hygro(RH):
    return np.where(RH > 65, 1 + 0.025 * (RH - 65), 1.0)

def f_temp_PM(T):
    return 1 + 0.002 * (T - 20)

# ─── VOLTAGE GENERATOR ───────────────────────────────────────────────────────
def generate_voltages(C_CO, C_NO2, PM, T, RH, n):
    """Convert true concentrations + environment → raw AFE voltages."""
    I_CO  = (S_CO  * C_CO  * K_T_CO(T)  * K_RH_CO(RH)  + I_zero_CO)
    I_NO2 = (S_NO2 * C_NO2 * K_T_NO2(T) * K_RH_NO2(RH) + I_zero_NO2)

    V_CO_raw  = I_CO  * Rf_CO  + np.random.normal(0, sigma_CO,  n)
    V_NO2_raw = I_NO2 * Rf_NO2 + np.random.normal(0, sigma_NO2, n)
    V_PM_raw  = PM * f_hygro(RH) * f_temp_PM(T) * G_PM \
                + np.random.normal(0, sigma_PM, n)

    T_raw  = T  + 0.01 * np.arange(n) + np.random.normal(0, sigma_T,  n)
    RH_raw = RH + np.random.normal(0, sigma_RH, n)

    return V_CO_raw, V_NO2_raw, V_PM_raw, T_raw, RH_raw

def save_csv(filename, t, V_CO, V_NO2, V_PM, T_raw, RH_raw,
             C_CO_true, C_NO2_true, PM_true, scenario_id):
    df = pd.DataFrame({
        "timestamp":    t,
        "scenario":     scenario_id,
        "V_CO_raw":     V_CO,
        "V_NO2_raw":    V_NO2,
        "V_PM_raw":     V_PM,
        "T_raw":        T_raw,
        "RH_raw":       RH_raw,
        "C_CO_true":    C_CO_true,
        "C_NO2_true":   C_NO2_true,
        "PM_true":      PM_true,
    })
    df.to_csv(filename, index=False)
    print(f"[✓] Saved {filename}  ({len(df)} samples)")

# ─── SCENARIO 1: NOMINAL URBAN ────────────────────────────────────────────────
def scenario1():
    n   = 3600
    t   = np.arange(n, dtype=float)
    T   = np.full(n, 25.0)
    RH  = np.full(n, 55.0)

    C_CO  = 5 + 3  * np.sin(2 * np.pi * t / 3600)          # 2–8 ppm
    C_NO2 = 50 + 30 * np.sin(2 * np.pi * t / 3600 + 0.3)   # 20–80 ppb
    PM    = 20 + 15 * np.sin(2 * np.pi * t / 1800)          # 5–35 ug/m3

    V_CO, V_NO2, V_PM, T_raw, RH_raw = generate_voltages(C_CO, C_NO2, PM, T, RH, n)
    save_csv("data/scenario1_raw.csv", t, V_CO, V_NO2, V_PM,
             T_raw, RH_raw, C_CO, C_NO2, PM, 1)

# ─── SCENARIO 2: POLLUTION SPIKE ─────────────────────────────────────────────
def scenario2():
    n   = 1800
    t   = np.arange(n, dtype=float)

    T   = 20 + (18 / 1800) * t                              # 20→38°C ramp
    RH  = 70 - (30 / 1800) * t                              # 70→40% drop

    C_CO  = np.where(t < 600, 5.0, np.where(t < 1200, 30.0, 5.0))
    C_NO2 = np.where(t < 600, 30.0, np.where(t < 1200, 180.0, 30.0))
    PM    = np.where(t < 600, 15.0, np.where(t < 1200, 200.0, 15.0))

    V_CO, V_NO2, V_PM, T_raw, RH_raw = generate_voltages(C_CO, C_NO2, PM, T, RH, n)
    save_csv("data/scenario2_raw.csv", t, V_CO, V_NO2, V_PM,
             T_raw, RH_raw, C_CO, C_NO2, PM, 2)

# ─── SCENARIO 3: EDGE CASES ───────────────────────────────────────────────────
def scenario3():
    n   = 900
    t   = np.arange(n, dtype=float)

    T   = -5 + (10 / 900) * t                               # -5→5°C
    RH  = 88 + 7 * np.sin(2 * np.pi * t / 300)             # 88–95%

    C_CO  = 10 + 1  * np.sin(2 * np.pi * t / 60)           # 9–11 ppm
    C_NO2 = 200 + 50 * np.sin(2 * np.pi * t / 90)          # 150–250 ppb
    PM    = 50 + 20 * np.cumsum(np.random.normal(0, 0.05, n))
    PM    = np.clip(PM, 30, 70)

    V_CO, V_NO2, V_PM, T_raw, RH_raw = generate_voltages(C_CO, C_NO2, PM, T, RH, n)
    save_csv("data/scenario3_raw.csv", t, V_CO, V_NO2, V_PM,
             T_raw, RH_raw, C_CO, C_NO2, PM, 3)

if __name__ == "__main__":
    print("Generating synthetic sensor data...")
    scenario1()
    scenario2()
    scenario3()
    print("All scenario CSVs generated successfully.")
