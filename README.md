````md
# AI Resume Screening & Technical Assessment Platform

An end-to-end recruitment pipeline built with Python and Django that automates candidate screening, resume analysis, technical assessment, and candidate ranking using machine learning and AI.

This project goes beyond traditional ATS systems by combining resume parsing, semantic matching, AI-assisted evaluation, and adaptive technical testing into one workflow.

---

## Features

### Resume Upload & Processing
- Upload resumes in PDF format
- Extract raw text from resumes
- Clean and preprocess noisy resume content
- Handle multiple resume layouts and formatting styles

Extracted information includes:
- Skills
- Experience
- Education
- Projects
- Certifications

---

### Job Role Classification
Predict candidate job roles using machine learning models.

Example roles:
- Backend Developer
- Data Scientist
- Machine Learning Engineer
- Frontend Developer

Pipeline:
- Text preprocessing
- Feature vectorization
- Classification model inference

---

### Semantic Resume Matching
Measure how well a candidate matches a job description.

Methods used:
- TF-IDF
- Word Embeddings
- Cosine Similarity
- Random Forest scoring

Matching considers:
- Skill overlap
- Semantic relevance
- Experience relevance

Outputs:
- Match score
- Missing skills
- Candidate ranking

---

### Skill Extraction (NER Pipeline)
Extract technical skills and domain-specific keywords.

Examples:
- Python
- Django
- FastAPI
- AWS
- Docker
- Machine Learning

Used for:
- Candidate profiling
- Test generation
- Role matching

---

### AI-Generated Content Detection
Detect suspicious AI-generated or templated resumes.

Signals include:
- Repetitive sentence structure
- Buzzword density
- Statistical language patterns

Helps flag suspicious submissions for manual review.

---

### Candidate Verification System
Identity verification before technical assessment.

Includes:

#### Photo Clarity Check
Uses Laplacian variance to detect blurry images.

#### Face Detection
Detects valid face presence.

#### Blink Test
Uses Euclidean distance between eye landmarks for liveness detection.

Optional:
- Multiple face detection
- Anti-cheating checks

---

### Technical Assessment Engine

#### Objective Questions
Multiple-choice technical questions.

Topics:
- Python
- SQL
- Computer Science fundamentals

#### Subjective Questions
Open-ended questions evaluated with LLM-assisted scoring.

Evaluation criteria:
- Relevance
- Correctness
- Depth

#### Aptitude Test
Logical reasoning and problem-solving.

#### Programming Assessment
Coding questions with automated evaluation.

Supports:
- Hidden test cases
- Functional validation
- Automated scoring

---

### Adaptive Question Generation
Questions are tailored based on:
- Resume skills
- Job position
- Candidate level

Question metadata:
- Job position
- Difficulty level
- Question type

---

### Candidate Ranking Engine

Final ranking combines multiple weighted scores.

Example:

```text
Final Score =
0.30 × Resume Match +
0.20 × Objective +
0.20 × Subjective +
0.15 × Aptitude +
0.15 × Programming
````

Weights can be adjusted depending on job role.

---

## Tech Stack

### Backend

* Python
* Django
* Django ORM

### Machine Learning / AI

* Scikit-learn
* TF-IDF
* Word2Vec
* Random Forest
* Cosine Similarity

### Computer Vision

* OpenCV
* dlib
* face_recognition

### Database

* SQLite (Development)
* PostgreSQL (Production)

### Async / Background Tasks

* Task queues
* Email verification workers

---

## System Workflow

```text
Recruiter Creates Job Posting
          ↓
Candidate Uploads Resume
          ↓
Resume Parsing & Cleaning
          ↓
Skill Extraction
          ↓
Resume Matching
          ↓
Candidate Verification
          ↓
Technical Test Generation
          ↓
Assessment Evaluation
          ↓
Final Candidate Ranking
```

---

## Project Structure

```bash
resume_screening/
│
├── resumeapp/
│   ├── models.py
│   ├── views.py
│   ├── utils.py
│   ├── tasks.py
│   ├── cosine.py
│   ├── titlepredictor.py
│   ├── templates/
│   └── static/
│
├── media/
├── requirements.txt
└── manage.py
```

---

## Installation

Clone repository:

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start development server:

```bash
python manage.py runserver
```

---

## Future Improvements

* Dockerized code execution sandbox
* Support for multiple programming languages
* Advanced proctoring
* Microservice architecture
* Cloud deployment
* LLM-based interview feedback

---

## Motivation

Traditional ATS systems rely heavily on keyword matching and often fail to assess real candidate capability.

This project aims to:

* Reduce recruiter workload
* Improve candidate-job matching
* Evaluate actual technical competence
* Explore scalable AI-assisted backend systems

---

## License

MIT License

```
```
