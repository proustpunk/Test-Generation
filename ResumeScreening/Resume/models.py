from django.conf import settings
from django.db import models
from django.contrib.auth.models import User



    


class JobProviderRegister(models.Model):


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    company_description = models.TextField()

    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name
    



class Job(models.Model):

    user = models.ForeignKey(User, models.CASCADE,null=True, related_name="job_post")
    job_title = models.CharField(max_length=200)
    job_description_file = models.FileField(upload_to='description/', blank=True, null=True)
    job_requirements = models.TextField()
    salary_range = models.CharField(max_length=100)
    job_location = models.CharField(max_length=200)
    posted_at = models.DateTimeField(auto_now_add=True)

    processed_description = models.TextField(blank=True, null=True)
    description_vector = models.JSONField(blank=True, null=True)

    application_count = models.PositiveIntegerField(default=0)  


    def __str__(self):
        return self.job_title
    
    

class JobSeekerRegister(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField()
    bio = models.TextField(blank=True, null=True)


    processed_text = models.TextField(blank=True, null=True)
    vector = models.JSONField(blank=True, null=True)
    prediction = models.CharField(max_length=100, blank=True, null=True)
    cosine_similarity_score = models.TextField(max_length=100, null=False, default=0)



    job_description = models.ForeignKey(Job,models.CASCADE,null=True)
    
    def __str__(self):
        return self.user.username



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_provider = models.BooleanField(default=False)  # True for job providers, False for job seekers

    def __str__(self):
        return self.user.username
