from celery import shared_task
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import JobApplication, Job
from django.conf import settings

@shared_task
def send_email_to_seekers_task(job_id, domain):
    job = Job.objects.get(id=job_id)

    # Only send emails if the job is closed
    if not job.active:  # job still open → do nothing
        return f"Job {job_id} is still active. Emails not sent."

    applications = JobApplication.objects.filter(job=job).order_by('-cosine_similarity_score')

    if not applications.exists():
        return f"No applicants for job {job_id}"

    # Calculate top 20%
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
