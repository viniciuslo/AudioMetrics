# video_fetcher.py

import os
import yt_dlp as youtube_dl
from pytube import YouTube

def download_youtube_video_with_ytdlp(url, destination_folder):
    """
    Baixa um vídeo do YouTube usando yt-dlp.
    
    :param url: URL do vídeo do YouTube.
    :param destination_folder: Pasta de destino onde o vídeo será salvo.
    """
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "Download concluído com sucesso!"
    except Exception as e:
        return f"Erro ao baixar o vídeo com yt-dlp: {e}"

def download_youtube_video_with_pytube(url, destination_folder):
    """
    Fallback para baixar um vídeo do YouTube usando pytube caso yt-dlp falhe.
    
    :param url: URL do vídeo do YouTube.
    :param destination_folder: Pasta de destino onde o vídeo será salvo.
    """
    try:
        yt = YouTube(url)
        video_streams = yt.streams.filter(file_extension="mp4", progressive=True).order_by('resolution').desc()
        stream = video_streams.first()
        
        if not stream:
            raise Exception("Nenhum stream de vídeo compatível encontrado.")
        
        stream.download(output_path=destination_folder)
        return f"Vídeo '{yt.title}' baixado com sucesso na resolução {stream.resolution}!"
    except Exception as e:
        return f"Erro ao baixar o vídeo com pytube: {e}"
