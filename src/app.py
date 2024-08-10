import logging
import os
import shutil
import streamlit as st
from streamlit_option_menu import option_menu
from extractor import extract_audio
from analyzer import save_audio_analysis, analyze_audio_for_parameters
from enhancer import AudioProcessor
from pydub import AudioSegment
from config import create_directory_if_not_exists, staging_folder, treated_folder, converted_folder, input_folder

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Funções para manipulação de arquivos e processamento de áudio
def process_file(processor, input_path, treated_path, noise_reduction_prop, low_cutoff, high_cutoff):
    try:
        logging.info(f"Tratando o áudio: {input_path}")
        y, sr, metrics = analyze_audio_for_parameters(input_path)
        processor.enhance_audio(y, sr, metrics, treated_path, noise_reduction_prop, low_cutoff, high_cutoff)
    except Exception as e:
        logging.error(f"Erro ao processar arquivo: {e}")

def treat_audio_file(processor, input_path, noise_reduction_prop, low_cutoff, high_cutoff):
    treated_path = input_path.replace('.wav', '_treated.mp3')
    process_file(processor, input_path, treated_path, noise_reduction_prop, low_cutoff, high_cutoff)
    return treated_path

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
    return [filename for filename in os.listdir(folder) if filename.endswith(('.wav', '.mp3', '.mp4'))]

def delete_file(file_path):
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
            return True
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            return True
    except Exception as e:
        logging.error(f'Erro ao deletar {file_path}. Motivo: {e}')
    return False

def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        delete_file(file_path)

def display_audio_analysis(file_path, stage):
    analysis_folder = os.path.join(os.path.dirname(file_path), 'analysis')

    st.subheader(f"Análise de Áudio ({stage.capitalize()})")
    
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    metrics_file = os.path.join(analysis_folder, f'{base_filename}_{stage}_metrics.txt')
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            st.text(f.read())

    spectrogram_file = os.path.join(analysis_folder, f'{base_filename}_{stage}_spectrogram.png')
    if os.path.exists(spectrogram_file):
        st.image(spectrogram_file)

def suggest_parameters(metrics):
    noise_reduction_prop = 0.5 + (metrics.get('Zero Crossing Rate', 0) * 0.5)
    low_cutoff = max(20, int(metrics.get('Spectral Centroid', 100)))
    high_cutoff = min(16000, int(metrics.get('Spectral Bandwidth', 8000)))
    
    return noise_reduction_prop, low_cutoff, high_cutoff

def extract_audio_from_file(input_file, output_folder):
    try:
        temp_dir = os.path.join(output_folder, "temp_video")
        create_directory_if_not_exists(temp_dir)

        temp_file_path = os.path.join(temp_dir, os.path.basename(input_file))
        shutil.copy(input_file, temp_file_path)

        logging.info(f"Extraindo áudio do vídeo {input_file}")
        extract_audio(temp_dir, output_folder)

        shutil.rmtree(temp_dir)
    except Exception as e:
        logging.error(f"Erro ao extrair áudio do vídeo {input_file}: {e}")

def main():
    st.title("Processamento de Áudio")

    # Adiciona custom CSS para alinhar os itens da navbar
    st.markdown("""
        <style>
        /* Estiliza a navbar para ter os itens com o mesmo tamanho e centralizados */
        .nav-pills .nav-link {
            flex: 1;
            text-align: center;
            margin-right: 5px;
            padding: 10px;
            border-radius: 10px;
        }
        .nav-pills .nav-link.active {
            background-color: #FF4B4B !important;
            color: white !important;
        }
        .nav-pills {
            display: flex;
            justify-content: center;
        }
        </style>
        """, unsafe_allow_html=True)

    # Implementação da Navbar
    selected_section = option_menu(
        menu_title=None,  # Ocultar título do menu
        options=["Home", "Extrair Áudio", "Tratar Áudio", "Converter Áudio", "Analisar Áudio", "Gerenciar Arquivos"],
        icons=["house", "cloud-upload", "tools", "headphones", "graph-up-arrow", "folder"],
        menu_icon="cast",  # Ícone do menu
        default_index=0,  # A primeira opção é "Home"
        orientation="horizontal",
    )

    if selected_section == "Home":
        st.write("Bem-vindo ao Processamento de Áudio. Use o menu acima para selecionar uma ação.")

    elif selected_section == "Extrair Áudio":
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
            st.write("Arquivos na pasta de vídeos:")
            for file in video_files:
                st.text(file)
        else:
            st.write("Nenhum arquivo de vídeo encontrado.")

        st.subheader("Extrair Áudio")
        if st.button('Extrair Áudio de Todos os Vídeos na Pasta'):
            extract_audio(input_folder, staging_folder)
            st.success('Áudio de todos os vídeos extraído com sucesso!')

        video_file = st.selectbox("Selecione um vídeo para extrair o áudio", video_files)
        if video_file:
            file_path = os.path.join(input_folder, video_file)
            if st.button(f'Extrair Áudio de {video_file}'):
                extract_audio_from_file(file_path, staging_folder)
                st.success(f'Áudio de {video_file} extraído com sucesso!')

    elif selected_section == "Tratar Áudio":
        st.subheader("Parâmetros de Tratamento de Áudio")
        noise_reduction_prop = st.slider("Proporção de Redução de Ruído", 0.0, 1.0, 0.5)
        low_cutoff = st.slider("Frequência de Corte Baixa (Hz)", 20, 500, 100)
        high_cutoff = st.slider("Frequência de Corte Alta (Hz)", 5000, 16000, 8000)

        audio_file = st.selectbox("Selecione o arquivo", list_files_in_folder(staging_folder))
        if audio_file:
            file_path = os.path.join(staging_folder, audio_file)
            if st.button('Tratar Áudio Selecionado'):
                treated_file_path = treat_audio_file(AudioProcessor(), file_path, noise_reduction_prop, low_cutoff, high_cutoff)
                st.success('Áudio tratado com sucesso!')
                display_audio_analysis(treated_file_path, "treated")

    elif selected_section == "Converter Áudio":
        if st.button('Converter Áudio para MP3 sem Tratamento'):
            convert_audio_to_mp3(staging_folder, converted_folder)
            st.success('Áudio convertido com sucesso!')

    elif selected_section == "Analisar Áudio":
        st.subheader("Selecione um arquivo de áudio para análise")
        folder_option = st.selectbox("Selecione a pasta", ["staging", "treated", "converted"])
        folder_mapping = {"staging": staging_folder, "treated": treated_folder, "converted": converted_folder}
        selected_folder = folder_mapping[folder_option]

        audio_file = st.selectbox("Selecione o arquivo", list_files_in_folder(selected_folder))
        if audio_file:
            file_path = os.path.join(selected_folder, audio_file)
            if st.button(f'Analisar Áudio {folder_option.capitalize()}'):
                analyze_audio(selected_folder, folder_option)
                st.success(f'Análise do áudio {folder_option} concluída!')
                display_audio_analysis(file_path, folder_option)

            if st.button("Gerar Sugestão de Parâmetros"):
                y, sr, metrics = analyze_audio_for_parameters(file_path)
                noise_reduction_prop, low_cutoff, high_cutoff = suggest_parameters(metrics)
                st.write("Sugestão de Parâmetros:")
                st.write(f"Proporção de Redução de Ruído: {noise_reduction_prop}")
                st.write(f"Frequência de Corte Baixa: {low_cutoff} Hz")
                st.write(f"Frequência de Corte Alta: {high_cutoff} Hz")

                if st.button("Aplicar Sugestões no Tratamento"):
                    treated_file_path = treat_audio_file(AudioProcessor(), file_path, noise_reduction_prop, low_cutoff, high_cutoff)
                    st.success("Sugestões aplicadas e áudio tratado com sucesso!")
                    display_audio_analysis(treated_file_path, "treated")

    elif selected_section == "Gerenciar Arquivos":
        st.subheader("Gerenciar Arquivos de Áudio")
        folder_option = st.selectbox("Selecione a pasta", ["staging", "treated", "converted"])
        folder_mapping = {"staging": staging_folder, "treated": treated_folder, "converted": converted_folder}
        selected_folder = folder_mapping[folder_option]

        files = list_files_in_folder(selected_folder)
        if files:
            st.write(f"Arquivos na pasta {folder_option}:")
            for file in files:
                file_path = os.path.join(selected_folder, file)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(file)
                with col2:
                    if st.button('Excluir', key=f'delete_{file}'):
                        if delete_file(file_path):
                            st.success(f"Arquivo {file} excluído com sucesso!")
                            files.remove(file)
                        else:
                            st.error(f"Erro ao excluir o arquivo {file}.")
        else:
            st.write(f"Não há arquivos na pasta {folder_option}.")

        if st.button('Limpar Pasta Selecionada'):
            clear_folder(selected_folder)
            st.success(f"Pasta {folder_option} limpa com sucesso!")
            files = list_files_in_folder(selected_folder)

if __name__ == "__main__":
    main()
