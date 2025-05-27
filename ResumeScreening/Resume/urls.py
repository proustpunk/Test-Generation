from django.urls import path
from .views import TopJob,apply_job, job_details, ranking,homepage,loginmain,registermain,jobseeker_register,jobseeker_login,jobprovider_register,PostJob,joblist,jobprovider_login, verify_email

urlpatterns =[

    path('',TopJob,name="homepage"),
    path('loginmain/',loginmain,name="loginmain"),
    path('registermain/',registermain, name="register"),
    path('jobseeker_register/',jobseeker_register,name="jobseeker_register"),
    path('jobseeker_login/',jobseeker_login,name="jobseeker_login"),
    path('jobprovider_register/',jobprovider_register,name="jobprovider_register"),
    #####################jobproviderregisterbigrekoxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa#####################################
    path('jobprovider_login',jobprovider_login,name="jobprovider_login"),

    path('jobprovider_dashboard/',PostJob,name="jobprovider_dashboard"),
    path('joblist/',joblist,name="joblist"),
    path('ranking/<int:job_id>/',ranking,name="ranking"),
    path('jobdetails/<int:job_id>/',job_details,name="jobdetails"),

    path('apply/<int:job_id>/',apply_job,name="apply"),

    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),

]