import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Exemplo de função para treinar o modelo de parâmetros de áudio
def train_audio_processing_model():
    # Carregar o dataset (substitua com o caminho correto)
    df = pd.read_csv('audio_noise_dataset.csv')
    
    # Features e rótulo
    X = df.drop(columns=['label'])
    y = df['label']
    
    # Dividir o dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Treinar o modelo
    model = RandomForestRegressor()  # Ou RandomForestClassifier para classificação
    model.fit(X_train, y_train)
    
    # Avaliação do modelo
    accuracy = model.score(X_test, y_test)
    print(f'Accuracy: {accuracy * 100:.2f}%')
    
    # Salvar o modelo
    joblib.dump(model, 'audio_processing_model.pkl')

if __name__ == '__main__':
    train_audio_processing_model()
