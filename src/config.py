import os

# Diretórios
input_folder = './videos'
staging_folder = './audio/staging'
treated_folder = './audio/treated'
converted_folder = './audio/converted'

# Parâmetros de Processamento
noise_reduction_prop = 0.8
low_cutoff_frequency = 100
high_cutoff_frequency = 8000

# Função para criar diretórios, se não existirem
def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"A pasta {directory} foi criada.")
