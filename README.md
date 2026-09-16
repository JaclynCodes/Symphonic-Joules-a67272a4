"""
Symphonic-Joules: Harmonizing Sound and Energy

A project that explores the intersection of audio processing and energy calculations,
providing tools and insights that bridge the gap between acoustics and physics.
"""

__version__ = "0.1.0"
__author__ = "JaclynCodes"
__license__ = "MIT"

from .audio import load_audio, normalize_peak, save_audio, to_mono, frame_signal
from .energy import (
    calculate_kinetic_energy,
    calculate_potential_energy,
    instantaneous_intensity_proxy,
    frame_mean_square,
    spectral_band_energy_proxy,
)

# Package metadata and public API exports
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
]
