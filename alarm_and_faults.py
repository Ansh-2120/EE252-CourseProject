"""
alarm_and_faults.py
====================
Hysteresis alarm state machine + fault detection logic.

Alarm States: NORMAL → WARNING → ALARM (no direct NORMAL↔ALARM skip)

Hysteresis thresholds prevent relay chatter when AQI hovers at boundary.

Fault Codes:
  CO_SENSOR_FAULT    — CO voltage below minimum rail
  NO2_SENSOR_FAULT   — NO2 voltage below minimum rail
  CO_OVERRANGE       — CO voltage above ADC rail
  NO2_OVERRANGE      — NO2 voltage above ADC rail
  TEMP_OUT_OF_BOUNDS — Temperature outside -10°C to 60°C
  KALMAN_DIVERGE     — Kalman filter sanity bounds exceeded
  NONE               — no fault
"""

import numpy as np
import pandas as pd

# ─── ALARM THRESHOLDS ────────────────────────────────────────────────────────
AQI_WARN_ON    = 100
AQI_WARN_OFF   = 85
AQI_ALARM_ON   = 150
AQI_ALARM_OFF  = 130
R_WARN_ON      = 1.2
R_ALARM_ON     = 1.5
R_ALARM_OFF    = 1.3
R_WARN_OFF     = 1.0

# ─── FAULT THRESHOLDS ────────────────────────────────────────────────────────
V_MIN_RAIL     = 0.010   # V — below this = sensor fault
V_MAX_RAIL     = 3.400   # V — above this = overrange
T_MIN          = -10.0   # °C
T_MAX          =  60.0   # °C

# ─── HYSTERESIS STATE MACHINE ────────────────────────────────────────────────
def run_alarm_fsm(aqi_arr, risk_arr):
    """
    Finite state machine with hysteresis.
    States: 0=NORMAL, 1=WARNING, 2=ALARM
    Returns array of state labels.
    """
    n      = len(aqi_arr)
    states = np.zeros(n, dtype=int)
    state  = 0   # start NORMAL

    for k in range(n):
        aqi = aqi_arr[k]
        R   = risk_arr[k]

        if state == 0:   # NORMAL
            if aqi > AQI_ALARM_ON or R > R_ALARM_ON:
                state = 2
            elif aqi > AQI_WARN_ON or R > R_WARN_ON:
                state = 1

        elif state == 1:  # WARNING
            if aqi > AQI_ALARM_ON or R > R_ALARM_ON:
                state = 2
            elif aqi < AQI_WARN_OFF and R < R_WARN_OFF:
                state = 0

        elif state == 2:  # ALARM
            if aqi < AQI_ALARM_OFF and R < R_ALARM_OFF:
                state = 1
            # Cannot jump directly ALARM → NORMAL

        states[k] = state

    labels = {0: "NORMAL", 1: "WARNING", 2: "ALARM"}
    return np.array([labels[s] for s in states])

# ─── FAULT DETECTION ─────────────────────────────────────────────────────────
def detect_faults(df):
    """
    Checks raw voltages and temperature for fault conditions.
    Returns list of fault flag strings per sample.
    """
    n      = len(df)
    faults = []

    V_CO  = df["V_CO_raw"].values
    V_NO2 = df["V_NO2_raw"].values
    T     = df["T_raw"].values
    kdiv  = df.get("kalman_diverge",
                   pd.Series(np.zeros(n, dtype=bool))).values

    for i in range(n):
        f = []

        if V_CO[i] < V_MIN_RAIL:
            f.append("CO_SENSOR_FAULT")
        elif V_CO[i] > V_MAX_RAIL:
            f.append("CO_OVERRANGE")

        if V_NO2[i] < V_MIN_RAIL:
            f.append("NO2_SENSOR_FAULT")
        elif V_NO2[i] > V_MAX_RAIL:
            f.append("NO2_OVERRANGE")

        if T[i] < T_MIN or T[i] > T_MAX:
            f.append("TEMP_OUT_OF_BOUNDS")

        if kdiv[i]:
            f.append("KALMAN_DIVERGE")

        faults.append("|".join(f) if f else "NONE")

    return faults

# ─── MAIN FUNCTION ───────────────────────────────────────────────────────────
def apply_alarms_and_faults(df):
    """
    Adds alarm_state and fault_flags columns to dataframe.
    Uses Kalman AQI as primary alarm input.
    """
    aqi_k  = df["AQI_kalman"].values
    risk_k = df["risk_score_kalman"].values

    df["alarm_state"] = run_alarm_fsm(aqi_k, risk_k)
    df["fault_flags"] = detect_faults(df)

    return df

if __name__ == "__main__":
    from adc_model import process_all_channels
    from environmental_correction import apply_corrections
    from cross_sensitivity import apply_cross_sensitivity
    from kalman import apply_kalman
    from regression import train, apply_regression
    from aqi_engine import apply_aqi

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
    df = apply_alarms_and_faults(df)

    print("=== Alarm State Distribution (Scenario 2) ===")
    print(df["alarm_state"].value_counts())
    print("\n=== Fault Flags Distribution ===")
    print(df["fault_flags"].value_counts().head(10))
