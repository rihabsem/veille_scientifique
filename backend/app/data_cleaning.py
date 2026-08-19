import string
import re
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
model = AutoModel.from_pretrained('distilbert-base-uncased')

def clean_data(data):
    data = data.lower()
    translator = str.maketrans('','',string.punctuation)
    data = data.translate(translator)
    data = re.sub('\s+', ' ', data)
    return data 

def get_embedding(data):
    inputs = tokenizer(
        data,
        return_tensors='pt',
        truncation=True,
        padding=True,
        max_length=512
    )
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1)
    return embedding.squeeze().tolist()








