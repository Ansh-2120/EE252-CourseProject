"""
main_pipeline.py
================
Single entry point. Runs the complete EE252 AQI sensor fusion pipeline.

Execution order:
  1. Generate synthetic raw CSVs (all 3 scenarios)
  2. ADC model — quantisation + oversampling
  3. Environmental correction (T + RH compensation)
  4. Cross-sensitivity matrix correction
  5. Algorithm A — Kalman Filter
  6. Algorithm B — Polynomial Regression + Rolling Baseline
  7. AQI computation (EPA standard)
  8. Alarm FSM + Fault detection
  9. Logger — save structured output CSVs

Outputs:
  data/scenario1_raw.csv     data/scenario1_output.csv
  data/scenario2_raw.csv     data/scenario2_output.csv
  data/scenario3_raw.csv     data/scenario3_output.csv
  comparison_metrics.csv     (algorithm comparison table)

Project: EE252 Multi-Factor Urban AQI Monitoring System
"""

import time
import numpy as np
import pandas as pd
import os

# ─── PIPELINE IMPORTS ────────────────────────────────────────────────────────
from synthetic_data_gen    import scenario1, scenario2, scenario3
from adc_model             import process_all_channels
from environmental_correction import apply_corrections
from cross_sensitivity     import apply_cross_sensitivity
from kalman                import apply_kalman
from regression            import train, apply_regression
from aqi_engine            import apply_aqi
from alarm_and_faults      import apply_alarms_and_faults
from logger                import save_output, compute_comparison_metrics, print_summary

def run():
    total_start = time.perf_counter()
    print("\n" + "="*60)
    print("  EE252 — Multi-Factor AQI Sensor Fusion Pipeline")
    print("="*60)

    # ── STEP 1: Generate raw scenario CSVs ───────────────────────────────────
    print("\n[STEP 1] Generating synthetic sensor data...")
    scenario1()
    scenario2()
    scenario3()

    # ── STEP 2: Train regression on Scenario 1 ───────────────────────────────
    print("\n[STEP 2] Training regression model on Scenario 1...")
    df_train = pd.read_csv("data/scenario1_raw.csv")
    df_train = process_all_channels(df_train)
    df_train = apply_corrections(df_train)
    df_train = apply_cross_sensitivity(df_train)
    coef     = train(df_train)
    print(f"  Regression coefficients fitted for CO, NO2, PM channels.")

    # ── STEP 3-8: Process all three scenarios ─────────────────────────────────
    all_metrics = {}

    for sid in [1, 2, 3]:
        print(f"\n[STEP 3-8] Processing Scenario {sid}...")
        t0 = time.perf_counter()

        df = pd.read_csv(f"data/scenario{sid}_raw.csv")

        # ADC model
        df = process_all_channels(df)

        # Environmental correction
        df = apply_corrections(df)

        # Cross-sensitivity
        df = apply_cross_sensitivity(df)

        # Algorithm A — Kalman
        df = apply_kalman(df)

        # Algorithm B — Regression
        df = apply_regression(df, coef)

        # AQI
        df = apply_aqi(df)

        # Alarm + Faults
        df = apply_alarms_and_faults(df)

        # Log compute time per sample
        t1       = time.perf_counter()
        elapsed  = (t1 - t0) * 1e6 / len(df)   # microseconds per sample

        # Save output
        metrics  = compute_comparison_metrics(df)
        metrics["compute_us_per_sample"] = elapsed
        all_metrics[f"scenario{sid}"] = metrics
        save_output(df, sid)
        print_summary(df, sid, metrics)
        print(f"  Compute time: {elapsed:.2f} μs/sample")

    # ── STEP 9: Save comparison metrics CSV ───────────────────────────────────
    print("\n[STEP 9] Saving algorithm comparison metrics...")
    rows = []
    for scen, m in all_metrics.items():
        row = {"scenario": scen}
        row.update(m)
        rows.append(row)
    metrics_df = pd.DataFrame(rows)
    metrics_df.to_csv("data/comparison_metrics.csv", index=False, float_format="%.6f")
    print("[✓] Saved data/comparison_metrics.csv")

    # ── FINAL SUMMARY ─────────────────────────────────────────────────────────
    total_time = time.perf_counter() - total_start
    print("\n" + "="*60)
    print(f"  Pipeline complete in {total_time:.2f} seconds")
    print("  Output files:")
    for f in sorted(os.listdir("data")):
        size = os.path.getsize(f"data/{f}") / 1024
        print(f"    data/{f}  ({size:.1f} KB)")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
