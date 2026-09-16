# Calibration Guide

## Why calibration matters

A WAV file stores digital sample amplitudes, not direct physical sound pressure. For a physically meaningful result, the system must know how those samples relate to pressure in Pascals.

Without calibration, the package can still compute useful relative signal-energy proxies, but it cannot truthfully report physical acoustic energy density in J/m³.

## Required information

To convert digital audio into physical pressure you need:
- microphone sensitivity (for example, mV/Pa or V/Pa)
- gain or recording-chain amplification information
- ADC or interface full-scale range and conversion settings
- explicit assumptions about the sound field, such as plane-wave conditions

## Common path to calibrated pressure

1. Load the WAV file into a NumPy array.
2. Convert digital amplitude to voltage using the ADC reference and full-scale range.
3. Convert voltage to pressure using the microphone sensitivity.
4. Apply the appropriate acoustic model if needed.

Example:

```python
import numpy as np
from scipy.io import wavfile

sample_rate, data = wavfile.read("recording.wav")
# Assume 16-bit PCM normalized to [-1, 1]
normalized = data.astype(np.float64) / 32768.0

# Example values for illustration only
adc_full_scale_vpp = 2.0
mic_sensitivity_v_per_pa = 0.05

volts = normalized * (adc_full_scale_vpp / 2.0)
pressure_pa = volts / mic_sensitivity_v_per_pa
```

This is a calibration workflow, not a one-click conversion. The exact values depend on hardware and recording chain configuration.

## Scientific caveat

For a plane progressive wave, pressure and particle velocity are related by:

$$ v = \frac{p}{\rho c} $$

and the total acoustic energy density becomes:

$$ w = \frac{p^2}{\rho c^2} $$

This holds only under the stated acoustic assumptions and with calibrated pressure data.

## Current package stance

The package currently reports relative or normalized energy metrics for uncalibrated digital audio. Those values are useful as signal proxies but should not be described as physical acoustic energy density without calibration.
