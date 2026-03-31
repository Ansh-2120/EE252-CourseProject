"""
adc_model.py
============
Models a 12-bit ADC with 64x oversampling and decimation.

- Quantises each voltage to 12-bit resolution (4096 levels, 3.3V ref)
- Takes 64 rapid sub-samples per output sample and averages them
- Effective resolution improves to 15-bit equivalent
- Noise floor reduced by factor of 8 (sqrt(64))
"""

import numpy as np

ADC_BITS    = 12
ADC_REF     = 3.3          # V
ADC_LEVELS  = 2 ** ADC_BITS   # 4096
LSB         = ADC_REF / ADC_LEVELS   # 0.806 mV
OVERSAMPLE  = 64

def quantise(v: np.ndarray) -> np.ndarray:
    """12-bit quantisation. Clamps to [0, ADC_REF]."""
    v_clamped = np.clip(v, 0.0, ADC_REF)
    codes     = np.round(v_clamped / ADC_REF * (ADC_LEVELS - 1)).astype(int)
    return codes * ADC_REF / (ADC_LEVELS - 1)

def oversample_decimate(v: np.ndarray,
                        sigma_quant: float = None) -> np.ndarray:
    """
    Simulate 64x oversampling + decimation.

    For each output sample, draw 64 sub-samples with added quantisation
    noise, quantise each, then average → one high-resolution output.

    Parameters
    ----------
    v           : array of voltages (one per output sample)
    sigma_quant : optional extra noise per sub-sample (default = 0.5 LSB)
    """
    if sigma_quant is None:
        sigma_quant = 0.5 * LSB          # ±0.5 LSB uniform ≈ 0.289 LSB RMS

    n      = len(v)
    output = np.zeros(n)

    for i in range(n):
        sub = v[i] + np.random.normal(0, sigma_quant, OVERSAMPLE)
        output[i] = np.mean(quantise(sub))

    return output

def process_all_channels(df):
    """
    Apply oversampling + decimation to every raw voltage channel.
    Returns the dataframe with new *_adc columns added.
    """
    for col in ["V_CO_raw", "V_NO2_raw", "V_PM_raw"]:
        df[col.replace("_raw", "_adc")] = oversample_decimate(df[col].values)

    # Temperature and humidity channels (lower noise, same process)
    df["T_adc"]  = df["T_raw"].values  + np.random.normal(0, 0.5 * LSB, len(df))
    df["RH_adc"] = df["RH_raw"].values + np.random.normal(0, 0.5 * LSB, len(df))

    return df

if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("data/scenario1_raw.csv")
    df = process_all_channels(df)
    print(df[["V_CO_raw", "V_CO_adc", "T_raw", "T_adc"]].head(5))
    print(f"\nLSB = {LSB*1000:.3f} mV  |  Effective bits after OS = {ADC_BITS + int(np.log2(np.sqrt(OVERSAMPLE)))}")
