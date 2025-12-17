from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
import os
from .cosine import cosine_similarity,update_cosine
from .forms import JobSeekerRegistrationForm, JobSeekerLoginForm,JobProviderRegistrationForm,JobProviderLoginForm
from django.contrib.auth import authenticate, login
from .models import CandidateLog,Answer, Job, JobSeekerRegister, UserProfile,Question

from .forms import JobPostForm
from django.contrib import messages
from .authentication import send_verification_email

from django.contrib.auth.decorators import login_required
from .embeddings import embed_text

from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from .utils import stuffing_check, clean_text, is_ai_written_resume


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json





def TopJob(request):
    top_jobs = Job.objects.order_by('-application_count')[:3]
    top_jobs_date = Job.objects.order_by('-posted_at')[:3]
    return render(request,'homepage.html',{'top_jobs': top_jobs, 'top_jobs_date': top_jobs_date})



def jobseeker_login(request):
    if request.method == 'POST':
        form = JobSeekerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user type 
                return redirect('joblist')
            else:
                return HttpResponse("Invalid credentials, please try again.")
        else:
            return HttpResponse("Invalid form submission.")
    else:
        form = JobSeekerLoginForm()
    return render(request, 'jobseeker_login.html', {'form': form})


def jobprovider_login(request):
    if request.method == 'POST':
        form = JobProviderLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('jobprovider_dashboard')
                else:
                    return HttpResponse("Please verify your email before logging in.")
            
            else:
                return HttpResponse("Invalid credentials, please try again.")
        else:
            return HttpResponse("Invalid form submission.")
    else:
        form = JobSeekerLoginForm()
    return render(request, 'jobprovider_login.html', {'form': form})

def homepage(request):
    return render(request, 'homepage.html')



def loginmain(request):
    return render(request, 'loginmain.html')


def registermain(request):
    return render(request, 'registermain.html')


def jobseeker_register(request):
    if request.method == 'POST':
        form = JobSeekerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user,job_seeker = form.save()
            send_verification_email(request,user)
            return redirect('loginmain') 
            
        else:
                        print("Form errors:", form.errors)  # Log form errors for debugging

    else:
        form = JobSeekerRegistrationForm()
    return render(request, 'jobseeker_register.html', {'form': form})



def jobprovider_register(request):
    if request.method == 'POST':
        form = JobProviderRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            
            return redirect('loginmain')  # Redirect to the login page after registration
    else:
        form = JobProviderRegistrationForm()
    return render(request, 'jobprovider_register.html', {'form': form})


@login_required
def PostJob(request): #dashboard
   


    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile.is_provider:
            return redirect('loginmain') 
    except UserProfile.DoesNotExist:
        return redirect('registermain') 

    if request.method == 'POST':
        form = JobPostForm(request.POST, request.FILES)
        if form.is_valid():
            job_post = form.save(commit=False)

            job_post.user = request.user
            job_post.save() 
            return redirect('jobprovider_dashboard')  
    else:
        form = JobPostForm()  


 
    posted_jobs = request.user.job_post.all()
    return render(request, 'jobprovider_dashboard.html', {'form': form, 'posted_jobs':posted_jobs})

@login_required
def joblist(request): #dashboard

    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.is_provider:
            return redirect(loginmain)

    except user_profile.DoesNotExist:
            return redirect(loginmain)

    
    jobs = Job.objects.all()
    return render(request, 'joblist.html', {'jobs': jobs})




@login_required
def ranking(request, job_id):
    print('ranking')
    if job_id:
       
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            messages.error(request, "Job description not found.")
            return redirect('jobprovider_dashboard')

        data = JobSeekerRegister.objects.filter(job_description=job).order_by('-cosine_similarity_score')
        
        for single_data in data:
            resume_file = single_data.resume

            if resume_file and os.path.exists(resume_file.path):
                with open(resume_file.path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                    cleaned_text = clean_text(text)
                    single_data.is_suspicious = stuffing_check(cleaned_text)
                    single_data.is_suspicious_ai = is_ai_written_resume(cleaned_text)
            else:
                single_data.is_suspicious = False 
        return render(request, 'ranking.html', {'data': data, 'job': job})
    else:
        messages.error(request, "No job description selected.")
        return redirect('joblist') 
    


def job_details(request, job_id):
   
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobdetails.html', {'job': job})


def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.is_provider: 
            messages.error(request, "Only job seekers can apply.")
            return redirect('joblist') 

    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('loginmain')

    has_applied = JobSeekerRegister.objects.filter(job_description=job, user=request.user).exists()

   
    print(has_applied)
    if request.method == 'POST' and has_applied==False:  # User confirmed application
        job_seeker_register = JobSeekerRegister.objects.get(user=request.user)

        job_seeker_register.job_description = job
        job.application_count += 1
        job.save()
        job_seeker_register.save()
        
        messages.success(request, f"Successfully applied for {job.job_title}.")
        update_cosine(job.id)
        return redirect('jobdetails', job_id=job.id)

    # Render confirmation page for GET request
    return render(request, 'jobdetails.html', {'job': job, 'has_applied':has_applied})


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponse

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None

    
    if user is not None and default_token_generator.check_token(user, token):
        
        user.is_active = True  
        
        user.save()

       
        return redirect('loginmain')
    else:
        return HttpResponse("Invalid verification link.")



def send_email_to_seekers(request, job_id):

   #pass in email, name everything of the user

    job = get_object_or_404(Job, id=job_id)

    seekers = JobSeekerRegister.objects.filter (job_description=job)

   

    if not seekers.exists():
        messages.warning(request, "No seekers have applied for this job yet.")
        return redirect('ranking', job_id=job_id)
    
    for seeker in seekers:

        seeker_email = seeker.user.email

        uid = urlsafe_base64_encode(force_bytes(seeker.user.pk))
        token = default_token_generator.make_token(seeker.user)

        current_site = get_current_site(request)
        domain = current_site.domain
        test_link = f"http://{domain}/test-validation/{uid}/{token}/{job.id}"
        send_mail(

            subject=f"Test Invitation for {job.job_title}",
            message=f"Dear {seeker.user.username},\n\nYou have been invited to take a test for the job: {job.job_title}.\n\nBest regards,\n{request.user.username}.{test_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[seeker.user.email]
        )

    messages.success(request,f"Emails Sent!")
    return redirect('ranking', job_id=job_id)


##############################################
from io import BytesIO
from PIL import Image
import dlib
import numpy as np
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.contrib import messages
from base64 import b64decode
from .models import Job, JobSeekerRegister

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('Resume/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('Resume/dlib_face_recognition_resnet_model_v1.dat')
def get_face_descriptor(image_pil):
    try:
        print("DEBUG: Converting to RGB")
        image_pil = image_pil.convert('RGB')
        
        print("DEBUG: Resizing image to 640x480")
        image_pil = image_pil.resize((640, 480))  # Resize to improve detection
        
        image_np = np.array(image_pil)
        print("DEBUG: Image converted to numpy array")

        dets = detector(image_np, 1)
        print(f"DEBUG: Faces detected: {len(dets)}")

        if len(dets) == 0:
            print("WARNING: No face detected")
            return None

        shape = sp(image_np, dets[0])
        face_descriptor = facerec.compute_face_descriptor(image_np, shape)
        print("DEBUG: Face descriptor generated")
        return np.array(face_descriptor)

    except Exception as e:
        print(f"ERROR in get_face_descriptor: {e}")
        return None

def test_validation(request, uidb64, token, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        messages.error(request, "Job description not found.")
        return redirect('jobprovider_dashboard')

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        print (user)
    except Exception:
        return JsonResponse({'match': False, 'error': 'Invalid user link.'}) if request.method == 'POST' else HttpResponseBadRequest("Invalid link.")

    try:
        target_photo_record = JobSeekerRegister.objects.get(user=user, job_description=job)
    except JobSeekerRegister.DoesNotExist:
        return JsonResponse({'match': False, 'error': 'No uploaded photo found for this user and job.'}) if request.method == 'POST' else render(request, 'test_validation.html', {'target_photo': None})
    print("this")
    if request.method == 'POST':
        print('posted')
        data = json.loads(request.body)
        img_data_url = data.get('image')
        if not img_data_url:
            return HttpResponseBadRequest('No image data provided.')
            
            
        
        try:
            header, encoded = img_data_url.split(',', 1)
            img_bytes = BytesIO(b64decode(encoded))
            img = Image.open(img_bytes)

            snapshot_descriptor = get_face_descriptor(img)
            if snapshot_descriptor is None:
                return JsonResponse({'match': False, 'error': 'No face detected in snapshot'})

            print("thisn")
            
            target_img = Image.open(target_photo_record.profile_pics.path)

            print("called")
            target_descriptor = get_face_descriptor(target_img)
            if target_descriptor is None:
                return JsonResponse({'match': False, 'error': 'No face detected in uploaded photo'})

            dist = np.linalg.norm(snapshot_descriptor - target_descriptor)
            print(dist)
            threshold = 0.6
            is_match = bool(dist < threshold)

            print(dist)

            return JsonResponse({'match': is_match, 'distance': dist})

        except Exception as e:
            return JsonResponse({'match': False, 'error': str(e)})

    else:
       return render(request, 'test_validation.html', {
        'target_photo': target_photo_record,
        'uidb64':       uidb64,
        'token':        token,
        'job':          job,
    })


def start_test(request, uidb64, token, job_id):
    try:
       uid = urlsafe_base64_decode(uidb64).decode()
       user = get_user_model().objects.get(pk=uid) 
    except Exception:
        return HttpResponse("Invalid or corrupted link.")

    except Exception:
        return HttpResponse("Invalid or corrupted link.")   
    

    job = get_object_or_404(Job, id=job_id)

    candidate = Candidate.objects.create(user=user, job=job)
    candidate_id = candidate.id

   #category=job.job_title
    questions_subjective = Question.objects.filter(category=job.job_title, question_type='subjective', difficulty='intermediate').order_by('?')[:5]
    questions_objective = Question.objects.filter(category=job.job_title,question_type='objective', difficulty='intermediate').order_by('?')[:8]
    questions_mcq = Question.objects.filter(category=job.job_title, question_type='mcq', difficulty='intermediate').order_by('?')[:8]

    questions_code = Question.objects.filter(category=job.job_title, question_type='code', difficulty='intermediate').order_by('?')[:4]


    questions = list(questions_subjective) + list(questions_objective) + list(questions_mcq) + list(questions_code)

    return render(request, 'test_page.html', {
        'job': job,
        'user': user,
        'questions': questions,
        'uidb64': uidb64,
        'token': token,        
        'candidate_id': candidate_id,
    })

import subprocess, uuid, os, json, tempfile
from .models import Candidate
from django.contrib.auth.models import User


def submit_test(request):

    #decode the email id everyting and send it to variable as context to the url of the provider page and show it in container in well managed way with suspicitious activity log
    if request.method == "POST":

        uidb64 = request.POST.get("uidb64")
        job_id = request.POST.get("job_id")

        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        job = Job.objects.get(id=job_id)

        cid = request.POST.get("candidate_id")
        candidate = Candidate.objects.get(id=cid)

      
        if candidate.total_score is None:
            candidate.total_score = 0


        total_score = 0
        for key,value in request.POST.items():
            if key.startswith('q'):
                qid = key[1:]

                try:
                    question = Question.objects.get(id=qid)

                    answer = Answer.objects.create(
                        user=user,
                        question=question,
                        selected_option=value if question.question_type in ['mcq', 'objective'] else None,
                        written_answer=value if question.question_type in ['subjective', 'code'] else None,
                        score = 0 #else throws error adding to None
                    )

                    
                    if question.question_type in ['mcq', 'objective']:
                        if question.correct_answer and value:
                            if value.strip().upper() == question.correct_answer.strip().upper():
                             answer.score += 1  
                            else:
                             answer.score += 0  
                    
                    answer.save()

                    if question.question_type == "subjective":
                        ref_emb = question.reference_vector
                        ans_emb = embed_text(answer.written_answer)
                        similarity = cosine_similarity(ref_emb,ans_emb)
                        answer.score += round(similarity*10,2) 
                        answer.save()


                    elif question.question_type=="code":
                        test_cases = question.test_cases or []
                        all_passed = True


                        filename = f"{uuid.uuid4().hex}.py"
                        filepath = os.path.abspath(filename)

                        with open(filepath, "w") as f:
                            f.write(value)

                        
                        for case in test_cases:
                            input_data = case.get("input", "") + "\n"
                            expected_output = case.get("expected_output", "")

                            try:
                                result = subprocess.run([
                                    "docker", "run", "--rm",
                                    "-v", f"{filepath}:/app/code.py",
                                    "python:3.9", "python", "/app/code.py"
                                ],
                                input=input_data,
                                capture_output=True,
                                text=True,
                                timeout=5
                                )

                                output = result.stdout.strip()

                                if output != str(expected_output):
                                    all_passed = False
                                    break

                            except subprocess.TimeoutExpired:
                                all_passed=False
                                break

                        if os.path.exists(filepath):
                             os.remove(filepath)

                        # Scoring
                        if all_passed:
                            answer.score = 10
                        else:
                            answer.score = 0
                        answer.save()

                    candidate.answers.add(answer)
                    total_score += answer.score


                            
                except Question.DoesNotExist:
                    continue

        candidate.total_score = total_score
        candidate.save()

        return redirect('test_submitted', job_id=job.id)

    return HttpResponse("Invalid access.")


def test_submitted(request,job_id):
    job = Job.objects.get(id=job_id)
    return render(request,'test_submitted.html',{'job': job})



def candidates_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    candidates = Candidate.objects.filter(job=job)
    return render(request, 'candidates_for_job.html', {'job': job, 'candidates': candidates})


@csrf_exempt
def log_activity(request):

    data = json.loads(request.body)
    cid = data.get("candidate_id")
    flags = data.get("flags")
    suspicious = data.get("suspicious")

    candidate = Candidate.objects.get(id=cid)

    CandidateLog.objects.create(
        candidate = candidate,
        flags = flags,
        suspicious = suspicious
    )


    return JsonResponse({"status": "ok"})