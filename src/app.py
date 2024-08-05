import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from analyzer import analyze_audio_for_parameters, save_audio_analysis
from enhancer import AudioProcessor
from extractor import extract_audio
from pydub import AudioSegment
import plotly.express as px
import tempfile

# Função para coletar métricas de áudio
def collect_audio_metrics(folder):
    metrics_list = []

    if not os.path.exists(folder):
        st.error(f"A pasta '{folder}' não existe. Por favor, execute o processamento de áudio primeiro.")
        return pd.DataFrame()  # Retorna um DataFrame vazio

    for filename in os.listdir(folder):
        if filename.endswith('.wav') or filename.endswith('.mp3'):
            input_path = os.path.join(folder, filename)
            y, sr, prop_decrease, metrics = analyze_audio_for_parameters(input_path)
            metrics['filename'] = filename
            metrics_list.append(metrics)

    return pd.DataFrame(metrics_list)

# Função para processar o áudio
def process_audio(file, noise_reduction_prop, eq_cutoff):
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_input_path = os.path.join(tmpdir, file.name)
        with open(temp_input_path, 'wb') as f:
            f.write(file.getbuffer())

        processor = AudioProcessor()
        y, sr, prop_decrease, metrics = analyze_audio_for_parameters(temp_input_path)
        processed_audio_path = os.path.join(tmpdir, 'processed_audio.mp3')
        processor.enhance_audio(y, sr, prop_decrease, metrics, processed_audio_path, noise_reduction_prop, eq_cutoff)

        with open(processed_audio_path, 'rb') as f:
            processed_audio = f.read()

    return processed_audio, metrics, y, sr

# Função para gerar espectrograma
def generate_spectrogram(y, sr, title):
    plt.figure(figsize=(10, 4))
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title(title)
    st.pyplot(plt)

# Interface do Streamlit
st.set_page_config(page_title="Sistema de Processamento de Áudio", layout="wide")

with st.sidebar:
    selected = option_menu(
        "Menu Principal", 
        ["Extrair Áudio", "Tratar Áudio", "Converter Áudio", "Analisar Áudio"], 
        icons=['cloud-upload', 'wrench', 'repeat', 'bar-chart'],
        menu_icon="cast", 
        default_index=0,
    )

if selected == "Extrair Áudio":
    st.title("Extrair Áudio dos Vídeos")
    video_folder = st.text_input("Pasta de Vídeos", "./videos")
    output_folder = "./staging"
    if st.button("Extrair Áudio"):
        if os.path.exists(video_folder):
            extract_audio(video_folder, output_folder)
            st.success(f"Áudio extraído e salvo em {output_folder}")
        else:
            st.error("A pasta de vídeos não existe. Verifique o caminho e tente novamente.")

elif selected == "Tratar Áudio":
    st.title("Tratar Áudio Extraído")
    uploaded_file = st.file_uploader("Faça upload de um arquivo de áudio (WAV)", type=["wav"])
    noise_reduction_prop = st.slider("Proporção de Redução de Ruído", 0.0, 1.0, 0.5)
    eq_cutoff = st.slider("Corte de Equalização (Hz)", 500, 15000, 8000)
    if uploaded_file:
        st.audio(uploaded_file, format='audio/wav')
        if st.button("Processar Áudio"):
            processed_audio, metrics, y, sr = process_audio(uploaded_file, noise_reduction_prop, eq_cutoff)
            st.audio(processed_audio, format='audio/mp3')
            st.subheader("Métricas de Áudio")
            metrics_df = pd.DataFrame([metrics])
            st.write(metrics_df)
            selected_metric = st.selectbox(
                'Escolha uma métrica para visualizar',
                [col for col in metrics_df.columns if col != 'filename']
            )
            fig = px.box(metrics_df, y=selected_metric, points="all")
            st.plotly_chart(fig)
            st.subheader("Espectrograma Original")
            generate_spectrogram(y, sr, "Espectrograma Original")

elif selected == "Converter Áudio":
    st.title("Converter Áudio para MP3 sem Tratamento")
    staging_folder = "./staging"
    converted_folder = "./converted"
    if st.button("Converter Áudio"):
        if os.path.exists(staging_folder):
            for filename in os.listdir(staging_folder):
                if filename.endswith('.wav'):
                    input_path = os.path.join(staging_folder, filename)
                    converted_path = os.path.join(converted_folder, filename.replace('.wav', '.mp3'))
                    audio = AudioSegment.from_wav(input_path)
                    audio.export(converted_path, format='mp3')
                    st.success(f"Áudio convertido e salvo em {converted_folder}")
        else:
            st.error("A pasta staging não existe. Verifique o caminho e tente novamente.")

elif selected == "Analisar Áudio":
    st.title("Analisar Áudio")
    folder = st.selectbox("Escolha a pasta para análise", ["./staging", "./treated", "./converted"])
    if os.path.exists(folder):
        metrics_df = collect_audio_metrics(folder)
        if not metrics_df.empty:
            st.subheader("Métricas de Áudio")
            st.write(metrics_df)
            selected_metric = st.selectbox(
                'Escolha uma métrica para visualizar',
                [col for col in metrics_df.columns if col != 'filename']
            )
            fig = px.box(metrics_df, y=selected_metric, points="all")
            st.plotly_chart(fig)
        else:
            st.warning("Nenhum dado disponível para visualização. Por favor, execute o processamento de áudio primeiro.")
    else:
        st.error("A pasta selecionada não existe. Verifique o caminho e tente novamente.")
