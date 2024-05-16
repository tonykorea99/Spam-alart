from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import joblib
from transformers import BertTokenizer
import numpy as np

# URL 벡터라이저 로드
url_vectorizer = joblib.load('C:/SERVER/vectorizer.joblib')

# URL 모델 로드
url_model = joblib.load('C:/SERVER/rf_classifier.joblib')

# GRU 모델 로드
text_model = load_model('C:/SERVER/smishing_model_gru.h5')

# BERT 토크나이저 로드
bert_model_directory = 'C:/SERVER/bert'
tokenizer = BertTokenizer.from_pretrained(bert_model_directory)

def predict_url(url):
    # URL 벡터라이징
    url_vector = url_vectorizer.transform([url])
    # URL 모델 예측
    prediction = url_model.predict(url_vector)
    # NumPy bool을 Python bool로 변환
    return bool(prediction[0] > 0.5)  # 확률 0.5 이상을 True로 간주


def predict_text(text):
    # 텍스트를 BERT 토크나이저를 사용하여 시퀀스로 변환
    encoded_input = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=100,
        padding='max_length',
        truncation=True,
        return_tensors='tf'
    )
    input_ids = encoded_input['input_ids']
    # GRU 모델 예측
    prediction = text_model.predict(input_ids)
    # 확률로 변환 (sigmoid 출력이므로 직접 확률 계산)
    probability = float(prediction[0, 0]) * 100  # 확률을 퍼센트로 변환
    return probability


