from celery import shared_task
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import JobApplication, Job,Candidate
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render, redirect
import pytz
@shared_task(name="check_job_deadlines")
def check_job_deadlines():
    now_utc = timezone.now()  # UTC now
    ktm_tz = pytz.timezone('Asia/Kathmandu')
    ktm_now = now_utc.astimezone(ktm_tz)

    # Get all active jobs whose deadline has passed in UTC
    jobs = Job.objects.filter(
        deadline__lte=now_utc,
        email_sent=False,
        active=True
    )

    domain = settings.SITE_DOMAIN

    for job in jobs:
        # Convert each job deadline to KTM for comparison
        job_deadline_ktm = job.deadline.astimezone(ktm_tz)

        if ktm_now >= job_deadline_ktm:
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


@shared_task(name="check_final_deadlines")
def check_final_deadlines():
    now = timezone.now()

    candidates = Candidate.objects.filter(
        final_deadline_date__lte=now,
        final_email_sent=False
    )

    job_ids = candidates.values_list("job_id", flat=True).distinct()

    for job_id in job_ids:
        send_final_selection_email.delay(job_id)

    return f"Processed {len(job_ids)} jobs for final selection"


@shared_task
def send_final_selection_email(job_id):
    job = Job.objects.get(id=job_id)

    candidates = Candidate.objects.filter(
        job=job,
        final_email_sent=False
    ).order_by('-total_score')

    if not candidates.exists():
        return f"No candidates for job {job_id}"

    top_count = max(1, int(len(candidates) * 0.2))
    selected = candidates[:top_count]

    for candidate in selected:
        user = candidate.user

        send_mail(
            subject=f"Final Selection – {job.job_title}",
            message=(
                f"Dear {user.username},\n\n"
                f"You have been selected in the final list for the position: "
                f"{job.job_title}.\n\n"
                f"Congratulations.\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    candidates.update(final_email_sent=True)

    return f"Final emails sent for job {job_id}"



from django.contrib.auth import get_user_model
from .ner_save import create_ner_pool
from .models import JobSeekerRegister
from .authentication import build_and_send_verification_email  


@shared_task
def create_ner_pool_task(job_seeker_id):
    try:
        job_seeker = JobSeekerRegister.objects.get(id=job_seeker_id)
        create_ner_pool(job_seeker)
    except JobSeekerRegister.DoesNotExist:
        pass


@shared_task
def send_verification_email_task(user_id):
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        build_and_send_verification_email(user, settings.SITE_DOMAIN)
    except User.DoesNotExist:
        pass

