"""
Audio processing utilities for Symphonic-Joules.

This module provides tools for:
- Audio file loading and saving
- Audio signal analysis and transformation
- Frequency domain analysis (FFT, spectrograms)
- Time-domain processing (framing, normalization, mono conversion)

All multi-channel audio is returned in channel-first shape: (n_channels, n_samples).
Mono audio has shape (n_samples,).
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
    Load an audio file into memory.

    Multi-channel audio is returned in channel-first shape:
    (n_channels, n_samples). Mono audio has shape (n_samples,).

    Args:
        path: Path to the audio file
        sr: Target sample rate (None to use file's native sample rate)
        mono: Convert to mono if True (default: True)

    Returns:
        Tuple containing:
        - y: Audio waveform as numpy array
        - sample_rate: Sample rate in Hz
        - metadata: Dict with 'duration_seconds', 'n_samples', 'channels', 'sample_rate_hz'

    Raises:
        FileNotFoundError: If audio file does not exist
        RuntimeError: If audio file cannot be loaded

    Example:
        >>> y, sr, metadata = load_audio('birdsong.wav', sr=22050)
        >>> print(f"Duration: {metadata['duration_seconds']:.2f}s")
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
    """
    Save a mono or channel-first multi-channel waveform to a file.

    For multi-channel input, `y` must use shape (n_channels, n_samples).
    The function will transpose to (n_samples, n_channels) for soundfile.

    Args:
        path: Output file path
        y: Audio waveform as numpy array
        sr: Sample rate in Hz

    Raises:
        ValueError: If waveform or sample rate is invalid
        RuntimeError: If file cannot be saved

    Example:
        >>> save_audio('output.wav', waveform, 22050)
    """
    if sr <= 0:
        raise ValueError(f"Sample rate must be positive, got {sr}")
    if not isinstance(y, np.ndarray):
        raise TypeError("Waveform must be a NumPy array")
    if y.size == 0:
        raise ValueError("Cannot save an empty waveform")
    if y.ndim not in (1, 2):
        raise ValueError("Waveform must be one-dimensional or two-dimensional")

    # Transpose multi-channel audio from (n_channels, n_samples) to (n_samples, n_channels)
    output = y.T if y.ndim == 2 else y

    try:
        sf.write(str(path), output, sr)
    except Exception as exc:
        raise RuntimeError(f"Failed to save audio file '{path}': {exc}") from exc


def normalize_peak(y: np.ndarray) -> np.ndarray:
    """
    Return a copy of `y` normalized to peak absolute amplitude of 1.0.

    Args:
        y: Audio waveform as numpy array

    Returns:
        Normalized waveform with peak amplitude of 1.0

    Raises:
        TypeError: If waveform is not a numpy array
        ValueError: If waveform is empty or all zeros

    Example:
        >>> normalized = normalize_peak(waveform)
        >>> assert np.abs(normalized).max() == 1.0
    """
    if not isinstance(y, np.ndarray):
        raise TypeError("Waveform must be a NumPy array")
    if y.size == 0:
        raise ValueError("Cannot normalize an empty waveform")

    peak = float(np.max(np.abs(y)))
    if peak == 0.0:
        raise ValueError("Cannot normalize an all-zero waveform")

    return y / peak


def to_mono(y: np.ndarray) -> np.ndarray:
    """
    Average a channel-first waveform to mono.

    Expects multi-channel audio in shape (n_channels, n_samples).
    If already mono (1D), returns a copy.

    Args:
        y: Audio waveform as numpy array
           Shape: (n_samples,) for mono, (n_channels, n_samples) for multi-channel

    Returns:
        Mono waveform with shape (n_samples,)

    Raises:
        TypeError: If waveform is not a numpy array
        ValueError: If waveform is invalid

    Example:
        >>> stereo = np.array([[1, 2, 3], [4, 5, 6]])  # 2 channels, 3 samples
        >>> mono = to_mono(stereo)
        >>> # Result: [2.5, 3.5, 4.5]
    """
    if not isinstance(y, np.ndarray):
        raise TypeError("Waveform must be a NumPy array")
    if y.size == 0:
        raise ValueError("Cannot convert an empty waveform to mono")
    if y.ndim == 1:
        return y
    if y.ndim != 2:
        raise ValueError("Waveform must be one-dimensional or channel-first 2D")

    return np.mean(y, axis=0)


def frame_signal(
    y: np.ndarray,
    frame_length: int,
    hop_length: int,
) -> np.ndarray:
    """
    Split a mono waveform into overlapping frames.

    Uses librosa's efficient framing utility. Frames are returned with
    shape (frame_length, n_frames).

    Args:
        y: Audio waveform as numpy array (mono, 1D)
        frame_length: Length of each frame in samples
        hop_length: Number of samples between frame starts

    Returns:
        2D array of frames with shape (frame_length, n_frames)

    Raises:
        TypeError: If waveform is not a numpy array
        ValueError: If parameters are invalid

    Example:
        >>> frames = frame_signal(waveform, frame_length=2048, hop_length=512)
        >>> print(f"Number of frames: {frames.shape[1]}")
    """
    if not isinstance(y, np.ndarray):
        raise TypeError("Waveform must be a NumPy array")
    if y.ndim != 1:
        raise ValueError("frame_signal expects a one-dimensional mono waveform")
    if y.size < frame_length:
        raise ValueError("Signal is shorter than frame_length")
    if frame_length <= 0 or hop_length <= 0:
        raise ValueError("frame_length and hop_length must be positive")

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
