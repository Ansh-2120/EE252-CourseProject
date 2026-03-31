"""
logger.py
=========
Writes final structured CSV output with all channels, both algorithm
outputs, AQI scores, alarm state, fault flags, and rolling RMSE.

Output columns follow the schema defined in Phase 3 planning.
"""

import numpy as np
import pandas as pd
import os

OUTPUT_DIR  = "data"
RMSE_WINDOW = 60    # rolling RMSE window in samples

def rolling_rmse(estimated, true_vals, window=RMSE_WINDOW):
    """Compute rolling RMSE over a sliding window."""
    n      = len(estimated)
    result = np.full(n, np.nan)
    for i in range(window - 1, n):
        err        = estimated[i-window+1:i+1] - true_vals[i-window+1:i+1]
        result[i]  = np.sqrt(np.mean(err ** 2))
    return result

def compute_comparison_metrics(df):
    """
    Compute RMSE and MAE for both algorithms vs ground truth.
    Returns dict of metric name → value.
    """
    metrics = {}

    for gas, true_col, k_col, r_col in [
        ("CO",  "C_CO_true",  "C_CO_kalman",  "C_CO_regression"),
        ("NO2", "C_NO2_true", "C_NO2_kalman", "C_NO2_regression"),
        ("PM",  "PM_true",    "PM_kalman",    "PM_regression"),
    ]:
        true = df[true_col].values
        k    = df[k_col].values
        r    = df[r_col].values

        metrics[f"RMSE_{gas}_kalman"]      = np.sqrt(np.mean((k - true)**2))
        metrics[f"RMSE_{gas}_regression"]  = np.sqrt(np.mean((r - true)**2))
        metrics[f"MAE_{gas}_kalman"]       = np.mean(np.abs(k - true))
        metrics[f"MAE_{gas}_regression"]   = np.mean(np.abs(r - true))

    return metrics

def save_output(df, scenario_id):
    """
    Selects and orders output columns, computes rolling RMSE,
    saves to data/scenarioN_output.csv
    """
    # Rolling RMSE columns
    df["RMSE_CO_kalman"]     = rolling_rmse(df["C_CO_kalman"].values,
                                             df["C_CO_true"].values)
    df["RMSE_CO_regression"] = rolling_rmse(df["C_CO_regression"].values,
                                             df["C_CO_true"].values)

    output_cols = [
        "timestamp", "scenario",
        "V_CO_raw", "V_NO2_raw", "V_PM_raw", "T_raw", "RH_raw",
        "T_adc", "RH_adc",
        "C_CO_corrected", "C_NO2_corrected", "PM_corrected",
        "C_CO_kalman",    "C_NO2_kalman",    "PM_kalman",
        "C_CO_regression","C_NO2_regression", "PM_regression",
        "C_CO_true",      "C_NO2_true",       "PM_true",
        "AQI_CO_kalman",  "AQI_NO2_kalman",  "AQI_PM_kalman",
        "AQI_kalman",     "risk_score_kalman","category_kalman",
        "AQI_regression", "risk_score_regression",
        "alarm_state", "fault_flags",
        "kalman_diverge",
        "RMSE_CO_kalman", "RMSE_CO_regression",
    ]

    # Only keep columns that exist
    existing = [c for c in output_cols if c in df.columns]
    out_df   = df[existing].copy()

    filepath = os.path.join(OUTPUT_DIR, f"scenario{scenario_id}_output.csv")
    out_df.to_csv(filepath, index=False, float_format="%.6f")
    print(f"[✓] Saved {filepath}  ({len(out_df)} rows, {len(existing)} columns)")

    return out_df

def print_summary(df, scenario_id, metrics):
    print(f"\n{'='*55}")
    print(f"  SCENARIO {scenario_id} SUMMARY")
    print(f"{'='*55}")
    print(f"  Samples          : {len(df)}")
    print(f"  Alarm NORMAL     : {(df['alarm_state']=='NORMAL').sum()}")
    print(f"  Alarm WARNING    : {(df['alarm_state']=='WARNING').sum()}")
    print(f"  Alarm ALARM      : {(df['alarm_state']=='ALARM').sum()}")
    print(f"  Faults detected  : {(df['fault_flags']!='NONE').sum()}")
    print(f"\n  RMSE (Kalman vs Regression):")
    for gas in ["CO", "NO2", "PM"]:
        rk = metrics[f"RMSE_{gas}_kalman"]
        rr = metrics[f"RMSE_{gas}_regression"]
        print(f"    {gas:4s}: Kalman={rk:.4f}  Regression={rr:.4f}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    from adc_model import process_all_channels
    from environmental_correction import apply_corrections
    from cross_sensitivity import apply_cross_sensitivity
    from kalman import apply_kalman
    from regression import train, apply_regression
    from aqi_engine import apply_aqi
    from alarm_and_faults import apply_alarms_and_faults

    df_train = pd.read_csv("data/scenario1_raw.csv")
    df_train = process_all_channels(df_train)
    df_train = apply_corrections(df_train)
    df_train = apply_cross_sensitivity(df_train)
    coef     = train(df_train)

    for sid in [1, 2, 3]:
        df = pd.read_csv(f"data/scenario{sid}_raw.csv")
        df = process_all_channels(df)
        df = apply_corrections(df)
        df = apply_cross_sensitivity(df)
        df = apply_kalman(df)
        df = apply_regression(df, coef)
        df = apply_aqi(df)
        df = apply_alarms_and_faults(df)
        m  = compute_comparison_metrics(df)
        save_output(df, sid)
        print_summary(df, sid, m)
