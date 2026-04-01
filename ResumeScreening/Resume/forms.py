from django import forms
from django.contrib.auth.models import User
from .models import JobSeekerRegister,JobProviderRegister,Job
from django.contrib.auth.forms import AuthenticationForm
from .validatee import validate_password

from django.core.validators import validate_email
from django.core.exceptions import ValidationError


CATEGORY_CHOICES = [
        ('data scientist', 'Data Science'),
        ('software developer', 'Software Developer'),
        ('cybersecurity specialist', 'Cybersecurity Specialist'),
        ('devops engineer', 'Devops engineer'),
        ('graphics engineer', 'Graphics engineer'),
        ('machine learning engineer', 'Machine Learning Engineer'),
        ('robotics engineer', 'Robotics Engineer'),
    ]
class JobSeekerRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        help_text="Password must be at least 8 characters long, include uppercase and lowercase letters, a number, and a special character (!@#$%^&*)."
    )
    email = forms.EmailField(required=True)
    resume = forms.FileField(required=True)
    class Meta:
        model = JobSeekerRegister
        fields = ['resume', 'skills', 'bio', 'processed_text', 'vector', 'prediction','profile_pics']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password) 
        return password
    
    def clean_email(self):
        email = self.cleaned_data.get('email') #.get to remove keyerror i.e. shows -> email is incorrect instead of crashing
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Invalid email format.")
        return email
    
    def clean_username(self):
       
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],


            is_active=False
        )
        job_seeker = JobSeekerRegister(
            user=user,
            resume=self.cleaned_data['resume'],
            skills=self.cleaned_data['skills'],
            bio=self.cleaned_data['bio'],
            profile_pics=self.cleaned_data.get('profile_pics')

        )
        if commit:
            user.save()
            job_seeker.save()
        return user, job_seeker



class JobSeekerLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'password']


class JobProviderLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'password']


class JobProviderRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True,        help_text="Password must be at least 8 characters long, include uppercase and lowercase letters, a number, and a special character (!@#$%^&*)."
)

    class Meta:
        model = JobProviderRegister
        fields = ['company_name', 'company_description', 'bio']
    def clean_username(self):
       
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username
    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password) 
        return password

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
           
        )
        job_provider = JobProviderRegister(
            user=user,
            company_name=self.cleaned_data['company_name'],
            company_description=self.cleaned_data['company_description'],
            bio=self.cleaned_data['bio']
        )
        if commit:
            user.save()
            job_provider.save()
        return user,job_provider
    
 

class JobPostForm(forms.ModelForm):
  
    class Meta:
        model = Job
        fields = ['deadline','job_title', 'job_requirements', 'salary_range', 'job_location','job_description_file','processed_description','description_vector']

    job_title = forms.ChoiceField(choices=CATEGORY_CHOICES,widget=forms.Select(attrs={"class": "form-control"}))
    job_requirements = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'List the required qualifications', 'rows': 5}))
    salary_range = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter salary range'}))
    company_logo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))
    job_location = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter job location'}))
    job_description_file = forms.FileField()
        
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }
        )
    )

