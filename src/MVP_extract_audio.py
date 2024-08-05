import os
import ffmpeg
import librosa
import numpy as np
import noisereduce as nr
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

def extract_audio(input_folder, output_folder):
    if not os.path.exists(input_folder):
        print(f"A pasta {input_folder} não existe.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"A pasta de saída {output_folder} foi criada.")

    for filename in os.listdir(input_folder):
        if filename.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.wav')

            try:
                ffmpeg.input(input_path).output(output_path).run()
                print(f"Áudio extraído de {filename} para {output_path}")
            except ffmpeg.Error as e:
                print(f"Erro ao processar {filename}: {e}")

def analyze_audio_for_parameters(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    S_full, phase = librosa.magphase(librosa.stft(y))
    rms = librosa.feature.rms(y=y)[0]
    mean_rms = np.mean(rms)
    prop_decrease = 0.5 + (mean_rms / 2)
    return y, sr, prop_decrease

def save_audio_analysis(audio_path, analysis_folder, stage=''):
    y, sr = librosa.load(audio_path, sr=None)
    S_full, phase = librosa.magphase(librosa.stft(y))

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(librosa.amplitude_to_db(S_full, ref=np.max), y_axis='log', x_axis='time')
    plt.title(f'Espectrograma {stage}')
    plt.colorbar(format='%+2.0f dB')
    plt.tight_layout()

    if not os.path.exists(analysis_folder):
        os.makedirs(analysis_folder)

    # Salva o espectrograma como uma imagem
    image_path = os.path.join(analysis_folder, os.path.splitext(os.path.basename(audio_path))[0] + f'_{stage}_spectrogram.png')
    plt.savefig(image_path)
    plt.close()
    print(f"Espectrograma salvo como {image_path}")

    return y, sr, S_full, phase

def enhance_audio(y, sr, prop_decrease, output_path):
    # Redução de ruído com noisereduce ajustado
    reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=prop_decrease)

    # Normalização
    y_normalized = librosa.util.normalize(reduced_noise, norm=np.inf, axis=0)

    # Aplicar um filtro passa-alta para remover ruído de baixa frequência
    y_filtered = librosa.effects.preemphasis(y_normalized)

    # Salva o áudio tratado
    write(output_path, sr, (y_filtered * 32767).astype(np.int16))
    print(f"Áudio tratado salvo em {output_path}")

def treat_audio(input_folder, treated_folder):
    if not os.path.exists(input_folder):
        print(f"A pasta {input_folder} não existe.")
        return

    if not os.path.exists(treated_folder):
        os.makedirs(treated_folder)
        print(f"A pasta de saída tratada {treated_folder} foi criada.")

    for filename in os.listdir(input_folder):
        if filename.endswith('.wav'):
            input_path = os.path.join(input_folder, filename)
            treated_path = os.path.join(treated_folder, filename)

            try:
                y, sr, prop_decrease = analyze_audio_for_parameters(input_path)
                enhance_audio(y, sr, prop_decrease, treated_path)
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")

def main():
    input_folder = './videos'
    output_folder = './output'
    treated_folder = './treated'
    analysis_folder = os.path.join(output_folder, 'analysis')

    while True:
        print("\nEscolha uma opção:")
        print("1. Extrair áudio dos vídeos")
        print("2. Tratar áudio extraído")
        print("3. Extrair e tratar áudio")
        print("4. Analisar áudio extraído")
        print("5. Analisar áudio tratado")
        print("6. Sair")

        choice = input("Digite o número da sua escolha: ")

        if choice == '1':
            extract_audio(input_folder, output_folder)
        elif choice == '2':
            treat_audio(output_folder, treated_folder)
        elif choice == '3':
            extract_audio(input_folder, output_folder)
            treat_audio(output_folder, treated_folder)
        elif choice == '4':
            for filename in os.listdir(output_folder):
                if filename.endswith('.wav'):
                    input_path = os.path.join(output_folder, filename)
                    save_audio_analysis(input_path, analysis_folder, stage='original')
        elif choice == '5':
            treated_analysis_folder = os.path.join(treated_folder, 'analysis')
            for filename in os.listdir(treated_folder):
                if filename.endswith('.wav'):
                    input_path = os.path.join(treated_folder, filename)
                    save_audio_analysis(input_path, treated_analysis_folder, stage='treated')
        elif choice == '6':
            print("Saindo...")
            break
        else:
            print("Escolha inválida. Tente novamente.")

if __name__ == "__main__":
    main()
