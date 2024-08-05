import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from enhancer import AudioProcessor

def test_enhance_audio(tmp_path):
    processor = AudioProcessor()
    y = [0.1, -0.1, 0.2, -0.2]  # Example waveform
    sr = 22050  # Example sampling rate
    metrics = {'Zero Crossing Rate': 0.1}
    output_file = tmp_path / "output.mp3"
    processor.enhance_audio(y, sr, metrics, str(output_file))
    assert output_file.exists()
