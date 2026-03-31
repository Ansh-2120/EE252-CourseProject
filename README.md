# EE252 — Multi-Factor Urban AQI Monitoring System

A comprehensive urban air quality monitoring system that integrates analog front-end (AFE) simulations, edge processing algorithms, and a real-time dashboard. This project models multi-gas sensors (CO, NO₂, PM), applies environmental corrections, and compares Kalman filtering vs. polynomial regression for AQI computation.

## Features

- **Analog Front-End Simulations**: LTspice models for CO electrochemical, temperature (PT100 RTD), and optical PM channels.
- **Edge Processing Pipeline**: ADC modeling, environmental correction, cross-sensitivity compensation, and dual algorithm comparison (Kalman Filter vs. Polynomial Regression).
- **AQI Engine**: EPA-compliant AQI calculation with risk scoring.
- **Fault Detection**: Hysteresis-based alarm FSM and fault logging.
- **Interactive Dashboard**: React-based web interface for visualizing sensor data, AQI metrics, and algorithm comparisons.
- **Synthetic Data Generation**: Realistic urban scenarios including nominal conditions, pollution spikes, and edge cases.

## Project Structure

```
EE252-CourseProject/
│
├── EE252-File1-COChannel.asc          # LTspice — CO electrochemical AFE
├── EE252-File2-TempChannel.asc        # LTspice — RTD temperature AFE
├── EE252-File3-PMChannel.asc          # LTspice — Optical PM AFE
│
├── synthetic_data_gen.py              # Generates raw sensor CSVs (3 scenarios)
├── adc_model.py                       # 12-bit ADC + 64x oversampling/decimation
├── environmental_correction.py        # Temperature + humidity compensation
├── cross_sensitivity.py               # Cross-sensitivity matrix correction
├── kalman.py                          # Algorithm A — Extended Kalman Filter
├── regression.py                      # Algorithm B — Polynomial Regression
├── aqi_engine.py                      # EPA AQI computation + risk scoring
├── alarm_and_faults.py                # Hysteresis FSM + fault detection
├── logger.py                          # Structured CSV output + metrics
├── main_pipeline.py                   # Single entry point — runs everything
│
├── package.json                       # Node.js dependencies and scripts
├── vite.config.js                     # Vite configuration
├── tailwind.config.js                 # Tailwind CSS configuration
├── postcss.config.js                  # PostCSS configuration
├── index.html                         # Main HTML file for dashboard
│
├── src/                               # React dashboard source
│   ├── App.jsx                        # Main app component
│   ├── main.jsx                       # Entry point
│   ├── index.css                      # Global styles
│   ├── components/                    # Reusable components
│   │   ├── AQIGauge.jsx               # AQI gauge visualization
│   │   ├── TimeSeriesChart.jsx        # Time series charts
│   │   ├── ComparisonTable.jsx        # Algorithm comparison table
│   │   └── ...                        # Other components
│   ├── pages/                         # Dashboard pages
│   │   ├── Overview.jsx               # Main overview page
│   │   ├── GasChannels.jsx            # Gas channel details
│   │   └── ...                        # Other pages
│   └── utils/                         # Utility functions
│       ├── csvLoader.js               # CSV data loading
│       └── aqiColors.js               # AQI color schemes
│
├── public/                            # Static assets
│   └── data/                          # Processed CSV data for dashboard
│
└── data/                              # Generated data files
    ├── scenario1_raw.csv              # Nominal urban (3600 samples)
    ├── scenario2_raw.csv              # Pollution spike (1800 samples)
    ├── scenario3_raw.csv              # Edge cases (900 samples)
    ├── scenario1_output.csv           # Processed output — Scenario 1
    ├── scenario2_output.csv           # Processed output — Scenario 2
    ├── scenario3_output.csv           # Processed output — Scenario 3
    └── comparison_metrics.csv         # Kalman vs Regression RMSE/MAE table
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- LTspice XVII (for circuit simulations)

### Backend (Python Pipeline)

1. Install Python dependencies:
   ```bash
   pip install numpy pandas
   ```

### Frontend (Dashboard)

1. Install Node.js dependencies:
   ```bash
   npm install
   ```

## Usage

### Running the Complete Pipeline

To generate synthetic data, process it through the full pipeline, and save outputs:

```bash
python main_pipeline.py
```

This will:
- Generate raw sensor data for 3 scenarios
- Apply ADC modeling, environmental corrections, and cross-sensitivity compensation
- Run both Kalman Filter and Polynomial Regression algorithms
- Compute AQI and risk scores
- Detect alarms and faults
- Save processed CSVs to the `data/` folder

### Running Individual Modules

```bash
python synthetic_data_gen.py      # Generate raw data only
python adc_model.py               # Test ADC module
python kalman.py                  # Test Kalman filter
python regression.py              # Test regression algorithm
python logger.py                  # Run pipeline + save outputs
```

### Running the Dashboard

1. Ensure the pipeline has been run to generate data files.
2. Start the development server:
   ```bash
   npm run dev
   ```
3. Open your browser to `http://localhost:5173` (default Vite port).

The dashboard provides:
- Real-time AQI visualization
- Time series charts for all sensors
- Algorithm comparison metrics
- Fault logs and alarm status

### LTspice Simulations

Open each `.asc` file in LTspice XVII to run simulations:

| File | Channel | Key Simulations |
|------|---------|-----------------|
| EE252-File1-COChannel.asc | CO electrochemical | Transient, AC sweep, Monte Carlo |
| EE252-File2-TempChannel.asc | PT100 RTD bridge | DC linearity, AC sweep |
| EE252-File3-PMChannel.asc | Optical PM | Pulse capture, 3 scenarios, AC sweep |

## System Architecture

```
Physical World
  CO gas + NO₂ gas + PM particles + Temperature + Humidity
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
  [Module 3: Dashboard — React/Vite]
  Interactive visualization + real-time monitoring
```

## Algorithm Comparison (Scenario 2 — Pollution Spike)

| Metric | Kalman Filter | Polynomial Regression |
|--------|--------------|----------------------|
| CO RMSE (ppm) | 4.38 | 1.79 |
| NO₂ RMSE (ppb) | 16.57 | 47.48 |
| PM RMSE (μg/m³) | 2.94 | 7.06 |
| Compute (μs/sample) | ~72 | ~72 |

**Kalman Filter**: Better on dynamic scenarios, handles sudden changes well.  
**Polynomial Regression**: Better on trained conditions, lower computational complexity.

## Sensors Modeled

| Sensor | Type | Output | Range |
|--------|------|--------|-------|
| CO cell | Electrochemical | 40–4540 nA | 0–50 ppm |
| NO₂ cell | Electrochemical | 100–1700 nA | 0–2000 ppb |
| PT100 RTD | Resistive bridge | 96–123 Ω | -10–60°C |
| Capacitive RH | Voltage ratiometric | 0.5–3.5 V | 5–95% RH |
| Optical PM | Laser scatter | 0–500 nA pulses | 0–500 μg/m³ |

## AQI Standards Used

- **EPA AQI**: Piecewise linear formula for air quality index calculation.
- **WHO Guidelines**: Urban air quality thresholds for health-based limits.
- **NIOSH Limits**: Occupational exposure limits for CO.
- **Composite Risk Score**: R = 0.35×(AQI_CO/100) + 0.35×(AQI_NO₂/100) + 0.30×(AQI_PM/100)

## Contributors

- **Ansh Agarwal** - 240102120
- **Parate Aditya Nitin** - 240102123
- **Tarun Gupta** - 240102257

---

*EE252 Electronics and Communication Engineering Project*
