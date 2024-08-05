import sys
import os
from moviepy.editor import ColorClip
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from extractor import extract_audio

def test_extract_audio(tmp_path):
    input_folder = tmp_path / "videos"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    video_path = input_folder / "test_video.mp4"
    
    # Create a simple video with moviepy
    clip = ColorClip(size=(640, 480), color=(255, 0, 0)).set_duration(2)
    
    # Create a simple audio clip
    sr = 44100  # Sample rate
    t = np.linspace(0, 2, int(2 * sr), endpoint=False)  # 2 seconds duration
    audio = np.sin(440 * 2 * np.pi * t)  # Generate a 440 Hz sine wave
    audio_stereo = np.column_stack([audio, audio])  # Make it stereo
    audio_clip = AudioArrayClip(audio_stereo, fps=sr)
    
    # Set the audio of the video clip
    clip = clip.set_audio(audio_clip)
    
    # Write the video file
    clip.write_videofile(str(video_path), codec="libx264", fps=24, audio_codec="aac")
    
    extract_audio(input_folder, output_folder)
    assert len(list(output_folder.glob("*.wav"))) > 0
