"""
cross_sensitivity.py
=====================
Applies cross-sensitivity matrix correction to isolate true gas readings.

Electrochemical cells are not perfectly selective:
  CO cell:  responds 100% to CO, -3% to NO2
  NO2 cell: responds 1.5% to CO, 100% to NO2

Without correction: 100 ppb NO2 spike falsely inflates CO by +0.033 ppm.

Cross-sensitivity matrix S:
    S = [[1.00, -0.03],
         [0.015, 1.00]]

True concentrations:
    [C_CO_true, C_NO2_true]^T = inv(S) * [C_CO_meas, C_NO2_meas]^T
"""

import numpy as np
import pandas as pd

# ─── CROSS-SENSITIVITY MATRIX ────────────────────────────────────────────────
# Row 0: CO cell response  — 100% to CO, -3% to NO2
# Row 1: NO2 cell response — 1.5% to CO, 100% to NO2
S_MATRIX = np.array([
    [1.000, -0.030],
    [0.015,  1.000]
])

S_INV = np.linalg.inv(S_MATRIX)

def apply_cross_sensitivity(df):
    """
    Applies inv(S) to corrected gas readings.
    Modifies C_CO_corrected and C_NO2_corrected in place.
    Returns updated dataframe.
    """
    C_CO  = df["C_CO_corrected"].values
    C_NO2 = df["C_NO2_corrected"].values

    # Stack into 2×N, apply inv(S_matrix) per sample
    raw_stack = np.vstack([C_CO, C_NO2])          # shape (2, N)
    corrected = S_INV @ raw_stack                  # matrix multiply (2, N)

    df["C_CO_corrected"]  = np.clip(corrected[0], 0, 100)
    df["C_NO2_corrected"] = np.clip(corrected[1], 0, 2000)

    return df

if __name__ == "__main__":
    from adc_model import process_all_channels
    from environmental_correction import apply_corrections

    df = pd.read_csv("data/scenario1_raw.csv")
    df = process_all_channels(df)
    df = apply_corrections(df)

    C_CO_before  = df["C_CO_corrected"].copy()
    C_NO2_before = df["C_NO2_corrected"].copy()

    df = apply_cross_sensitivity(df)

    print("=== Cross-Sensitivity Correction Effect ===")
    print(f"CO  mean shift : {(df['C_CO_corrected']  - C_CO_before).mean():.6f} ppm")
    print(f"NO2 mean shift : {(df['C_NO2_corrected'] - C_NO2_before).mean():.4f} ppb")
    print("\nS matrix inverse:")
    print(np.round(S_INV, 6))
