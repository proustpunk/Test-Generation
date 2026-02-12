from django import views
from django.urls import path
from .views import trigger_final_email,update_resume,log_activity,candidates_for_job,test_submitted,test_validation,submit_test,start_test,send_email_to_seekers,TopJob,apply_job, job_details, ranking,homepage,loginmain,registermain,jobseeker_register,jobseeker_login,jobprovider_register,PostJob,joblist,jobprovider_login, verify_email

urlpatterns =[

    path('',TopJob,name="homepage"),
    path('loginmain/',loginmain,name="loginmain"),
    path('registermain/',registermain, name="register"),
    path('jobseeker_register/',jobseeker_register,name="jobseeker_register"),
    path('jobseeker_login/',jobseeker_login,name="jobseeker_login"),
    path('jobprovider_register/',jobprovider_register,name="jobprovider_register"),
    path('jobprovider_login',jobprovider_login,name="jobprovider_login"),

    path('jobprovider_dashboard/',PostJob,name="jobprovider_dashboard"),
    path('joblist/',joblist,name="joblist"),
    path('ranking/<int:job_id>/',ranking,name="ranking"),
    path('jobdetails/<int:job_id>/',job_details,name="jobdetails"),

    path('apply/<int:job_id>/',apply_job,name="apply"),

    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),

    path('send-emails/<int:job_id>/',send_email_to_seekers,name='send_email_to_seekers'),
    path('update-resume/', update_resume, name='update_resume'),

    path('start-test/<uidb64>/<token>/<int:job_id>/', start_test, name='start-test'),
    path('submit-test/', submit_test, name='submit_test'),
    path('test-validation/<uidb64>/<token>/<int:job_id>/', test_validation, name='test-validation'),
    path('test-submitted/<int:job_id>/', test_submitted, name='test_submitted'),

    path('candidates/<int:job_id>/', candidates_for_job, name='candidates_for_job'),
    path('log-activity/',log_activity,name="log_activity"),

    path(
    "jobs/<int:job_id>/trigger-final-email/",
    trigger_final_email,
    name="trigger_final_email"
),




]