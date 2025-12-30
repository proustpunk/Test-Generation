import spacy
SKILL_LIST = [
    # Programming Languages & Scripts
    "java", "python", "c++", "scala", "sql", "bash", "node.js", "javascript", "typescript", "ruby", "go", "perl", "php", "r", "matlab", "swift", "kotlin", "c#", "shell scripting",

    # Data & Machine Learning Frameworks
    "tensorflow", "pytorch", "keras", "scikit-learn", "spark", "pyspark", "hadoop", "airflow", "xgboost", "lightgbm", "catboost", "fastai", "mlflow", "pandas", "numpy", "matplotlib", "seaborn", "opencv", "nltk", "spacy", "gensim", "machine learning", "deep learning",

    # Infrastructure & DevOps
    "ansible", "terraform", "kubernetes", "docker", "jenkins", "ci/cd", "git", "linux", "ubuntu", "centos", "apache", "nginx", "bash scripting", "powershell", "grafana", "prometheus", "elk stack", "monitoring", "travis ci", "circleci", "teamcity",

    # Databases & Data Stores
    "mongodb", "mysql", "postgresql", "redis", "cassandra", "sqlite", "oracle", "sql server", "dynamodb", "elasticsearch", "neo4j", "firebase", "hbase",

    # Web & Visualization Tools
    "react", "vue.js", "angular", "tableau", "powerbi", "d3.js", "plotly", "nlp", "flask", "django", "fastapi", "html", "html5", "css", "css3", "javascript", "ajax", "bootstrap", "sass", "less",

    # Misc / Soft Skills (optional)
    "agile", "scrum", "jira", "kanban", "gitlab", "bitbucket"
]
import spacy

def create_ner_pool(jobseeker):
    model_path = "C:/MinorProject/ResumeScreening/ner_modelA"
    nlp = spacy.load(model_path)

    if not jobseeker.resume:
        return

    resume_path = jobseeker.resume.path

    with open(resume_path, "r", encoding="utf-8") as f:
        text = f.read()

    doc = nlp(text)

    skills = []
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            skill = ent.text.lower().strip()
            if skill in SKILL_LIST:   # only keep valid skills
                skills.append(skill)

    skills = list(set(skills))  # remove duplicates
    jobseeker.skill_ner = skills 
    jobseeker.save()
