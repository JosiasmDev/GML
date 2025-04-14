from django.db import models
from django.utils import timezone

class JobOffer(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    company = models.CharField(max_length=200, verbose_name="Empresa")
    url = models.URLField(verbose_name="URL de la oferta")
    description = models.TextField(blank=True, verbose_name="Descripción")
    salary = models.CharField(max_length=100, blank=True, verbose_name="Salario")
    location = models.CharField(max_length=100, verbose_name="Ubicación")
    source = models.CharField(max_length=50, verbose_name="Fuente")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    published_date = models.CharField(max_length=50, blank=True, verbose_name="Fecha de publicación")
    is_favorite = models.BooleanField(default=False, verbose_name="Favorito")
    search_keywords = models.CharField(max_length=200, verbose_name="Palabras clave de búsqueda")
    search_location = models.CharField(max_length=100, verbose_name="Ubicación de búsqueda")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Oferta de trabajo"
        verbose_name_plural = "Ofertas de trabajo"

    def __str__(self):
        return f"{self.title} - {self.company}"

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
