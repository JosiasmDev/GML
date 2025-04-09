from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('filter/', views.filter_jobs, name='filter_jobs'),
    path('delete-all/', views.delete_all_jobs, name='delete_all_jobs'),
] 