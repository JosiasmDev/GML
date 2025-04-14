from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import JobOffer, SearchHistory
from .scrapers import InfoJobsScraper
import json

def dashboard(request):
    # Obtener parámetros de filtrado y ordenación
    filter_by = request.GET.get('filter_by', '')
    filter_value = request.GET.get('filter_value', '')
    order_by = request.GET.get('order_by', '-created_at')
    
    # Obtener todas las ofertas de trabajo
    jobs = JobOffer.objects.all()
    
    # Aplicar filtros
    if filter_by and filter_value:
        if filter_by == 'salary':
            jobs = jobs.filter(salary__icontains=filter_value)
        elif filter_by == 'work_mode':
            jobs = jobs.filter(work_mode__icontains=filter_value)
        elif filter_by == 'min_experience':
            jobs = jobs.filter(min_experience__icontains=filter_value)
        elif filter_by == 'contract_type':
            jobs = jobs.filter(contract_type__icontains=filter_value)
        elif filter_by == 'title':
            jobs = jobs.filter(title__icontains=filter_value)
        elif filter_by == 'company':
            jobs = jobs.filter(company__icontains=filter_value)
        elif filter_by == 'location':
            jobs = jobs.filter(location__icontains=filter_value)
        elif filter_by == 'studies':
            jobs = jobs.filter(studies__icontains=filter_value)
        elif filter_by == 'languages':
            jobs = jobs.filter(languages__icontains=filter_value)
        elif filter_by == 'required_skills':
            jobs = jobs.filter(required_skills__icontains=filter_value)
    
    # Aplicar ordenación
    jobs = jobs.order_by(order_by)
    
    # Paginar los resultados
    paginator = Paginator(jobs, 20)  # Mostrar 20 ofertas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener el total de ofertas
    total_jobs = jobs.count()
    
    # Obtener valores únicos para los filtros
    unique_values = {
        'work_mode': JobOffer.objects.values_list('work_mode', flat=True).distinct(),
        'contract_type': JobOffer.objects.values_list('contract_type', flat=True).distinct(),
        'min_experience': JobOffer.objects.values_list('min_experience', flat=True).distinct(),
        'studies': JobOffer.objects.values_list('studies', flat=True).distinct(),
        'languages': JobOffer.objects.values_list('languages', flat=True).distinct(),
    }
    
    context = {
        'jobs': page_obj,
        'total_jobs': total_jobs,
        'filter_by': filter_by,
        'filter_value': filter_value,
        'order_by': order_by,
        'unique_values': unique_values,
    }
    
    return render(request, 'jobs/dashboard.html', context)

def job_detail(request, job_id):
    job = get_object_or_404(JobOffer, id=job_id)
    context = {
        'job': job
    }
    return render(request, 'jobs/job_detail.html', context)

def under_construction(request, portal_name):
    context = {
        'portal_name': portal_name
    }
    return render(request, 'jobs/under_construction.html', context)

def delete_all_jobs(request):
    if request.method == 'POST':
        try:
            # Borrar todas las ofertas de trabajo
            count = JobOffer.objects.count()
            JobOffer.objects.all().delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Se han borrado {count} ofertas de trabajo correctamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al borrar las ofertas: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@csrf_exempt
def search_jobs(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            keywords = data.get('keywords', '')
            location = data.get('location', '0')
            
            if not keywords:
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor, introduce algunas palabras clave para buscar'
                })
            
            scraper = InfoJobsScraper()
            result = scraper.search_jobs(keywords, location)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': f'Se encontraron {result["count"]} ofertas',
                    'search_id': result['search_id']
                })
            else:
                error_message = result.get('error', 'Error desconocido en la búsqueda')
                if 'captcha' in error_message.lower():
                    error_message = 'Lo sentimos, el servicio está temporalmente no disponible. Por favor, inténtalo de nuevo más tarde.'
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Error en el formato de los datos'
            })
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@csrf_exempt
def toggle_favorite(request, job_id):
    try:
        job = JobOffer.objects.get(id=job_id)
        job.is_favorite = not job.is_favorite
        job.save()
        return JsonResponse({
            'success': True,
            'is_favorite': job.is_favorite
        })
    except JobOffer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Oferta no encontrada'
        })

@csrf_exempt
def delete_job(request, job_id):
    try:
        job = JobOffer.objects.get(id=job_id)
        job.delete()
        return JsonResponse({
            'success': True,
            'message': 'Oferta eliminada correctamente'
        })
    except JobOffer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Oferta no encontrada'
        })
