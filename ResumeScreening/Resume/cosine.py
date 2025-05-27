
from .models import Job,JobSeekerRegister
import numpy as np
from numpy.linalg import norm


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

def update_cosine(job_id):
    # Fetch the job description by job_id
    job = Job.objects.get(id=job_id)
    job_vector = np.array(job.description_vector)

    resumes = JobSeekerRegister.objects.filter(job_description=job)

    for resume in resumes:
        resume_vector = np.array(resume.vector)

        # Calculate the cosine similarity
        similarity_score = cosine_similarity(job_vector, resume_vector)

        resume.cosine_similarity_score = similarity_score
        resume.save()

    


