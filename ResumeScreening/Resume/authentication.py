
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
def send_verification_email(request, user):

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    

    current_site = get_current_site(request)
    domain = current_site.domain


    verification_link = f"http://{domain}/verify-email/{uid}/{token}/"

    send_mail(

        subject = "Verify Your Email",
        message=f'Click this link to verify your email: {verification_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]



    )