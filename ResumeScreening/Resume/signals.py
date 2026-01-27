from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile,JobSeekerRegister,Job
from django.contrib.auth.models import User
from .utils import process_file, process_file_description
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


@receiver(post_save, sender=JobSeekerRegister)
def process_uploaded_file(sender, instance, created, **kwargs):
    if created:  
        process_file(instance)


@receiver(post_save, sender=Job)
def process_uploaded_file(sender, instance, created, **kwargs):
    if created:  # Ensure this runs only on creation
        process_file_description(instance) #check