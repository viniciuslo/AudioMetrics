import os
import ffmpeg

def extract_audio(input_folder, output_folder):
    print(f"Extraindo áudio dos vídeos em {os.listdir(input_folder)} para {output_folder}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"A pasta {output_folder} foi criada.")

    for filename in os.listdir(input_folder):
        if filename.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.wav')

            try:
                ffmpeg.input(input_path).output(output_path).run()
                print(f"Áudio extraído de {filename} para {output_path}")
            except ffmpeg.Error as e:
                print(f"Erro ao processar {filename}: {e}")

if __name__ == "__main__":
    from config import input_folder, staging_folder
    extract_audio(input_folder, staging_folder)
