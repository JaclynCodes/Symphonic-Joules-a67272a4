# Symphonic-Joules Roadmap

## Current status

Symphonic-Joules is in an early-stage Python implementation phase. The codebase includes a working foundation for audio processing and signal-energy analysis, but several higher-level scientific and product features remain planned work.

## v0.1.0 — Foundation

Implemented:
- Python package structure under `src/symphonic_joules/`
- Audio loading and saving
- Signal normalization and mono conversion
- Framing utilities
- Relative energy proxies
- Initial test coverage

Planned:
- Calibration pipeline for microphone response and gain
- Clearer physical-unit conversion documentation
- Expansion of examples and usage guides

## v0.2.0 — Calibration and validation

Planned:
- Support for converting digital samples to pressure in Pa
- Microphone sensitivity and gain documentation
- Benchmark validation against known acoustic signals
- More rigorous unit tests for edge cases

## v0.3.0 — Analysis workflows

Planned:
- Real-time processing paths
- Frequency-domain analysis utilities
- Visualization tools and notebooks
- Broader audio-format support

## v1.0.0 — Scientific toolkit

Planned:
- Stable public API
- Calibration-aware acoustic processing
- Comprehensive docs and tutorials
- Community contributor workflow and review process

## Long-term vision

The long-term goal is to support robust, calibrated acoustic analysis for sound-based research, pattern detection, and scientific exploration without overclaiming physical results from uncalibrated WAV files.
