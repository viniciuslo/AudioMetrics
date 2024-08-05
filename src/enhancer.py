import librosa
import noisereduce as nr
import soundfile as sf
from scipy.signal import butter, lfilter
from pydub import AudioSegment
import os
import numpy as np

class AudioProcessor:
    def __init__(self, noise_reduction=True, equalization=True, compression=True, normalization=True):
        self.noise_reduction = noise_reduction
        self.equalization = equalization
        self.compression = compression
        self.normalization = normalization

    def butter_lowpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_highpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def lowpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def highpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_highpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def enhance_audio(self, y, sr, metrics, output_file, noise_reduction_prop=0.5, low_cutoff=100, high_cutoff=8000):
        if self.noise_reduction:
            # Ajustar a redução de ruído com base na métrica de ruído
            zcr = metrics.get('Zero Crossing Rate', 0)
            prop_decrease = noise_reduction_prop * (1 + (zcr / 0.1))  # Exemplo de ajuste
            y = nr.reduce_noise(y=y, sr=sr, prop_decrease=prop_decrease)
        
        if self.equalization:
            y = self.highpass_filter(y, cutoff=low_cutoff, fs=sr, order=6)
            y = self.lowpass_filter(y, cutoff=high_cutoff, fs=sr, order=6)
        
        if self.compression:
            y = librosa.effects.preemphasis(y)
        
        if self.normalization:
            y = librosa.util.normalize(y)
        
        # Salvar o áudio tratado como WAV temporariamente
        temp_wav_file = output_file.replace('.mp3', '.wav')
        sf.write(temp_wav_file, y, sr)
        
        # Converter WAV para MP3
        audio = AudioSegment.from_wav(temp_wav_file)
        audio.export(output_file, format='mp3')
        
        # Remover o arquivo WAV temporário
        os.remove(temp_wav_file)

        print(f'Áudio tratado salvo em {output_file}')
