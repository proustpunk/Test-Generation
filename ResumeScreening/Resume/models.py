from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .embeddings import embed_text
    


class JobProviderRegister(models.Model):


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    company_description = models.TextField()

    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name
    



class Job(models.Model):
    user = models.ForeignKey(User, models.CASCADE, null=True, related_name="job_post")
    job_title = models.CharField(max_length=200)
    job_description_file = models.FileField(upload_to='description/', blank=True, null=True)
    job_requirements = models.TextField()
    salary_range = models.CharField(max_length=100)
    job_location = models.CharField(max_length=200)
    posted_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    processed_description = models.TextField(blank=True, null=True)
    description_vector = models.JSONField(blank=True, null=True)
    application_count = models.PositiveIntegerField(default=0)

    deadline = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.job_title
    
    

class JobSeekerRegister(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField()
    bio = models.TextField(blank=True, null=True)
    profile_pics = models.ImageField(upload_to='profile_pics/', null=True) #profile_pics variable points to profilee_pics directory. the directory itself isnt accessed.

    processed_text = models.TextField(blank=True, null=True)
    vector = models.JSONField(blank=True, null=True)
    prediction = models.CharField(max_length=100, blank=True, null=True)
    cosine_similarity_score = models.TextField(max_length=100, null=False, default=0)

    skill_ner = models.JSONField(blank=True,null=True)



    job_description = models.ForeignKey(Job,models.CASCADE,null=True)
    
    def __str__(self):
        return self.user.username



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_provider = models.BooleanField(default=False)  # True for job providers, False for job seekers

    def __str__(self):
        return self.user.username


from .utils import generate_reference

class Question(models.Model):

    QUESTION_TYPES = [
        ('objective', 'Objective'),
        ('mcq', 'MCQ'),
        ('subjective', 'Subjective'),
        ('code','Code'),
    ]

    DIFFICULTY_LEVEL = [
        ('basic','Basic'),
        ('intermediate','Intermediate'),
        ('hard','Hard'),
    ]

    CATEGORY_CHOICES = [
        ('data scientist', 'Data Science'),
        ('software developer', 'Software Developer'),
        ('cybersecurity specialist', 'Cybersecurity Specialist'),
        ('devops engineer', 'Devops engineer'),
        ('graphics engineer', 'Graphics engineer'),
        ('machine learning engineer', 'Machine Learning Engineer'),
        ('robotics engineer', 'Robotics Engineer'),
        
    ]


    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVEL)
    category = models.CharField(max_length=30,choices=CATEGORY_CHOICES)

    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)

    correct_answer = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        
    )

    test_cases = models.JSONField(blank=True,null=True)
    reference_answer = models.TextField(blank=True, null=True)
    reference_vector = models.JSONField(blank=True, null=True) #all-MiniLM-L6-v2 (SentenceTransformers) is tiny, fast on CPU, and gives high-quality semantic vectors for matching.

#Embedding dim = 384 → small storage (~1.5 KB per vector), fast math.

    def save(self, *args, **kwargs):
        if self.question_type == 'subjective':
            print('loaded because subjective')
            if self.reference_answer and not self.reference_vector:
                print('no ref answer')
                emb = embed_text(self.reference_answer)
                self.reference_vector = emb.tolist()
            elif not self.reference_answer:
                print('ref exists but no vector')
                prompt = f"Question:{self.question_text}\nGenerate a reference answer, about 5 sentence."
                self.reference_answer = generate_reference(prompt)
                emb = embed_text(self.reference_answer)
                self.reference_vector = emb.tolist()
        super().save(*args, **kwargs)

    created_at = models.DateTimeField(auto_now_add=True, blank=True,null=True)




class Answer(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_option = models.CharField(max_length=10, blank=True, null=True)

    written_answer = models.TextField(blank=True, null=True)

    score = models.FloatField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
class Candidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    answers = models.ManyToManyField(Answer)
    total_score = models.FloatField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    test_taken = models.BooleanField(default=False)
    final_deadline_date = models.DateTimeField()
    final_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.job.job_title}"




class CandidateLog(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="logs") #django creates a relation automatically but if we want to customize a name for it, its related name
    suspicious = models.BooleanField(default=False)
    flags = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for Candidate {self.candidate.id} at {self.created_at}"
    

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    job_seeker = models.ForeignKey(JobSeekerRegister, on_delete=models.CASCADE)
    resume_snapshot = models.FileField(upload_to='applied_resumes/')
    skill_ner_snapshot = models.JSONField(blank=True, null=True)
    vector_snapshot = models.JSONField(blank=True, null=True)
    processed_text_snapshot = models.JSONField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    cosine_similarity_score = models.TextField(max_length=100, null=False, default=0)
    prediction = models.CharField(max_length=100, blank=True, null=True)



    def __str__(self):
        return f"{self.job_seeker.user.username} applied to {self.job.job_title}"
