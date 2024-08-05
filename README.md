# Extração e Processamento de Áudio em Python

Este projeto tem como objetivo extrair, analisar e processar arquivos de áudio extraídos de vídeos. Ao longo do desenvolvimento deste projeto, exploramos diversas técnicas de processamento de áudio, análise métrica e melhorias na qualidade do som.

## Recursos

- Extração de Áudio: Extrai áudio de arquivos de vídeo e os salva como arquivos WAV.
- Processamento de Áudio: Aplica técnicas de redução de ruído, equalização e normalização para melhorar a qualidade do áudio.
- Conversão de Áudio: Converte arquivos de áudio WAV para MP3.
- Análise de Áudio: Analisa o áudio extraído, processado e convertido, gerando métricas detalhadas e espectrogramas.
- Visualização com Streamlit: Interface interativa para upload de arquivos, extração de áudio de vídeo e visualização da análise e processamento aplicados.

## Tecnologias e Bibliotecas Utilizadas

- Python: A linguagem de programação principal utilizada no projeto.
- Librosa: Biblioteca para análise e manipulação de áudio.
- Noisereduce: Biblioteca para redução de ruído em áudio.
- Matplotlib: Utilizada para visualização de métricas e espectrogramas.
- Streamlit: Framework para criação de aplicações web interativas.
- Concurrent.futures: Biblioteca para paralelização de tarefas, melhorando o desempenho do processamento.
- Pydub: Biblioteca para manipulação de arquivos de áudio.
- MoviePy: Utilizada para extração de áudio de vídeos.

## Estrutura do Projeto

```
.
├── audio
│   ├── converted
│   │   ├── [arquivos MP3 convertidos]
│   │   └── analysis
│   │       ├── [métricas e espectrogramas dos arquivos convertidos]
│   ├── staging
│   │   ├── [arquivos WAV extraídos]
│   │   └── analysis
│   │       ├── [métricas e espectrogramas dos arquivos extraídos]
│   └── treated
│       ├── [arquivos MP3 processados]
│       └── analysis
│           ├── [métricas e espectrogramas dos arquivos processados]
├── src
│   ├── analyzer.py
│   ├── enhancer.py
│   ├── extractor.py
│   ├── main.py
│   ├── config.py
│   └── app.py
├── notebook
│   └── AudioAnalysis.ipynb
├── README.md
├── requirements.txt
└── .venv
```

## Como Executar

### Pré-requisitos

- Python 3.8+
- FFmpeg

### Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/seu-nome/seu-repositorio.git
    cd seu-repositorio
    ```

2. Crie e ative um ambiente virtual:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    .venv\Scripts\activate  # Windows
    ```

3. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

### Uso

- Execute o script principal:

  ```bash
  python src/main.py
  ```

- Execute a aplicação Streamlit:

  ```bash
  streamlit run src/app.py
  ```

### Recursos

- Extração de Áudio: Selecione a opção 1 no menu para extrair áudio de vídeos.
- Processamento de Áudio: Selecione a opção 2 para processar o áudio extraído.
- Conversão de Áudio: Selecione a opção 3 para converter o áudio para MP3 sem processamento.
- Análise de Áudio: Selecione as opções 4, 5 ou 6 para analisar o áudio extraído, processado ou convertido, respectivamente.

### Interface Streamlit

- Faça o upload de um arquivo de vídeo e selecione a opção para extrair o áudio.
- Após a extração, visualize as opções de processamento e análise diretamente na interface.

### Métricas de Análise

- Taxa de Cruzamento por Zero: O número de vezes que o sinal cruza o eixo zero.
- Centróide Espectral: O centro de massa do espectro, relacionado à percepção do brilho do som.
- Largura de Banda Espectral: A largura do espectro, representando a faixa de frequências presentes no sinal.
- Planicidade Espectral: Mede o quão plano é o espectro, indicando se o som é mais ruidoso ou tonal.
- Roll-off Espectral: A frequência abaixo da qual uma porcentagem específica da energia total do espectro é encontrada.
- Desvio RMS: Mede a energia do sinal.

### Melhorias Futuras

- Implementação de um sistema de detecção automática de ruídos específicos, como latidos de cachorro, sons de carros, etc.
- Integração de modelos de aprendizado de máquina para aprimorar o processamento de áudio.
- Otimização adicional de desempenho para grandes volumes de dados.
- Melhorias no Front-End para usuarios da aplicacao.

