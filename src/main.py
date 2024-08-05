import logging
import os
import concurrent.futures
import librosa
from extractor import extract_audio
from analyzer import save_audio_analysis, analyze_audio_for_parameters
from enhancer import AudioProcessor
from pydub import AudioSegment
from config import create_directory_if_not_exists, input_folder, staging_folder, treated_folder, converted_folder, noise_reduction_prop, low_cutoff_frequency, high_cutoff_frequency

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_file(processor, input_path, treated_path):
    try:
        logging.info(f"Tratando o áudio: {input_path}")
        y, sr, metrics = analyze_audio_for_parameters(input_path)
        processor.enhance_audio(y, sr, metrics, treated_path, noise_reduction_prop, low_cutoff_frequency, high_cutoff_frequency)
    except Exception as e:
        logging.error(f"Erro ao processar arquivo: {e}")

def treat_audio_concurrently(input_folder, treated_folder, processor):
    create_directory_if_not_exists(input_folder)
    create_directory_if_not_exists(treated_folder)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for filename in os.listdir(input_folder):
            if filename.endswith('.wav'):
                input_path = os.path.join(input_folder, filename)
                treated_path = os.path.join(treated_folder, filename.replace('.wav', '.mp3'))
                futures.append(executor.submit(process_file, processor, input_path, treated_path))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Erro ao processar arquivo: {e}")

def convert_audio_to_mp3(input_folder, converted_folder):
    create_directory_if_not_exists(input_folder)
    create_directory_if_not_exists(converted_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.wav'):
            input_path = os.path.join(input_folder, filename)
            converted_path = os.path.join(converted_folder, filename.replace('.wav', '.mp3'))

            try:
                logging.info(f"Convertendo o áudio: {input_path}")
                audio = AudioSegment.from_wav(input_path)
                audio.export(converted_path, format='mp3')
                logging.info(f"Áudio convertido salvo em {converted_path}")
            except Exception as e:
                logging.error(f"Erro ao converter {filename}: {e}")

def main():
    create_directory_if_not_exists(input_folder)
    create_directory_if_not_exists(staging_folder)
    create_directory_if_not_exists(treated_folder)
    create_directory_if_not_exists(converted_folder)

    processor = AudioProcessor()

    while True:
        print("\nEscolha uma opção:")
        print("1. Extrair áudio dos vídeos")
        print("2. Tratar áudio extraído")
        print("3. Converter áudio para MP3 sem tratamento")
        print("4. Analisar áudio extraído")
        print("5. Analisar áudio tratado")
        print("6. Analisar áudio convertido")
        print("7. Sair")

        choice = input("Digite o número da sua escolha: ")

        if choice == '1':
            extract_audio(input_folder, staging_folder)
        elif choice == '2':
            treat_audio_concurrently(staging_folder, treated_folder, processor)
        elif choice == '3':
            convert_audio_to_mp3(staging_folder, converted_folder)
        elif choice == '4':
            analysis_folder = os.path.join(staging_folder, 'analysis')
            create_directory_if_not_exists(analysis_folder)
            for filename in os.listdir(staging_folder):
                if filename.endswith('.wav'):
                    input_path = os.path.join(staging_folder, filename)
                    logging.info(f"Analisando o áudio extraído: {input_path}")
                    save_audio_analysis(input_path, analysis_folder, stage='original')
        elif choice == '5':
            treated_analysis_folder = os.path.join(treated_folder, 'analysis')
            create_directory_if_not_exists(treated_analysis_folder)
            logging.info("Listando arquivos .mp3 na pasta treated:")
            for filename in os.listdir(treated_folder):
                if filename.endswith('.mp3'):
                    logging.info(f"Encontrado: {filename}")
                    input_path = os.path.join(treated_folder, filename)
                    logging.info(f"Analisando o áudio tratado: {input_path}")
                    save_audio_analysis(input_path, treated_analysis_folder, stage='treated')
        elif choice == '6':
            converted_analysis_folder = os.path.join(converted_folder, 'analysis')
            create_directory_if_not_exists(converted_analysis_folder)
            logging.info("Listando arquivos .mp3 na pasta converted:")
            for filename in os.listdir(converted_folder):
                if filename.endswith('.mp3'):
                    logging.info(f"Encontrado: {filename}")
                    input_path = os.path.join(converted_folder, filename)
                    logging.info(f"Analisando o áudio convertido: {input_path}")
                    save_audio_analysis(input_path, converted_analysis_folder, stage='converted')
        elif choice == '7':
            logging.info("Saindo...")
            break
        else:
            print("Escolha inválida. Tente novamente.")

if __name__ == "__main__":
    main()
