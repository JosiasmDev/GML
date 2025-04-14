from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('search/', views.search_jobs, name='search_jobs'),
    path('delete-all/', views.delete_all_jobs, name='delete_all_jobs'),
    path('job/<int:job_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('portal/<str:portal_name>/', views.under_construction, name='under_construction'),
] 