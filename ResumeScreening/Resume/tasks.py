from celery import shared_task
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import JobApplication, Job
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render, redirect

@shared_task(name="check_job_deadlines")
def check_job_deadlines():
    now = timezone.now()

    jobs = Job.objects.filter(
        deadline__lte=now,
        email_sent=False,
        active=True
    )

    domain = settings.SITE_DOMAIN

    for job in jobs:
        send_email_to_seekers_task.delay(job.id, domain)

        job.email_sent = True
        job.active = False
        job.save()

    return f"Processed {jobs.count()} expired jobs"



@shared_task
def send_email_to_seekers_task(job_id, domain):
    job = Job.objects.get(id=job_id)

    

    applications = JobApplication.objects.filter(job=job).order_by('-cosine_similarity_score')

    if not applications.exists():
        return f"No applicants for job {job_id}"

    top_count = max(1, int(len(applications) * 0.2)) 
    top_applications = applications[:top_count]

    for app in top_applications:
        seeker_email = app.job_seeker.user.email
        uid = urlsafe_base64_encode(force_bytes(app.job_seeker.user.pk))
        token = default_token_generator.make_token(app.job_seeker.user)
        test_link = f"http://{domain}/test-validation/{uid}/{token}/{job.id}"

        send_mail(
            subject=f"Test Invitation for {job.job_title}",
            message=f"Dear {app.job_seeker.user.username},\n\nYou have been selected to take a test for the job: {job.job_title}.\n\nLink: {test_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[seeker_email],
        )
    return f"Emails sent to top {top_count} applicants for job {job_id}"
