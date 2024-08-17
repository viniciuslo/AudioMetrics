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
import librosa
import librosa.display
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levellevel)s - %(message)s')

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
        extract_audio(temp_file_path, output_folder)

        shutil.rmtree(temp_dir)
    except Exception as e:
        logging.error(f"Erro ao extrair áudio do vídeo {input_file}: {e}")

def get_file_as_bytes(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

# Função para cortar áudio
def cut_audio(audio, start_time, end_time):
    return audio[start_time:end_time]

def cortar_audio():
    st.title("Cortar Áudio")

    uploaded_file = st.file_uploader("Faça upload do seu arquivo de áudio", type=["mp3", "wav"])

    if uploaded_file is not None:
        # Salvar o arquivo temporariamente
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        # Carregar o áudio usando pydub para edição
        audio = AudioSegment.from_file(temp_file_path)

        # Carregar o áudio usando librosa para visualização
        y, sr = librosa.load(temp_file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        st.write(f"Duração do áudio: {duration:.2f} segundos")

        # Controle de zoom
        st.subheader("Zoom na Forma de Onda")
        zoom_start = st.slider("Zoom - Início (segundos)", 0.0, duration, 0.0)
        zoom_end = st.slider("Zoom - Fim (segundos)", zoom_start, duration, duration)

        # Exibir a forma de onda do áudio com zoom, ajustando o tamanho do gráfico
        fig, ax = plt.subplots(figsize=(10, 3))  # Ajuste o tamanho para ser mais retangular
        librosa.display.waveshow(y[int(zoom_start*sr):int(zoom_end*sr)], sr=sr, ax=ax)
        ax.set(title="Forma de Onda do Áudio", xlabel="Tempo (s)", ylabel="Amplitude")
        st.pyplot(fig)

        # Ouvir o áudio
        st.audio(uploaded_file, format='audio/wav')

        # Seção de corte manual
        st.subheader("Corte Manual")
        start_time = st.number_input("Início do corte (segundos)", min_value=0.0, max_value=duration, value=0.0, step=0.1)
        end_time = st.number_input("Fim do corte (segundos)", min_value=0.0, max_value=duration, value=duration, step=0.1)

        start_sample = int(start_time * 1000)
        end_sample = int(end_time * 1000)

        if st.button("Cortar Áudio"):
            # Cortar o áudio
            cut_audio_segment = cut_audio(audio, start_sample, end_sample)

            # Salvar o áudio cortado em memória
            cut_audio_file = BytesIO()
            cut_audio_segment.export(cut_audio_file, format="wav")
            cut_audio_file.seek(0)

            # Exibir o áudio cortado e oferecer para download
            st.audio(cut_audio_file, format='audio/wav')
            st.download_button(
                label="Baixar Áudio Cortado",
                data=cut_audio_file,
                file_name="corte_audio.wav",
                mime="audio/wav"
            )

# Função para criar o programa de rádio
def criar_programa_de_radio():
    st.title("Criar Programa")

    # Selecionar Áudios Cortados Disponíveis
    st.subheader("Selecione os Áudios Cortados")
    audio_files = list_files_in_folder('audio/programa')  # Caminho corrigido
    selected_audio = st.selectbox("Escolha um áudio para ouvir e adicionar", audio_files)

    if selected_audio:
        audio_path = os.path.join('audio/programa', selected_audio)

        # Reproduzir o áudio selecionado
        st.audio(audio_path, format='audio/wav')

        # Adicionar à sequência
        if 'sequence' not in st.session_state:
            st.session_state.sequence = []

        if st.button(f"Adicionar {selected_audio} à sequência"):
            st.session_state.sequence.append(selected_audio)

    # Exibir e Gerenciar Sequência Atual
    if 'sequence' in st.session_state and st.session_state.sequence:
        st.subheader("Sequência Atual")
        updated_sequence = st.session_state.sequence[:]
        for idx, audio in enumerate(updated_sequence):
            col1, col2, col3, col4 = st.columns([6, 1, 1, 1])
            with col1:
                st.write(f"{idx + 1}. {audio}")
            with col2:
                if st.button("↑", key=f"up_{idx}_{audio}"):
                    if idx > 0:
                        updated_sequence[idx], updated_sequence[idx - 1] = updated_sequence[idx - 1], updated_sequence[idx]
                        st.session_state.sequence = updated_sequence
            with col3:
                if st.button("↓", key=f"down_{idx}_{audio}"):
                    if idx < len(updated_sequence) - 1:
                        updated_sequence[idx], updated_sequence[idx + 1] = updated_sequence[idx + 1], updated_sequence[idx]
                        st.session_state.sequence = updated_sequence
            with col4:
                if st.button("Remover", key=f"remove_{idx}_{audio}"):
                    updated_sequence.pop(idx)
                    st.session_state.sequence = updated_sequence

        # Pré-visualização da sequência
        if st.button("Ouvir Sequência Completa"):
            final_audio = AudioSegment.empty()
            for audio in st.session_state.sequence:
                audio_path = os.path.join('audio/programa', audio)
                try:
                    audio_segment = AudioSegment.from_file(audio_path)
                    final_audio += audio_segment
                except FileNotFoundError:
                    st.error(f"Arquivo não encontrado: {audio_path}")
                    continue

            # Converter o áudio final para um formato que pode ser reproduzido no Streamlit
            preview_audio = BytesIO()
            final_audio.export(preview_audio, format="wav")
            preview_audio.seek(0)

            st.audio(preview_audio, format='audio/wav')

    # Exportar Programa de Rádio e Sequência em TXT
    if st.session_state.sequence:
        st.subheader("Gerar Programa e a Sequência")

        # Permitir ao usuário definir o nome do arquivo
        program_name = st.text_input("Nome do Programa", value="programa_final")

        if st.button("Gerar Programa"):
            # Exportar a sequência de áudios em um arquivo .txt
            sequence_txt = "\n".join([f"{idx + 1}. {audio}" for idx, audio in enumerate(st.session_state.sequence)])
            sequence_file = BytesIO(sequence_txt.encode('utf-8'))

            st.download_button(
                label="Baixar Sequência em TXT",
                data=sequence_file,
                file_name=f"{program_name}_sequencia.txt",
                mime="text/plain"
            )

            # Exportar o programa de rádio completo
            final_audio = AudioSegment.empty()
            for audio in st.session_state.sequence:
                audio_path = os.path.join('audio/programa', audio)
                try:
                    audio_segment = AudioSegment.from_file(audio_path)
                    final_audio += audio_segment
                except FileNotFoundError:
                    st.error(f"Arquivo não encontrado: {audio_path}")
                    continue

            # Salvar o programa de rádio final em memória
            export_audio_program = BytesIO()
            final_audio.export(export_audio_program, format="mp3")
            export_audio_program.seek(0)

            # Baixar o arquivo final
            st.download_button(
                label="Baixar Programa Completo",
                data=export_audio_program,
                file_name=f"{program_name}.mp3",
                mime="audio/mpeg"
            )

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
        options=["Home", "Upload de Video" , "Extrair Áudio", "Tratar Áudio", "Converter Áudio", "Analisar Áudio", "Cortar Áudio", "Criar Programa", "Gerenciar Arquivos"],
        icons=["house", "cloud-download","cloud-upload", "tools", "headphones", "graph-up-arrow", "scissors", "music-note", "folder"],
        menu_icon="cast",  # Ícone do menu
        default_index=0,  # A primeira opção é "Home"
        orientation="horizontal",
    )

    if selected_section == "Home":
        st.write("Bem-vindo ao Processamento de Áudio. Use o menu acima para selecionar uma ação.")

    elif selected_section == "Upload de Video":
        st.subheader("Upload de Vídeos")
        uploaded_videos = st.file_uploader("Faça upload dos seus vídeos", accept_multiple_files=True, type=["mp4", "mov", "avi"])

        if uploaded_videos:
            for uploaded_video in uploaded_videos:
                video_path = os.path.join(input_folder, uploaded_video.name)
                with open(video_path, "wb") as f:
                    f.write(uploaded_video.getbuffer())
                st.success(f"Arquivo {uploaded_video.name} salvo com sucesso!")

        st.subheader("Upload Vídeo do YouTube")
        youtube_url = st.text_input("Insira a URL do vídeo do YouTube")
        if st.button("Upload Vídeo do YouTube"):
            if youtube_url:
                resultado = download_youtube_video_with_ytdlp(youtube_url, input_folder)
                if "Erro ao baixar o vídeo" in resultado:
                    resultado = download_youtube_video_with_pytube(youtube_url, input_folder)
                st.success(resultado)
            else:
                st.error("Por favor, insira uma URL válida.")

        if st.button('Fazer upload do Google Drive'):
            st.info("Funcionalidade de upload do Google Drive ainda não implementada.")

    elif selected_section == "Extrair Áudio":
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

    elif selected_section == "Cortar Áudio":
        cortar_audio()

    elif selected_section == "Criar Programa":
        criar_programa_de_radio()

    elif selected_section == "Gerenciar Arquivos":
        st.subheader("Gerenciar Arquivos de Áudio")
        folder_option = st.selectbox("Selecione a pasta", ["staging", "treated", "converted", "videos"])
        folder_mapping = {"staging": staging_folder, "treated": treated_folder, "converted": converted_folder, "videos": input_folder}
        selected_folder = folder_mapping[folder_option]

        files = list_files_in_folder(selected_folder)
        if files:
            st.write(f"Arquivos na pasta {folder_option}:")
            for file in files:
                file_path = os.path.join(selected_folder, file)
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(file)
                with col2:
                    if st.button('Excluir', key=f'delete_{file}'):
                        if delete_file(file_path):
                            st.success(f"Arquivo {file} excluído com sucesso!")
                            files.remove(file)
                        else:
                            st.error(f"Erro ao excluir o arquivo {file}.")
                with col3:
                    st.download_button(
                    label="Download",
                    data=get_file_as_bytes(file_path),
                    file_name=file,
                    mime='application/octet-stream'
                )
        else:
            st.write(f"Não há arquivos na pasta {folder_option}.")

        if st.button('Limpar Pasta Selecionada'):
            clear_folder(selected_folder)
            st.success(f"Pasta {folder_option} limpa com sucesso!")
            files = list_files_in_folder(selected_folder)

if __name__ == "__main__":
    main()
