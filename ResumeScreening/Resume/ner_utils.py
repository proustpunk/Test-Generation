from spacy.training import Example
import os
import json
import random
import spacy


nlp = spacy.load("en_core_web_sm")

BASE_DIR = r"C:\MinorProject\ResumeScreening\Resume"
dataset_path = os.path.join(BASE_DIR, "newnerA.json")

data = []
with open(dataset_path, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)  
        data.append(item)

# Prepare TRAIN_DATA

TRAIN_DATA = []
for item in data:
    text = item.get("text", "")
    entities = []
    for ann in item.get("annotations", []):
        start, end, label = ann
        entities.append((start, end, label))
    TRAIN_DATA.append((text, {"entities": entities}))

# Add NER labels
ner = nlp.get_pipe("ner")
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable other pipes
pipe_exceptions = ["ner"]
unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
with nlp.disable_pipes(*unaffected_pipes):
    optimizer = nlp.resume_training()
    for iteration in range(30):
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], drop=0.2, sgd=optimizer, losses=losses)
        print(f"Iteration {iteration + 1}, Losses: {losses}")

# Save model
output_dir = os.path.join(os.getcwd(), "ner_modelA")
os.makedirs(output_dir, exist_ok=True)
nlp.to_disk(output_dir)
print(f"Saved fine-tuned model to {output_dir}")




model_path = "C:/MinorProject/ResumeScreening/ner_modelA"  
nlp = spacy.load(model_path)

# Your sample resume text
text = """


Name: John Doe
Email: john.doe@email.com
Phone: (123) 456-7890

Summary
Skilled Machine Learning Engineer with experience in developing, training, and deploying machine learning models. Proficient in using data processing techniques and ML frameworks to solve complex problems. Strong background in Python, R, and cloud platforms, with expertise in neural networks, deep learning, and data visualization.

Skills

Python, R, Java
TensorFlow, PyTorch, Keras
Machine learning algorithms (Supervised and Unsupervised Learning, Reinforcement Learning)
Natural Language Processing (NLP)
Data preprocessing (Normalization, Feature Engineering, Data Augmentation)
Model evaluation and performance metrics (Cross-validation, ROC, AUC, F1-Score)
Cloud computing platforms (AWS, GCP, Azure)
Version control (Git, GitHub)
Big Data Technologies (Hadoop, Spark)
Data visualization (Matplotlib, Seaborn, Plotly)
Containerization (Docker)
Professional Experience

Machine Learning Engineer | ABC Tech Solutions
Jan 2021 – Present

Design and implement machine learning models for predictive analysis using Python and TensorFlow.
Preprocess and clean large datasets using NumPy, Pandas, and Scikit-learn.
Develop and deploy deep learning models for natural language processing tasks such as text classification and sentiment analysis.
Collaborate with data engineers to streamline data pipelines using Apache Spark.
Conduct model evaluation and optimization for accuracy and performance.
Utilize cloud computing services like AWS and GCP to deploy ML models at scale.
Data Scientist | XYZ Innovations
Jul 2018 – Dec 2020

Applied machine learning algorithms to large-scale datasets to provide actionable insights.
Built and tested classification models using Scikit-learn, Keras, and XGBoost.
Collaborated with cross-functional teams to integrate machine learning models into production systems.
Produced reports and visualizations to explain model performance and results.
Education
Master of Science in Computer Science | University of ABC
Graduated: 2018

Bachelor of Science in Information Technology | University of XYZ
Graduated: 2016"""

# Run NER
doc = nlp(text)

# Print all recognized entities
for ent in doc.ents:
    print(ent.text, ent.label_)

