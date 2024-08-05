import sys
import os
import numpy as np
import soundfile as sf
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import treat_audio_concurrently, convert_audio_to_mp3
from enhancer import AudioProcessor

def test_treat_audio_concurrently(tmp_path):
    input_folder = tmp_path / "input"
    treated_folder = tmp_path / "treated"
    input_folder.mkdir()
    treated_folder.mkdir()
    audio_path = input_folder / "test_audio.wav"
    # Create a dummy audio file com valid WAV headers e some audio data
    sr = 22050
    y = np.random.randn(sr).astype(np.float32)
    sf.write(audio_path, y, sr)
    processor = AudioProcessor()
    treat_audio_concurrently(input_folder, treated_folder, processor)
    assert len(list(treated_folder.glob("*.mp3"))) > 0

def test_convert_audio_to_mp3(tmp_path):
    input_folder = tmp_path / "input"
    converted_folder = tmp_path / "converted"
    input_folder.mkdir()
    converted_folder.mkdir()
    audio_path = input_folder / "test_audio.wav"
    # Create a dummy audio file com valid WAV headers e some audio data
    sr = 22050
    y = np.random.randn(sr).astype(np.float32)
    sf.write(audio_path, y, sr)
    convert_audio_to_mp3(input_folder, converted_folder)
    assert len(list(converted_folder.glob("*.mp3"))) > 0
