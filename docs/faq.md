# 🎵 Symphonic-Joules

> Where Sound Meets Science.

## Current Status

Symphonic-Joules is an early-stage Python project with a working foundation for audio loading, waveform processing, and relative signal-energy analysis. The package is not yet a complete calibrated acoustic measurement system, and results from the audio-energy functions should be treated as signal proxies unless sound-pressure calibration has been applied.

### Implemented today
- ✅ Python package structure under `src/symphonic_joules/`
- ✅ Audio file loading and saving with NumPy, Librosa, and SoundFile
- ✅ Peak normalization, mono conversion, and signal framing
- ✅ Basic physics helpers for kinetic and potential energy
- ✅ Relative audio-energy proxies for frame-wise and spectral analysis
- ✅ Pytest-based validation and Ruff linting setup

### Planned / future work
- 🔄 Microphone calibration support and conversion from digital samples to Pascals
- 🔄 Real-time audio processing
- 🔄 Multi-format support beyond WAV
- 🔄 Plugin architecture and extensibility work
- 🔄 More rigorous scientific validation and benchmark datasets
- 🔄 Visualization, dashboards, and notebook tooling

This project currently provides a solid scientific and engineering foundation for audio analysis, but not yet a fully calibrated acoustics platform.

---

## The Science That Powers It

We analyze sound through the acoustic energy density equation, which governs how sound carries energy through space:

$$ w = \frac{p^2}{2\rho c^2} + \frac{\rho v^2}{2} $$

Where:
* $w$ = acoustic energy density ($\text{J}/\text{m}^3$)
* $p$ = sound pressure ($\text{Pa}$)
* $\rho$ = medium density ($\text{kg}/\text{m}^3$)
* $c$ = speed of sound ($\text{m}/\text{s}$)
* $v$ = particle velocity ($\text{m}/\text{s}$)

This equation is valid for calibrated acoustic quantities. Raw WAV sample amplitudes are digital representations, not direct physical pressure values. For uncalibrated audio, the package reports relative signal-energy proxies rather than claiming physical energy density in J/m³.

---

## 🚀 Quick Start

**Prerequisites:** Python 3.8+ (3.11 recommended for macOS)

```bash
# 1. Clone the repository
git clone https://github.com/JaclynCodes/Symphonic-Joules-a67272a4.git
cd Symphonic-Joules-a67272a4

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install the package
pip install -e .
```

### Quick API Preview

```python
from symphonic_joules import load_audio, frame_mean_square

# Load an audio file
y, sr, metadata = load_audio("birdsong.wav", sr=22050)

# Compute a relative frame-level energy proxy
energy = frame_mean_square(y, frame_length=2048, hop_length=512)
print(f"Computed {len(energy)} frames")
print(f"Sample rate: {sr} Hz")
print(f"Duration: {metadata['duration_seconds']:.2f}s")
```

---

## 💡 Patterns That Matter (Use Cases)

* Birdsong and animal communication analysis
* Tonal language analysis
* Emotional and social subtext via vocal prosody
* Acoustic ecology and environmental sound monitoring
* Music and cultural analysis
* Clinical, accessibility, and speech research workflows

---

## 🧭 Documentation

* [docs/faq.md](docs/faq.md)
* [docs/ROADMAP.md](docs/ROADMAP.md)
* [docs/calibration-guide.md](docs/calibration-guide.md)
* [CONTRIBUTING.md](CONTRIBUTING.md)

---

Current Phase: Foundation (v0.1.0) | Licensed under [MIT](LICENSE)
