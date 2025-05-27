from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .cosine import update_cosine
from .forms import JobSeekerRegistrationForm, JobSeekerLoginForm,JobProviderRegistrationForm,JobProviderLoginForm
from django.contrib.auth import authenticate, login
from .models import Job, JobSeekerRegister, UserProfile

from .forms import JobPostForm
from django.contrib import messages
from .authentication import send_verification_email

from django.contrib.auth.decorators import login_required


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
    if job_id:
       
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            messages.error(request, "Job description not found.")
            return redirect('jobprovider_dashboard')

        data = JobSeekerRegister.objects.filter(job_description=job).order_by('-cosine_similarity_score')
       
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

    # Check if the user has already applied for the job
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
