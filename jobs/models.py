from django.db import models


class JobOffer(models.Model):
    """Modelo para almacenar ofertas de trabajo de Infojobs"""
    
    position = models.CharField(max_length=200, verbose_name="Puesto")
    company = models.CharField(max_length=200, verbose_name="Empresa")
    company_valuation = models.FloatField(null=True, blank=True, verbose_name="Valoración empresa")
    city = models.CharField(max_length=200, verbose_name="Ciudad")
    country = models.CharField(max_length=200, default="España", verbose_name="País")
    work_mode = models.CharField(max_length=200, default="N/A", verbose_name="Modalidad de trabajo")
    contract_type = models.CharField(max_length=200, verbose_name="Tipo de contrato")
    salary = models.CharField(max_length=200, verbose_name="Salario")
    min_exp = models.CharField(max_length=200, verbose_name="Experiencia mínima")
    min_education = models.CharField(max_length=200, default="N/A", verbose_name="Estudios mínimos")
    description = models.TextField(blank=True, verbose_name="Descripción")
    requirements = models.TextField(blank=True, verbose_name="Requisitos")
    functions = models.TextField(blank=True, verbose_name="Funciones")
    conditions = models.TextField(blank=True, verbose_name="Condiciones")
    industry = models.CharField(max_length=200, default="N/A", verbose_name="Tipo de industria")
    category = models.CharField(max_length=200, default="N/A", verbose_name="Categoría")
    level = models.CharField(max_length=200, default="N/A", verbose_name="Nivel")
    vacancies = models.IntegerField(default=1, verbose_name="Número de vacantes")
    applicants = models.IntegerField(default=0, verbose_name="Número de inscritos")
    benefits = models.TextField(blank=True, verbose_name="Beneficios sociales")
    url = models.CharField(max_length=200, unique=True, verbose_name="URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Oferta de trabajo"
        verbose_name_plural = "Ofertas de trabajo"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.position} en {self.company}" 