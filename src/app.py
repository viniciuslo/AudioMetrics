import logging
import os
import concurrent.futures
import shutil
import streamlit as st
from extractor import extract_audio
from analyzer import save_audio_analysis, analyze_audio_for_parameters
from enhancer import AudioProcessor
from pydub import AudioSegment
from config import create_directory_if_not_exists, input_folder, staging_folder, treated_folder, converted_folder, input_folder, noise_reduction_prop, low_cutoff_frequency, high_cutoff_frequency

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_file(processor, input_path, treated_path, noise_reduction_prop, low_cutoff, high_cutoff):
    try:
        logging.info(f"Tratando o áudio: {input_path}")
        y, sr, metrics = analyze_audio_for_parameters(input_path)
        processor.enhance_audio(y, sr, metrics, treated_path, noise_reduction_prop, low_cutoff, high_cutoff)
    except Exception as e:
        logging.error(f"Erro ao processar arquivo: {e}")

def treat_audio_concurrently(input_folder, treated_folder, processor, noise_reduction_prop, low_cutoff, high_cutoff):
    create_directory_if_not_exists(input_folder)
    create_directory_if_not_exists(treated_folder)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for filename in os.listdir(input_folder):
            if filename.endswith('.wav'):
                input_path = os.path.join(input_folder, filename)
                treated_path = os.path.join(treated_folder, filename.replace('.wav', '.mp3'))
                futures.append(executor.submit(process_file, processor, input_path, treated_path, noise_reduction_prop, low_cutoff, high_cutoff))

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

def analyze_audio(folder, stage):
    analysis_folder = os.path.join(folder, 'analysis')
    create_directory_if_not_exists(analysis_folder)
    for filename in os.listdir(folder):
        if filename.endswith('.wav') or filename.endswith('.mp3'):
            input_path = os.path.join(folder, filename)
            logging.info(f"Analisando o áudio {stage}: {input_path}")
            save_audio_analysis(input_path, analysis_folder, stage=stage)

def list_files_in_folder(folder):
    files = []
    for filename in os.listdir(folder):
        if filename.endswith('.wav') or filename.endswith('.mp3') or filename.endswith('.mp4'):
            files.append(filename)
    return files

def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path) and filename != 'analysis':
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f'Erro ao deletar {file_path}. Motivo: {e}')

def main():
    st.title("Processamento de Áudio")

    processor = AudioProcessor()

    # Sidebar Menu
    menu = st.sidebar.selectbox("Escolha uma opção", ["Home", "Extrair Áudio", "Tratar Áudio", "Converter Áudio", "Analisar Áudio", "Visualizar Arquivos"])

    if menu == "Home":
        st.write("Bem-vindo ao Processamento de Áudio. Use o menu à esquerda para selecionar uma ação.")

    if menu == "Extrair Áudio":
        st.subheader("Upload de Vídeos")
        uploaded_videos = st.file_uploader("Faça upload dos seus vídeos", accept_multiple_files=True, type=["mp4", "mov", "avi"])

        if uploaded_videos:
            for uploaded_video in uploaded_videos:
                video_path = os.path.join(input_folder, uploaded_video.name)
                with open(video_path, "wb") as f:
                    f.write(uploaded_video.getbuffer())
                st.success(f"Arquivo {uploaded_video.name} salvo com sucesso!")

        if st.button('Fazer upload do Google Drive'):
            st.info("Funcionalidade de upload do Google Drive ainda não implementada.")

        st.subheader("Arquivos de Vídeo na Pasta de Entrada")
        video_files = list_files_in_folder(input_folder)
        if video_files:
            for file in video_files:
                st.text(file)
        else:
            st.write("Nenhum arquivo de vídeo encontrado.")

        if st.button('Extrair Áudio dos Vídeos'):
            extract_audio(input_folder, staging_folder)
            st.success('Áudio extraído com sucesso!')

    if menu == "Tratar Áudio":
        st.subheader("Parâmetros de Tratamento de Áudio")

        # Sliders para parâmetros ajustáveis
        noise_reduction_prop = st.slider("Proporção de Redução de Ruído", 0.0, 1.0, 0.5)
        low_cutoff = st.slider("Frequência de Corte Baixa (Hz)", 20, 500, 100)
        high_cutoff = st.slider("Frequência de Corte Alta (Hz)", 5000, 16000, 8000)

        if st.button('Tratar Áudio Extraído'):
            treat_audio_concurrently(staging_folder, treated_folder, processor, noise_reduction_prop, low_cutoff, high_cutoff)
            st.success('Áudio tratado com sucesso!')

    if menu == "Converter Áudio":
        if st.button('Converter Áudio para MP3 sem Tratamento'):
            convert_audio_to_mp3(staging_folder, converted_folder)
            st.success('Áudio convertido com sucesso!')

    if menu == "Analisar Áudio":
        analysis_stage = st.selectbox("Selecione o estágio para análise", ["original", "treated", "converted"])
        folder_mapping = {
            "original": staging_folder,
            "treated": treated_folder,
            "converted": converted_folder
        }
        selected_folder = folder_mapping[analysis_stage]

        if st.button(f'Analisar Áudio {analysis_stage.capitalize()}'):
            analyze_audio(selected_folder, analysis_stage)
            st.success(f'Análise do áudio {analysis_stage} concluída!')

    if menu == "Visualizar Arquivos":
        st.subheader("Arquivos de Áudio")
        folder_option = st.selectbox("Selecione a pasta", ["staging", "treated", "converted"])
        folder_mapping = {
            "staging": staging_folder,
            "treated": treated_folder,
            "converted": converted_folder
        }
        selected_folder = folder_mapping[folder_option]

        files = list_files_in_folder(selected_folder)
        if files:
            st.write(f"Arquivos na pasta {folder_option}:")
            for file in files:
                st.text(file)
        else:
            st.write(f"Não há arquivos na pasta {folder_option}.")

        if st.button('Limpar Pasta Selecionada'):
            clear_folder(selected_folder)
            st.success(f"Pasta {folder_option} limpa com sucesso!")

if __name__ == "__main__":
    main()
