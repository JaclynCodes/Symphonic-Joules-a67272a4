"""
Symphonic-Joules: Harmonizing Sound and Energy.

A Python toolkit for loading audio, processing signals, and computing
relative energy-based proxies with a clear distinction between signal metrics
and calibrated physical acoustics.
"""

__version__ = "0.1.0"
__author__ = "JaclynCodes"
__license__ = "MIT"

from .audio import frame_signal, load_audio, normalize_peak, save_audio, to_mono
from .energy import (
    calculate_kinetic_energy,
    calculate_potential_energy,
    frame_mean_square,
    instantaneous_intensity_proxy,
    spectral_band_energy_proxy,
)

# Backwards-compatible aliases for older names.
from .energy import (
    frame_energy_density as frame_energy_density,
    energy_decomposition_proxy as energy_decomposition_proxy,
    acoustic_intensity_proxy as acoustic_intensity_proxy,
)

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "load_audio",
    "save_audio",
    "normalize_peak",
    "to_mono",
    "frame_signal",
    "calculate_kinetic_energy",
    "calculate_potential_energy",
    "instantaneous_intensity_proxy",
    "frame_mean_square",
    "spectral_band_energy_proxy",
    "acoustic_intensity_proxy",
    "frame_energy_density",
    "energy_decomposition_proxy",
]
