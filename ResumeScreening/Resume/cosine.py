from .models import Job, JobApplication
import numpy as np
from numpy.linalg import norm

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

def update_cosine(job_id):
    job = Job.objects.get(id=job_id)
    job_vector = np.array(job.description_vector)

    applications = JobApplication.objects.filter(job=job)

    for app in applications:
        if app.vector_snapshot:
            resume_vector = np.array(app.vector_snapshot)
            similarity_score = cosine_similarity(job_vector, resume_vector)
            app.cosine_similarity_score = similarity_score
            app.save()
