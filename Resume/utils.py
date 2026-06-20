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
import requests
from sentence_transformers import SentenceTransformer
from .classifier_with_labels import SVMWithLabels


from .models import JobSeekerRegister

from sklearn.feature_extraction.text import TfidfVectorizer





CATEGORY_WEIGHTS = {
    'datascience': {
        'code': 0.40,
        'objective': 0.30,
        'mcq': 0.13,
        'subjective': 0.17,
    },
    'software developer': {
        'code': 0.50,
        'objective': 0.30,
        'mcq': 0.10,
        'subjective': 0.10,
    },
    'cybersecurity specialist': {
        'code': 0.48,
        'objective': 0.28,
        'mcq': 0.14,
        'subjective': 0.10,
    },
    'devops engineer': {
        'code': 0.42,
        'objective': 0.30,
        'mcq': 0.18,
        'subjective': 0.10,
    },
    'graphics engineer': {
        'code': 0.30,
        'objective': 0.20,
        'mcq': 0.20,
        'subjective': 0.30,
    },
    'machine learning engineer': {
        'code': 0.47,
        'objective': 0.28,
        'mcq': 0.10,
        'subjective': 0.15,
    },
    'robotics engineer': {
        'code': 0.46,
        'objective': 0.29,
        'mcq': 0.10,
        'subjective': 0.15,
    },
}


lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

current_dir = os.path.dirname(__file__)

model_path = os.path.join(current_dir, 'sentencebert')
model = SentenceTransformer(model_path)

classifier_model_joblib = os.path.join(current_dir, 'rf_sentencebert.joblib')

category_mapping_path = os.path.join(current_dir, 'category_mapping_rf_sentencebert.json')
classifier_with_labels = SVMWithLabels.load(classifier_model_joblib, category_mapping_path)



# def clean_text(text):
#     text = re.sub(r'\W',' ', text)
#     text = re.sub(r"\b\w{1}\b", '', text) 
#     text = re.sub(r"(\b\w+)'\b", r"\1", text)
#     text = text.lower()
#     return text


def chunk_text(text, max_words=150):
    words = text.split()
    chunks = [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]
    return chunks

def clean_text(text):
    """
    Cleaning function optimized for Sentence-BERT embeddings.
    Keeps sentence structure and context - ONLY removes PII and formatting artifacts.
    DOES NOT remove stopwords or tokenize into words.
    """
    
    # Convert to string and lowercase
    text = str(text).lower()
    
    # ============= REMOVE PII AND METADATA =============
    # Remove emails
    text = re.sub(r'\S+@\S+\.\S+', ' ', text)
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    # Remove GitHub/LinkedIn/Twitter handles
    text = re.sub(r'github\.com/[\w-]+/?[\w-]*/?', ' ', text)
    text = re.sub(r'linkedin\.com/in/[\w-]+', ' ', text)
    text = re.sub(r'@[\w-]+', ' ', text)
    # Remove phone numbers
    text = re.sub(r'\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', ' ', text)
    text = re.sub(r'\b\d{10,15}\b', ' ', text)
    # Remove dates (years, ranges)
    text = re.sub(r'\b(19|20)\d{2}\b', ' ', text)
    text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', ' ', text)
    text = re.sub(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(present|current|now)\b', ' ', text, flags=re.IGNORECASE)
    # Remove location/Zip codes
    text = re.sub(r'\b\d{5}(?:-\d{4})?\b', ' ', text)
    
    # ============= REMOVE SECTION HEADERS =============
    section_headers = [
        r'\b(profile|summary|professional summary|about me|bio|introduction|overview|executive summary)\b',
        r'\b(technical skills|skills|core competencies|tech stack|toolbox|expertise|proficiencies|capabilities)\b',
        r'\b(soft skills|interpersonal skills)\b',
        r'\b(projects|portfolio|featured work|case studies|side projects|key projects|selected projects|notable projects)\b',
        r'\b(work experience|professional experience|employment history|career history|work history|relevant experience)\b',
        r'\b(education|academic background|formal education|degrees|schooling|coursework)\b',
        r'\b(certifications|certificates|credentials|badges|licenses|continuing education)\b',
        r'\b(achievements|awards|honors|recognition|accomplishments)\b',
        r'\b(languages|spoken languages|human languages)\b',
        r'\b(volunteer|community involvement|open source contributions|community work)\b',
        r'\b(additional projects|other projects|miscellaneous)\b',
        r'\b(references|publications|conferences|speaking|hobbies|interests|memberships)\b',
    ]
    for pattern in section_headers:
        text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
    
    # ============= REMOVE FORMATTING ARTIFACTS =============
    # Remove separators
    separators = [r'={3,}', r'-{3,}', r'\*{3,}', r'_{3,}', r'─{3,}', r'━{3,}', r'•{3,}', r'◦{3,}']
    for pattern in separators:
        text = re.sub(pattern, ' ', text)
    
    # Remove bullet points and special symbols
    bullets = [r'[•·▪▫◦‣⁃➢➣►▶❯❭›]', r'[●○◆◇□■]', r'[→⇒⇨⟶➔]', r'[✓✔✓✓]', r'[–—]', r'[【】]', r'[《》]', r'[❯❭]']
    for pattern in bullets:
        text = re.sub(pattern, ' ', text)
    
    # Remove markdown/formatting characters (but keep meaningful punctuation)
    text = re.sub(r'\*+', ' ', text)
    text = re.sub(r'_{2,}', ' ', text)
    text = re.sub(r'`+', ' ', text)
    text = re.sub(r'#+', ' ', text)
    
    # ============= CLEAN TEXT CONTENT (KEEP SENTENCE STRUCTURE) =============
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # Remove extra punctuation but keep sentence structure
    # Keep: periods, commas, question marks, exclamation points, apostrophes, hyphens
    text = re.sub(r"[^a-zA-Z0-9\s\.\,\!\?\:\;\-\']", ' ', text)
    
    # Fix spacing around punctuation
    text = re.sub(r"\s+'\s+", "'", text)
    text = re.sub(r"\s+-\s+", '-', text)
    text = re.sub(r"\s+\.\s+", '. ', text)
    text = re.sub(r"\s+,\s+", ', ', text)
    text = re.sub(r"\s+\?\s+", '? ', text)
    text = re.sub(r"\s+!\s+", '! ', text)
    
    # Remove standalone numbers (but keep numbers attached to words like "react18")
    text = re.sub(r'\b\d+(?:\.\d+)?\b', ' ', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing spaces
    text = text.strip()
    
    # ============= KEEP AS STRING (DO NOT TOKENIZE) =============
    # For Sentence-BERT, we want the full text, not tokenized words
    # Remove single letters (except common tech short forms)
    tech_short = {'c', 'go', 'r', 'c#', 'f#'}
    words = text.split()
    # Keep words that are >1 character OR are in tech_short
    words = [w for w in words if len(w) > 1 or w in tech_short]
    text = ' '.join(words)
    
    return text

jobseekers = JobSeekerRegister.objects.all()
corpus = []
for seeker in jobseekers:
    resume_file_path = seeker.resume.path
    if seeker.resume and os.path.exists(seeker.resume.path):
  
        with open(resume_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            cleaned_text = clean_text(text) 
            corpus.append(cleaned_text)
    vectorizer = TfidfVectorizer()
    vectorizer.fit(corpus)

def handle_pdf(file_path):
    text = ""
    try:
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""



    except Exception as e:
        print ("error {e}")

    return text



def get_vector(text): 
    return model.encode(text)

    # vectors = [model.wv[word] for word in processed_text if word in model.wv]

    # if vectors:
    #     return np.mean(vectors, axis=0)
    
    # else:
    #     return np.zeros(model.vector_size)
    
def process_file(file_instance):
    file_path = file_instance.resume.path #in models

    # Open and read the file

    if file_path.endswith('.pdf'):
        text = handle_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
          text = file.read()

    # Preprocess the text
    text = clean_text(text)
    resume_chunks = chunk_text(text)
    resume_vector = get_vector(text)
    resume_chunk_vectors = [get_vector(chunk).tolist() for chunk in resume_chunks]
    # tokens = word_tokenize(text)

    # # Lemmatize and stem each word
    # processed_tokens = [lemmatizer.lemmatize(stemmer.stem(word)) for word in tokens]
   # resume_vector = get_vector(processed_tokens, model)
    # Vectorize with Word2Vec
    predicted_category = classifier_with_labels.predict([resume_vector])[0]

    # Save processed data back to the model
    file_instance.processed_text = text  # Store tokens in the database
    file_instance.vector = resume_chunk_vectors           # Store vectors in the database
    file_instance.prediction = predicted_category
    file_instance.save()

def process_file_description(file_instance):
    file_path = file_instance.job_description_file.path #in models

    if file_path.endswith('.pdf'):
        text = handle_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8',errors='ignore') as file:
          text = file.read()

   
    text = clean_text(text)
    jd_chunks = chunk_text(text)
    jd_chunk_vectors = [get_vector(chunk).tolist() for chunk in jd_chunks]
    # tokens = word_tokenize(text)

   
    # processed_tokens = [lemmatizer.lemmatize(stemmer.stem(word)) for word in tokens]

   
    file_instance.processed_description = text  
    file_instance.description_vector = jd_chunk_vectors           
   
    file_instance.save()



def stuffing_check(text):
    target_resume = text
    vector = vectorizer.transform([target_resume])
    scores = vector.toarray()[0]
    words = vectorizer.get_feature_names_out()


    stuffed_words = []

    for i in range(len(scores)):
        if scores[i] > 0.1:
            stuffed_words.append((words[i], scores[i]))
    print(len(stuffed_words))
    is_suspicious = len(stuffed_words) > 1

    return is_suspicious
        
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
modelgpt = GPT2LMHeadModel.from_pretrained("gpt2")
modelgpt.eval()


def calculate_perplexity(text):
    tokens = tokenizer.encode(text, return_tensors='pt', truncation=True, max_length=512)
    with torch.no_grad():
        outputs = modelgpt(tokens, labels=tokens)
        loss = outputs.loss
    return torch.exp(loss).item()


def is_ai_written_resume(text, perplexity_threshold=40):
    try:
        perplexity = calculate_perplexity(text)
        return perplexity < perplexity_threshold  #low is AI
    except Exception as e:
        print(f"Perplexity check error: {e}")
        return False

#needs langchain 
def generate_reference(question_text):

    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
    modelgpt = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")

    prompt =( f"""You are an intelligent, professional candidate answering interview-style subjective questions. 
Speak as a thoughtful human with professional tone: be concise, clear, and reasoned. 
Include relevant technical terms naturally (do not force jargon). Do not repeat the question. 
Give a short plan or rationale and a final one-sentence takeaway.

Example 1:
Q: What would you do if you were the CEO of a mid-size tech startup facing slowing growth?
A: I would start by diagnosing the slowdown through customer feedback and product analytics to identify the weakest retention and acquisition points. I would convene leadership to prioritize product improvements that directly address those friction points and reallocate marketing budget toward channels with proven ROI. I would invest in a small, cross-functional squad to ship one high-impact experiment within 60 days and measure lift with A/B tests. I would also focus on talent retention by clarifying goals and supporting managers to remove blockers. Takeaway: prioritize measurable experiments that improve customer retention while aligning the team around clear, short-term targets.

Example 2:
Q: How do you approach learning a new programming language when starting a project?
A: I identify the language’s idioms and standard libraries relevant to the problem, then scaffold a small prototype that exercises the language’s strengths. I read the official style guide and implement unit tests as I build to surface pitfalls early. I allocate time for one focused refactor after the prototype to adopt best practices and improve maintainability. I also consult one or two high-quality open-source examples to learn idiomatic patterns. Takeaway: learn by building a focused, test-backed prototype and refactor with idioms in mind.

Now answer the question below following the same voice, structure, and constraints:

Question: {question_text}
"""
)

    
    inputs = tokenizer(prompt, return_tensors="pt")
    
    output_ids = modelgpt.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.0,  # controls randomness
        do_sample=False,   # enables variability
        top_p=0.9         # nucleus sampling
    )
    
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)
