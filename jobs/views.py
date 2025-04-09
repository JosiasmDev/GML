from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import JobOffer
from infojobs_scraper import InfojobsScraper


def index(request):
    """Vista principal que muestra las ofertas de trabajo"""
    job_offers = JobOffer.objects.all()
    
    # Obtener valores únicos para los filtros
    cities = JobOffer.objects.values_list('city', flat=True).distinct()
    companies = JobOffer.objects.values_list('company', flat=True).distinct()
    contract_types = JobOffer.objects.values_list('contract_type', flat=True).distinct()
    industries = JobOffer.objects.values_list('industry', flat=True).distinct()
    categories = JobOffer.objects.values_list('category', flat=True).distinct()
    levels = JobOffer.objects.values_list('level', flat=True).distinct()
    work_modes = JobOffer.objects.values_list('work_mode', flat=True).distinct()
    educations = JobOffer.objects.values_list('min_education', flat=True).distinct()
    
    context = {
        'job_offers': job_offers,
        'cities': cities,
        'companies': companies,
        'contract_types': contract_types,
        'industries': industries,
        'categories': categories,
        'levels': levels,
        'work_modes': work_modes,
        'educations': educations,
    }
    
    return render(request, 'jobs/index.html', context)


def search(request):
    """Buscar ofertas de trabajo con palabras clave"""
    if request.method == 'POST':
        keywords = request.POST.get('keywords', '')
        if not keywords:
            messages.error(request, 'Por favor, introduce palabras clave para buscar')
            return redirect('jobs:index')
        
        # Iniciar el scraper
        scraper = InfojobsScraper(headless=False)
        jobs_saved = scraper.scrape_jobs(keywords)
        
        if jobs_saved > 0:
            messages.success(request, f'Se encontraron y guardaron {jobs_saved} ofertas de trabajo')
        else:
            messages.error(request, 'No se encontraron ofertas de trabajo o hubo un error durante el escaneo')
        
        return redirect('jobs:index')
    
    return redirect('jobs:index')


def delete_all_jobs(request):
    """Eliminar todas las ofertas de trabajo de la base de datos"""
    if request.method == 'POST':
        try:
            # Obtener el número de ofertas antes de eliminarlas
            count = JobOffer.objects.count()
            
            # Eliminar todas las ofertas
            JobOffer.objects.all().delete()
            
            messages.success(request, f'Se eliminaron {count} ofertas de trabajo de la base de datos')
        except Exception as e:
            messages.error(request, f'Error al eliminar las ofertas: {str(e)}')
    
    return redirect('jobs:index')


def job_detail(request, job_id):
    """Mostrar detalles de una oferta de trabajo específica"""
    job = get_object_or_404(JobOffer, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})


def filter_jobs(request):
    """Filtrar ofertas de trabajo por diferentes criterios"""
    # Obtener parámetros de filtrado
    city = request.GET.get('city', '')
    company = request.GET.get('company', '')
    contract_type = request.GET.get('contract_type', '')
    industry = request.GET.get('industry', '')
    category = request.GET.get('category', '')
    level = request.GET.get('level', '')
    work_mode = request.GET.get('work_mode', '')
    min_education = request.GET.get('min_education', '')
    
    # Construir la consulta base
    query = JobOffer.objects.all()
    
    # Aplicar filtros si se proporcionan
    if city:
        query = query.filter(city__icontains=city)
    if company:
        query = query.filter(company__icontains=company)
    if contract_type:
        query = query.filter(contract_type__icontains=contract_type)
    if industry:
        query = query.filter(industry__icontains=industry)
    if category:
        query = query.filter(category__icontains=category)
    if level:
        query = query.filter(level__icontains=level)
    if work_mode:
        query = query.filter(work_mode__icontains=work_mode)
    if min_education:
        query = query.filter(min_education__icontains=min_education)
    
    # Obtener valores únicos para los filtros
    cities = JobOffer.objects.values_list('city', flat=True).distinct()
    companies = JobOffer.objects.values_list('company', flat=True).distinct()
    contract_types = JobOffer.objects.values_list('contract_type', flat=True).distinct()
    industries = JobOffer.objects.values_list('industry', flat=True).distinct()
    categories = JobOffer.objects.values_list('category', flat=True).distinct()
    levels = JobOffer.objects.values_list('level', flat=True).distinct()
    work_modes = JobOffer.objects.values_list('work_mode', flat=True).distinct()
    educations = JobOffer.objects.values_list('min_education', flat=True).distinct()
    
    context = {
        'job_offers': query,
        'cities': cities,
        'companies': companies,
        'contract_types': contract_types,
        'industries': industries,
        'categories': categories,
        'levels': levels,
        'work_modes': work_modes,
        'educations': educations,
        'selected_city': city,
        'selected_company': company,
        'selected_contract_type': contract_type,
        'selected_industry': industry,
        'selected_category': category,
        'selected_level': level,
        'selected_work_mode': work_mode,
        'selected_education': min_education,
    }
    
    return render(request, 'jobs/index.html', context) 