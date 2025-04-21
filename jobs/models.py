from django.db import models
from django.utils import timezone

class JobOffer(models.Model):
    """Modelo para almacenar ofertas de trabajo"""
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    salary = models.CharField(max_length=255, blank=True)
    work_mode = models.CharField(max_length=100, blank=True)
    min_experience = models.CharField(max_length=255, blank=True)
    contract_type = models.CharField(max_length=255, blank=True)
    studies = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=255, blank=True)
    required_skills = models.TextField(blank=True)
    description = models.TextField(blank=True)
    publication_date = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_history = models.ForeignKey('SearchHistory', on_delete=models.CASCADE, related_name='job_offers', null=True, blank=True)
    vacantes = models.CharField(max_length=50, blank=True, verbose_name="Número de vacantes")
    inscritos = models.CharField(max_length=50, blank=True, verbose_name="Número de inscritos")
    is_favorite = models.BooleanField(default=False, verbose_name="Oferta favorita")
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.company} - {self.location}"

class SearchHistory(models.Model):
    keywords = models.CharField(max_length=200, verbose_name="Palabras clave")
    location = models.CharField(max_length=100, verbose_name="Ubicación")
    source = models.CharField(max_length=50, verbose_name="Fuente")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de búsqueda")
    results_count = models.IntegerField(default=0, verbose_name="Número de resultados")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Historial de búsqueda"
        verbose_name_plural = "Historial de búsquedas"

    def __str__(self):
        return f"{self.keywords} en {self.location} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
