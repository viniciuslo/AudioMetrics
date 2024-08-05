import sys
import os
import numpy as np
import librosa
import soundfile as sf
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from analyzer import calculate_metrics, save_audio_analysis

def test_calculate_metrics():
    y = np.array([0.1, -0.1, 0.2, -0.2])  # Example waveform
    sr = 22050  # Example sampling rate
    metrics = calculate_metrics(y, sr)
    assert 'RMS Desvio' in metrics
    assert 'Zero Crossing Rate' in metrics
    assert 'Spectral Centroid' in metrics
    assert 'Spectral Bandwidth' in metrics
    assert 'Spectral Flatness' in metrics
    assert 'Spectral Roll-off' in metrics

def test_save_audio_analysis(tmp_path):
    audio_path = tmp_path / "test_audio.wav"
    output_folder = tmp_path / "analysis"
    output_folder.mkdir()
    # Create a dummy audio file with valid WAV headers and some audio data
    sr = 22050
    y = np.random.randn(sr).astype(np.float32)
    sf.write(audio_path, y, sr)
    save_audio_analysis(audio_path, output_folder, stage='original')
    assert (output_folder / "test_audio_original_metrics.txt").exists()
    assert (output_folder / "test_audio_original_spectrogram.png").exists()
