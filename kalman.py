"""
kalman.py
==========
Algorithm A — Extended Kalman Filter (EKF) for sensor fusion.

State vector:  x = [C_CO (ppm), C_NO2 (ppb), PM2.5 (ug/m3)]
Process model: random walk  x[k] = x[k-1] + w[k],  w ~ N(0, Q)
Measurement:   z[k] = x[k] + v[k],                  v ~ N(0, R)

Q/R ratio determines speed vs smoothness trade-off.
Sanity bounds guard against physically impossible states.
"""

import numpy as np
import pandas as pd

# ─── FILTER PARAMETERS ───────────────────────────────────────────────────────
# Process noise Q — how much we expect the true value to vary per sample
Q = np.diag([
    0.5,    # CO  (ppm^2)
    5.0,    # NO2 (ppb^2)
    2.0,    # PM  (ug/m3)^2
])

# Measurement noise R — derived from ADC noise referred back to concentration
R = np.diag([
    (0.028) ** 2,   # CO  variance  (ppm^2)
    (0.50)  ** 2,   # NO2 variance  (ppb^2)
    (1.00)  ** 2,   # PM  variance  (ug/m3)^2
])

# State transition matrix (identity = random walk model)
F = np.eye(3)
H = np.eye(3)   # measurement matrix (direct observation)
I = np.eye(3)

# ─── PHYSICAL SANITY BOUNDS ──────────────────────────────────────────────────
BOUNDS = [
    (0.0, 100.0),     # CO   ppm
    (0.0, 2000.0),    # NO2  ppb
    (0.0, 600.0),     # PM   ug/m3
]

def run_kalman(z_co, z_no2, z_pm):
    """
    Run Kalman filter over measurement sequences.

    Parameters
    ----------
    z_co, z_no2, z_pm : 1-D arrays of corrected measurements

    Returns
    -------
    x_co, x_no2, x_pm : filtered state estimates
    innovations        : array (N, 3) of innovation signals
    diverge_flags      : boolean array (N,) — True when bounds exceeded
    """
    n = len(z_co)
    Z = np.vstack([z_co, z_no2, z_pm]).T   # (N, 3)

    # Storage
    x_out       = np.zeros((n, 3))
    innovations = np.zeros((n, 3))
    diverge     = np.zeros(n, dtype=bool)

    # Initialise
    x_post = Z[0].copy()
    P_post = R.copy()

    for k in range(n):
        # ── PREDICT ──────────────────────────────────────────────────────────
        x_prior = F @ x_post
        P_prior = F @ P_post @ F.T + Q

        # ── UPDATE ───────────────────────────────────────────────────────────
        z_k    = Z[k]
        innov  = z_k - H @ x_prior
        S_k    = H @ P_prior @ H.T + R
        K_k    = P_prior @ H.T @ np.linalg.inv(S_k)

        x_post = x_prior + K_k @ innov
        P_post = (I - K_k @ H) @ P_prior

        innovations[k] = innov

        # ── SANITY BOUNDS ────────────────────────────────────────────────────
        flag = False
        for i, (lo, hi) in enumerate(BOUNDS):
            if x_post[i] < lo or x_post[i] > hi:
                x_post[i] = z_k[i]     # revert to raw measurement
                flag = True
        diverge[k] = flag

        x_out[k] = np.clip(x_post, [b[0] for b in BOUNDS],
                                    [b[1] for b in BOUNDS])

    return x_out[:, 0], x_out[:, 1], x_out[:, 2], innovations, diverge

def apply_kalman(df):
    """Run Kalman filter on dataframe corrected measurements."""
    co_k, no2_k, pm_k, innov, div = run_kalman(
        df["C_CO_corrected"].values,
        df["C_NO2_corrected"].values,
        df["PM_corrected"].values
    )
    df["C_CO_kalman"]    = co_k
    df["C_NO2_kalman"]   = no2_k
    df["PM_kalman"]      = pm_k
    df["kalman_diverge"] = div
    return df

if __name__ == "__main__":
    from adc_model import process_all_channels
    from environmental_correction import apply_corrections
    from cross_sensitivity import apply_cross_sensitivity

    df = pd.read_csv("data/scenario1_raw.csv")
    df = process_all_channels(df)
    df = apply_corrections(df)
    df = apply_cross_sensitivity(df)
    df = apply_kalman(df)

    rmse_co  = np.sqrt(np.mean((df["C_CO_kalman"]  - df["C_CO_true"]) **2))
    rmse_no2 = np.sqrt(np.mean((df["C_NO2_kalman"] - df["C_NO2_true"])**2))
    rmse_pm  = np.sqrt(np.mean((df["PM_kalman"]    - df["PM_true"])   **2))

    print("=== Kalman Filter RMSE (Scenario 1) ===")
    print(f"  CO  : {rmse_co:.4f} ppm")
    print(f"  NO2 : {rmse_no2:.4f} ppb")
    print(f"  PM  : {rmse_pm:.4f} ug/m3")
    print(f"  Divergence events: {df['kalman_diverge'].sum()}")
