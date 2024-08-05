import librosa
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import os

def calculate_metrics(y, sr):
    y = np.array(y)  # Ensure y is a numpy array
    metrics = {}
    metrics['RMS Desvio'] = np.sqrt(np.mean(y**2))
    metrics['Zero Crossing Rate'] = np.mean(librosa.feature.zero_crossing_rate(y))
    metrics['Spectral Centroid'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    metrics['Spectral Bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    metrics['Spectral Flatness'] = np.mean(librosa.feature.spectral_flatness(y=y))
    metrics['Spectral Roll-off'] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    return metrics

def save_metrics(metrics, filepath):
    with open(filepath, 'w') as f:
        for key, value in metrics.items():
            if isinstance(value, np.ndarray):
                value = value.tolist()  # Convertendo array numpy para lista
            f.write(f'{key}: {value}\n')

def generate_spectrogram(y, sr, filepath):
    plt.figure(figsize=(10, 4))
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def analyze_audio_for_parameters(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    
    # Calculando métricas
    metrics = {
        'Zero Crossing Rate': np.mean(librosa.feature.zero_crossing_rate(y=y)),
        'Spectral Centroid': np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
        'Spectral Bandwidth': np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)),
        'Spectral Flatness': np.mean(librosa.feature.spectral_flatness(y=y)),
        'Spectral Roll-off': np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)),
        'RMS': np.mean(librosa.feature.rms(y=y))
    }
    
    return y, sr, metrics

def save_audio_analysis(input_file, output_folder, stage='original'):
    y, sr = librosa.load(input_file, sr=None)
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    metrics = calculate_metrics(y, sr)
    metrics_file = os.path.join(output_folder, f'{base_filename}_{stage}_metrics.txt')
    spectrogram_file = os.path.join(output_folder, f'{base_filename}_{stage}_spectrogram.png')
    save_metrics(metrics, metrics_file)
    generate_spectrogram(y, sr, spectrogram_file)
    print(f'Análise de áudio {stage} salva em {metrics_file} e {spectrogram_file}')
