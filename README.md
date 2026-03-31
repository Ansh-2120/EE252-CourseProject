# EE252 — Multi-Factor Urban AQI Monitoring System
## Project Directory

---

## Directory Structure

```
project/
│
├── EE252-File1-COChannel.asc          LTspice — CO electrochemical AFE
├── EE252-File2-TempChannel.asc        LTspice — RTD temperature AFE
├── EE252-File3-PMChannel.asc          LTspice — Optical PM AFE
│
├── synthetic_data_gen.py              Generates raw sensor CSVs (3 scenarios)
├── adc_model.py                       12-bit ADC + 64x oversampling/decimation
├── environmental_correction.py        Temperature + humidity compensation
├── cross_sensitivity.py               Cross-sensitivity matrix correction
├── kalman.py                          Algorithm A — Extended Kalman Filter
├── regression.py                      Algorithm B — Polynomial Regression
├── aqi_engine.py                      EPA AQI computation + risk scoring
├── alarm_and_faults.py                Hysteresis FSM + fault detection
├── logger.py                          Structured CSV output + metrics
├── main_pipeline.py                   Single entry point — runs everything
│
└── data/
    ├── scenario1_raw.csv              Nominal urban (3600 samples)
    ├── scenario2_raw.csv              Pollution spike (1800 samples)
    ├── scenario3_raw.csv              Edge cases (900 samples)
    ├── scenario1_output.csv           Processed output — Scenario 1
    ├── scenario2_output.csv           Processed output — Scenario 2
    ├── scenario3_output.csv           Processed output — Scenario 3
    └── comparison_metrics.csv         Kalman vs Regression RMSE/MAE table
```

---

## How to Run

### Requirements
```
pip install numpy pandas
```

### Run Complete Pipeline
```
python main_pipeline.py
```

This generates all raw CSVs, processes them through the full pipeline,
and saves output CSVs to the data/ folder.

### Run Individual Modules
```
python synthetic_data_gen.py      # Generate raw data only
python adc_model.py               # Test ADC module
python kalman.py                  # Test Kalman filter
python logger.py                  # Run pipeline + save outputs
```

---

## LTspice Simulations

Open each .asc file in LTspice XVII.

| File | Channel | Key Simulations |
|------|---------|-----------------|
| EE252-File1-COChannel.asc | CO electrochemical | Transient, AC sweep, Monte Carlo |
| EE252-File2-TempChannel.asc | PT100 RTD bridge | DC linearity, AC sweep |
| EE252-File3-PMChannel.asc | Optical PM | Pulse capture, 3 scenarios, AC sweep |

---

## System Architecture

```
Physical World
  CO gas + NO2 gas + PM particles + Temperature + Humidity
       │
  [Module 1: AFE — LTspice]
  TIA + Bridge + INA + Sallen-Key LPF (3 channels)
       │
  [Module 2: Edge Processing — Python]
  ADC model → Env correction → Cross-sensitivity
       │
  ┌────┴────┐
  Kalman    Regression     ← compared side by side
  Filter    + Baseline
  └────┬────┘
       │
  AQI Engine (EPA standard)
       │
  Alarm FSM + Fault Detection
       │
  Structured CSV Output
       │
  [Module 4: Dashboard — Phase 4]
```

---

## Algorithm Comparison (Scenario 2 — Pollution Spike)

| Metric | Kalman Filter | Polynomial Regression |
|--------|--------------|----------------------|
| CO RMSE (ppm) | 4.38 | 1.79 |
| NO2 RMSE (ppb) | 16.57 | 47.48 |
| PM RMSE (ug/m3) | 2.94 | 7.06 |
| Compute (μs/sample) | ~72 | ~72 |

**Kalman Filter** — better on dynamic scenarios, handles sudden changes
**Regression** — better on trained conditions, lower complexity

---

## Sensors Modelled

| Sensor | Type | Output | Range |
|--------|------|--------|-------|
| CO cell | Electrochemical | 40–4540 nA | 0–50 ppm |
| NO2 cell | Electrochemical | 100–1700 nA | 0–2000 ppb |
| PT100 RTD | Resistive bridge | 96–123 Ω | -10–60°C |
| Capacitive RH | Voltage ratiometric | 0.5–3.5 V | 5–95% RH |
| Optical PM | Laser scatter | 0–500 nA pulses | 0–500 μg/m³ |

---

## AQI Standards Used

- EPA AQI piecewise linear formula
- WHO urban air quality guidelines for thresholds
- NIOSH occupational exposure limits for CO
- Composite risk score R = 0.35×(AQI_CO/100) + 0.35×(AQI_NO2/100) + 0.30×(AQI_PM/100)

---

*EE252 Electronics and Communication Engineering Project*
