import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer

import numpy as np
import re

import pdfplumber

from gensim.models import Word2Vec
#from gensim.models.fasttext import FastText

import joblib
from .svm_with_labels import SVMWithLabels

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()


current_dir = os.path.dirname(__file__)

w2v_model_path = os.path.join(current_dir, 'w2v.model')
w2v_model = Word2Vec.load(w2v_model_path)

svm_model_path = os.path.join(current_dir, 'SVMD.joblib')


category_mapping_path = os.path.join(current_dir, 'category_mapping.json')
svm_with_labels = SVMWithLabels.load(svm_model_path, category_mapping_path)



def clean_text(text):
    text = re.sub(r'\W',' ', text)
    text = re.sub(r"\b\w{1}\b", '', text)  # This removes isolated single letters (e.g. "s")
    # Remove apostrophes that are typically attached to words (like in "how's" becoming "hows")
    text = re.sub(r"(\b\w+)'\b", r"\1", text)
    text = text.lower()
    return text



def handle_pdf(file_path):
    text = ""
    try:
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""



    except Exception as e:
        print ("error {e}")

    return text



def get_vector(processed_text, s_model): 


    vectors = [w2v_model.wv[word] for word in processed_text if word in w2v_model.wv]

    if vectors:
        return np.mean(vectors, axis=0)
    
    else:
        return np.zeros(w2v_model.vector_size)
    

def process_file(file_instance):
    file_path = file_instance.resume.path #in models

    # Open and read the file

    if file_path.endswith('.pdf'):
        text = handle_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
          text = file.read()

    # Preprocess the text
    text = clean_text(text)
    tokens = word_tokenize(text)

    # Lemmatize and stem each word
    processed_tokens = [lemmatizer.lemmatize(stemmer.stem(word)) for word in tokens]
    resume_vector = get_vector(processed_tokens, w2v_model)
    # Vectorize with Word2Vec
    predicted_category = svm_with_labels.predict([resume_vector])[0]

    # Save processed data back to the model
    file_instance.processed_text = processed_tokens  # Store tokens in the database
    file_instance.vector = resume_vector.tolist()           # Store vectors in the database
    file_instance.prediction = predicted_category
    file_instance.save()  


def process_file_description(file_instance):
    file_path = file_instance.job_description_file.path #in models

    if file_path.endswith('.pdf'):
        text = handle_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
          text = file.read()

   
    text = clean_text(text)
    tokens = word_tokenize(text)

   
    processed_tokens = [lemmatizer.lemmatize(stemmer.stem(word)) for word in tokens]
    resume_vector = get_vector(processed_tokens, w2v_model)

   
    file_instance.processed_description = processed_tokens  
    file_instance.description_vector = resume_vector.tolist()           
   
    file_instance.save() 