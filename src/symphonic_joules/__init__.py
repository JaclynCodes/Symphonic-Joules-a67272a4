"""
Energy-related numerical utilities for Symphonic-Joules.

This module provides:
- Basic physics utilities (kinetic and potential energy)
- Audio signal analysis proxies (relative energy measures)
- Spectral decomposition for frequency-band energy comparison

IMPORTANT: Unless calibrated sound-pressure data are supplied, audio-derived
results in this module are dimensionless signal-energy proxies rather than
physical acoustic quantities in SI units (J/m³).
"""

from typing import Any

import librosa
import numpy as np


def calculate_kinetic_energy(mass: float, velocity: float) -> float:
    """
    Calculate translational kinetic energy in joules.

    Formula: KE = 0.5 * m * v²

    Args:
        mass: Mass in kilograms (kg)
        velocity: Velocity in meters per second (m/s)

    Returns:
        Kinetic energy in Joules (J)

    Raises:
        ValueError: If mass is negative
    """
    if mass < 0:
        raise ValueError("Mass cannot be negative")

    return 0.5 * mass * velocity**2


def calculate_potential_energy(
    mass: float,
    height: float,
    gravity: float = 9.81,
) -> float:
    """
    Calculate gravitational potential energy in joules.

    Formula: PE = m * g * h

    Args:
        mass: Mass in kilograms (kg)
        height: Height above reference point in meters (m)
        gravity: Gravitational acceleration in m/s² (default: 9.81 for Earth)

    Returns:
        Potential energy in Joules (J)

    Raises:
        ValueError: If mass is negative
    """
    if mass < 0:
        raise ValueError("Mass cannot be negative")

    return mass * gravity * height


def instantaneous_intensity_proxy(y: np.ndarray) -> np.ndarray:
    """
    Return squared waveform amplitudes as an intensity proxy.

    In acoustics, intensity is proportional to the square of sound pressure.
    For uncalibrated digital audio, this is a relative proxy only—not an
    absolute physical intensity in W/m².

    Args:
        y: Audio waveform as numpy array (mono, 1D)

    Returns:
        Array of squared amplitudes (dimensionless intensity proxy)

    Raises:
        TypeError: If waveform is not a numpy array
        ValueError: If waveform is empty
    """
    waveform = _validate_mono_waveform(y)
    return np.square(waveform, dtype=np.float64)


def frame_mean_square(
    y: np.ndarray,
    frame_length: int,
    hop_length: int,
) -> np.ndarray:
    """
    Compute mean-square amplitude for overlapping signal frames.

    The result is a relative signal-energy proxy for uncalibrated audio.
    Values represent frame-wise power density proportional to amplitude,
    not physical energy density in joules per cubic meter.

    Args:
        y: Audio waveform as numpy array (mono, 1D)
        frame_length: Length of each frame in samples
        hop_length: Number of samples between frame starts

    Returns:
        Array of mean-square values per frame (dimensionless proxy)

    Raises:
        TypeError: If waveform is not a numpy array
        ValueError: If parameters are invalid
    """
    waveform = _validate_mono_waveform(y)

    if frame_length <= 0 or hop_length <= 0:
        raise ValueError("frame_length and hop_length must be positive")
    if waveform.size < frame_length:
        raise ValueError(
            f"Signal is too short ({waveform.size} samples) "
            f"for frame_length ({frame_length})"
        )

    frames = librosa.util.frame(
        waveform,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    return np.mean(np.square(frames, dtype=np.float64), axis=0)


def spectral_band_energy_proxy(
    y: np.ndarray,
    sr: int,
    cutoff_hz: float = 1000.0,
) -> dict[str, float]:
    """
    Split the relative spectral energy of a mono signal into two frequency bands.

    This function computes energy in low and high frequency regions separated
    by a cutoff frequency. Absolute proxy values depend on signal length and
    amplitude. Ratio fields are generally more suitable for comparing similarly
    processed recordings.

    Args:
        y: Audio waveform as numpy array (mono, 1D)
        sr: Sample rate in Hz
        cutoff_hz: Frequency (Hz) separating low and high bands (default: 1000 Hz)

    Returns:
        Dictionary with keys:
        - 'cutoff_hz': Cutoff frequency used
        - 'low_band_energy_proxy': Relative energy in low band
        - 'high_band_energy_proxy': Relative energy in high band
        - 'total_energy_proxy': Sum of both bands
        - 'low_band_ratio': Fraction of energy in low band (0–1)
        - 'high_band_ratio': Fraction of energy in high band (0–1)

    Raises:
        TypeError: If waveform is not a numpy array
        ValueError: If parameters are invalid
    """
    waveform = _validate_mono_waveform(y)

    if sr <= 0:
        raise ValueError(f"Sample rate must be positive, got {sr}")
    if not 0 < cutoff_hz < sr / 2:
        raise ValueError(
            f"cutoff_hz must be between 0 and the Nyquist frequency ({sr / 2} Hz)"
        )

    spectrum = np.fft.rfft(waveform)
    frequencies = np.fft.rfftfreq(waveform.size, d=1 / sr)
    magnitude_squared = np.abs(spectrum) ** 2

    low_energy = float(np.sum(magnitude_squared[frequencies < cutoff_hz]))
    high_energy = float(np.sum(magnitude_squared[frequencies >= cutoff_hz]))
    total_energy = low_energy + high_energy

    low_ratio = low_energy / total_energy if total_energy else 0.0
    high_ratio = high_energy / total_energy if total_energy else 0.0

    return {
        "cutoff_hz": float(cutoff_hz),
        "low_band_energy_proxy": low_energy,
        "high_band_energy_proxy": high_energy,
        "total_energy_proxy": total_energy,
        "low_band_ratio": low_ratio,
        "high_band_ratio": high_ratio,
    }


def _validate_mono_waveform(y: np.ndarray) -> np.ndarray:
    """
    Validate and return a one-dimensional floating-point waveform.

    Private helper for internal use.

    Args:
        y: Input to validate

    Returns:
        Validated numpy array as float64

    Raises:
        TypeError: If not a numpy array
        ValueError: If not 1D or is empty
    """
    if not isinstance(y, np.ndarray):
        raise TypeError("Waveform must be a NumPy array")
    if y.ndim != 1:
        raise ValueError("This function expects a one-dimensional mono waveform")
    if y.size == 0:
        raise ValueError("Waveform cannot be empty")

    return y.astype(np.float64, copy=False)


__all__ = [
    "calculate_kinetic_energy",
    "calculate_potential_energy",
    "frame_mean_square",
    "instantaneous_intensity_proxy",
    "spectral_band_energy_proxy",
]
