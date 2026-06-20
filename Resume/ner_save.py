import spacy
from spacy.matcher import PhraseMatcher
SKILL_LIST = [
    # =========================
    # Frontend
    # =========================
    "html", "html5", "css", "css3", "javascript", "typescript",
    "react", "next.js", "vue.js", "nuxt.js", "angular", "svelte",
    "redux", "tailwind css", "bootstrap", "sass", "less", "material ui",
    "webpack", "vite", "babel", "jquery", "ajax",
    "d3.js", "three.js", "responsive design", "web accessibility",
    "figma", "adobe xd", "photoshop",

    # =========================
    # Backend
    # =========================
    "java", "python", "node.js", "c#", "php", "ruby", "go", "scala",
    "spring boot", "django", "flask", "fastapi", "express.js", ".net",
    "rest api", "graphql", "grpc", "microservices",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "oracle", "sql server", "cassandra", "dynamodb", "elasticsearch",
    "neo4j", "firebase", "rabbitmq", "kafka",

    # =========================
    # Fullstack
    # (covers integration-heavy tools that span both ends;
    # frontend/backend basics above already apply here too)
    # =========================
    "mern stack", "mean stack", "next.js", "nestjs",
    "websockets", "jwt", "oauth", "api integration",
    "git", "github", "gitlab", "bitbucket", "ci/cd",

    # =========================
    # AI / Machine Learning / Data
    # =========================
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "matplotlib", "seaborn", "opencv",
    "nltk", "spacy", "gensim", "hugging face", "transformers",
    "xgboost", "lightgbm", "catboost", "fastai", "mlflow",
    "spark", "pyspark", "hadoop", "airflow", "data engineering",
    "llm", "generative ai", "prompt engineering", "rag",

    # =========================
    # DevOps
    # =========================
    "docker", "kubernetes", "terraform", "ansible", "jenkins",
    "github actions", "gitlab ci", "circleci", "travis ci", "teamcity",
    "aws", "azure", "gcp", "linux", "ubuntu", "centos",
    "bash", "shell scripting", "powershell",
    "nginx", "apache", "grafana", "prometheus", "elk stack",
    "helm", "argo cd", "monitoring", "infrastructure as code",

    # =========================
    # Cybersecurity
    # =========================
    "cybersecurity", "information security", "network security",
    "application security", "endpoint security", "cloud security",
    "iam", "vulnerability management", "risk assessment", "threat modeling",
    "penetration testing", "ethical hacking", "kali linux", "metasploit",
    "nmap", "burp suite", "owasp zap", "nessus", "nikto",
    "sql injection", "xss", "csrf", "privilege escalation",
    "ids/ips", "snort", "suricata", "firewall",
    "cisco asa", "palo alto", "fortinet", "checkpoint",
    "siem", "soc", "splunk", "ibm qradar", "logrhythm", "solarwinds",
    "threat hunting", "threat intelligence", "mitre att&ck",
    "malware analysis", "phishing detection",
    "edr", "xdr", "crowdstrike", "symantec endpoint protection",
    "incident response", "digital forensics", "encryption",
    "ftk imager", "pci-dss", "gdpr", "hipaa", "iso 27001",
    "security audit",

    # =========================
    # QA / Testing
    # =========================
    "manual testing", "automation testing", "selenium", "cypress",
    "playwright", "junit", "testng", "pytest", "mocha", "jest",
    "postman", "soapui", "jmeter", "loadrunner",
    "test case design", "regression testing", "api testing",
    "performance testing", "bug tracking",

    # =========================
    # Soft / Project Management (cross-cutting, all categories)
    # =========================
    "agile", "scrum", "kanban", "jira", "confluence",
    "project management", "stakeholder communication",
]

_nlp = spacy.blank("en")
_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
_patterns = [_nlp.make_doc(skill) for skill in SKILL_LIST]
_matcher.add("SKILLS", _patterns)


def create_ner_pool(jobseeker):
    if not jobseeker.resume or not jobseeker.processed_text:
        return

    doc = _nlp(jobseeker.processed_text)
    matches = _matcher(doc)

    skills = set()
    for match_id, start, end in matches:
        skill = doc[start:end].text.lower().strip()
        skills.add(skill)

    jobseeker.skill_ner = list(skills)
    jobseeker.save()