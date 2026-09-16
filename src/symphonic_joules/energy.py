"""
Audio processing utilities for Symphonic-Joules.

This module provides tools for:
- Audio file loading and saving
- Audio signal analysis and transformation
- Time-domain processing (framing, normalization, mono conversion)

All multi-channel audio uses a channel-first convention internally:
(n_channels, n_samples). Mono audio has shape (n_samples,).
"""

from pathlib import Path
from typing import Any, Optional

import librosa
import numpy as np
import soundfile as sf


def load_audio(
    path: str | Path,
    sr: Optional[int] = None,
    mono: bool = True,
) -> tuple[np.ndarray, int, dict[str, Any]]:
    """
    Load an audio file.

    Multi-channel audio is returned in channel-first shape:
    (n_channels, n_samples). Mono audio has shape (n_samples,).

    Args:
        path: Path to the audio file
        sr: Target sample rate (None to use file's native sample rate)
        mono: Convert to mono if True

    Returns:
        Tuple containing waveform, sample_rate, and metadata.

    Raises:
        FileNotFoundError: If the file does not exist
        RuntimeError: If the file cannot be loaded
    """
    try:
        y, sample_rate = librosa.load(str(path), sr=sr, mono=mono)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Audio file not found: {path}") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to load audio file '{path}': {exc}") from exc

    n_samples = y.shape[-1]
    channels = 1 if y.ndim == 1 else y.shape[0]

    metadata = {
        "duration_seconds": n_samples / sample_rate,
        "n_samples": n_samples,
        "channels": channels,
        "sample_rate_hz": sample_rate,
    }

    return y, sample_rate, metadata


def save_audio(path: str | Path, y: np.ndarray, sr: int) -> None:
    """Save a mono or channel-first multi-channel waveform to a file."""
    if sr <= 0:
        raise ValueError(f"Sample rate must be positive, got {sr}")
    if not isinstance(y, np.ndarray):
        raise TypeError("Waveform must be a NumPy array")
    if y.size == 0:
        raise ValueError("Cannot save an empty waveform")
    if y.ndim not in (1, 2):
        raise ValueError("Waveform must be one-dimensional or two-dimensional")

    output = y.T if y.ndim == 2 else y

    try:
        sf.write(str(path), output, sr)
    except Exception as exc:
        raise RuntimeError(f"Failed to save audio file '{path}': {exc}") from exc


def normalize_peak(y: np.ndarray) -> np.ndarray:
    """Return a copy of `y` normalized to peak absolute amplitude 1.0."""
    if not isinstance(y, np.ndarray):
        raise TypeError("Waveform must be a NumPy array")
    if y.size == 0:
        raise ValueError("Cannot normalize an empty waveform")

    peak = float(np.max(np.abs(y)))
    if peak == 0.0:
        raise ValueError("Cannot normalize an all-zero waveform")

    return y / peak


def to_mono(y: np.ndarray) -> np.ndarray:
    """Average a channel-first waveform to mono."""
    if not isinstance(y, np.ndarray):
        raise TypeError("Waveform must be a NumPy array")
    if y.size == 0:
        raise ValueError("Cannot convert an empty waveform to mono")
    if y.ndim == 1:
        return y
    if y.ndim != 2:
        raise ValueError("Waveform must be one-dimensional or channel-first 2D")

    return np.mean(y, axis=0)


def frame_signal(y: np.ndarray, frame_length: int, hop_length: int) -> np.ndarray:
    """Split a mono waveform into overlapping frames."""
    if not isinstance(y, np.ndarray):
        raise TypeError("Waveform must be a NumPy array")
    if y.ndim != 1:
        raise ValueError("frame_signal expects a one-dimensional mono waveform")
    if y.size == 0:
        raise ValueError("Cannot frame an empty waveform")
    if frame_length <= 0 or hop_length <= 0:
        raise ValueError("frame_length and hop_length must be positive")
    if y.size < frame_length:
        raise ValueError("Signal is shorter than frame_length")

    return librosa.util.frame(
        y,
        frame_length=frame_length,
        hop_length=hop_length,
    )


__all__ = [
    "frame_signal",
    "load_audio",
    "normalize_peak",
    "save_audio",
    "to_mono",
]
