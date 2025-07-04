from django.contrib import admin
from .models import Answer,Question,JobSeekerRegister, JobProviderRegister,Job,UserProfile

admin.site.register(JobSeekerRegister)

admin.site.register(JobProviderRegister)

admin.site.register(Job)

admin.site.register(UserProfile)

admin.site.register(Question)

admin.site.register(Answer)
