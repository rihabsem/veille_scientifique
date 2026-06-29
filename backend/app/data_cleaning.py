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
    data = re.sub('\s+', '', data)
    return data

def get_embedding(data):
    inputs = tokenizer(
        data,
        return_tensors='pt',
        truncation=True,
        padding=True,
        max_length=512
    ) # the tokenizer model will convert each word to an id according to a existant vocabulary so a word sentence will be transformed to a vector of numbers (IDS) but this vector has no sense (it is not an embedding)
    with torch.no_grad():
        outputs = model(**inputs) #on obtient plusieurs vecteurs pour la même phrase
    embedding = outputs.last_hidden_state.mean(dim=1) #on fait la moyenne de tous les vecteurs pour obtenir un seul vecteur d'embedding pour la phrase
    return embedding.squeeze().tolist() #enleve les dimensions inutiles et transforme le tensor en json list pour pouvoir le stocker dans la base de données Chroma








