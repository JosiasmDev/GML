from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import JobOffer, SearchHistory
from .scrapers import InfoJobsScraper
import json

def dashboard(request):
    jobs = JobOffer.objects.all().order_by('-created_at')
    search_history = SearchHistory.objects.all().order_by('-created_at')[:5]
    
    # Añadir log para verificar el número de ofertas
    print(f"Total de ofertas en la base de datos: {jobs.count()}")
    
    # Paginación - aumentar a 20 ofertas por página
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'jobs': page_obj,
        'search_history': search_history,
        'total_jobs': jobs.count(),
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
