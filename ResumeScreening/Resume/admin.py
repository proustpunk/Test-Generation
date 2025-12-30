from django.contrib import admin
from .models import Candidate,CandidateLog,Answer,Question,JobSeekerRegister, JobProviderRegister,Job,UserProfile,JobApplication

admin.site.register(JobSeekerRegister)

admin.site.register(JobProviderRegister)

admin.site.register(Job)

admin.site.register(UserProfile)

admin.site.register(Question)

admin.site.register(Answer)

admin.site.register(Candidate)

admin.site.register(CandidateLog)
admin.site.register(JobApplication)
