"""
URL configuration for gml_project project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),  # Incluir las URLs de la aplicación jobs
] 