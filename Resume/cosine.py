from .models import Job, JobApplication
import numpy as np
from numpy.linalg import norm

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

def update_cosine(job_id):
    job = Job.objects.get(id=job_id)
    job_chunk_vectors = np.array(job.description_vector)

    applications = JobApplication.objects.filter(job=job)

    for app in applications:
        if app.vector_snapshot:
            resume_chunk_vectors = np.array(app.vector_snapshot)

            best_per_requirement = []
            for jd_chunk_vector in job_chunk_vectors:
                chunk_scores = [cosine_similarity(jd_chunk_vector, resume_chunk_vector) for resume_chunk_vector in resume_chunk_vectors]
                best_per_requirement.append(max(chunk_scores))

            similarity_score = sum(best_per_requirement) / len(best_per_requirement)
            app.cosine_similarity_score = similarity_score
            app.save()