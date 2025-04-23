from linkedin_api import Linkedin
import logging
import os
import time
import random
from datetime import datetime
from django.conf import settings
from .models import JobOffer, SearchHistory
from django.utils import timezone
from dotenv import load_dotenv
import re
from urllib.parse import quote

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class LinkedInScraper:
    def __init__(self):
        """Inicializa el scraper de LinkedIn"""
        self.base_url = "https://www.linkedin.com"
        self.logger = logging.getLogger(__name__)
        
        # Credenciales
        self.email = "josisapp@gmail.com"
        self.password = "DIcampus1!"
        
        # Inicializar la API de LinkedIn
        try:
            self.api = Linkedin(self.email, self.password)
            logger.info("✅ API de LinkedIn inicializada correctamente")
        except Exception as e:
            logger.error(f"❌ Error al inicializar la API de LinkedIn: {str(e)}")
            raise
    
    def search_jobs(self, keywords, location="Spain", limit=5):
        """
        Busca ofertas de trabajo en LinkedIn usando la API
        """
        try:
            logger.info(f"🔍 Iniciando búsqueda en LinkedIn")
            logger.info(f"📝 Palabras clave: {keywords}")
            logger.info(f"📍 Ubicación: {location}")
            logger.info(f"📊 Límite de resultados: {limit}")
            
            # Realizar la búsqueda con la API
            logger.info("🔍 Realizando búsqueda con la API...")
            search_results = self.api.search_jobs(
                keywords=keywords,
                location_name=location,  # Usar la ubicación directamente
                limit=limit
            )
            
            # Asegurarnos de que solo procesamos el número de ofertas especificado
            search_results = search_results[:limit]
            
            logger.info(f"✅ Búsqueda completada. Se encontraron {len(search_results)} ofertas")
            
            # Crear un historial de búsqueda
            search_history = SearchHistory.objects.create(
                keywords=keywords,
                location=location,
                source='LinkedIn',
                results_count=len(search_results)
            )
            
            # Listas para almacenar las ofertas
            jobs_to_create = []
            jobs_to_update = []
            
            for i, result in enumerate(search_results, 1):
                try:
                    logger.info(f"\n📋 Procesando oferta {i}/{limit}")
                    
                    # Obtener el ID de la oferta
                    job_id = result.get('jobPosting', {}).get('id') or result.get('dashEntityUrn', '').split(':')[-1] or result.get('entityUrn', '').split(':')[-1]
                    
                    if not job_id:
                        logger.warning("No se pudo obtener el ID de la oferta")
                        continue
                    
                    logger.info(f"🔑 ID de la oferta: {job_id}")
                    
                    # Obtener detalles de la oferta con la API
                    job_details = self.api.get_job(job_id)
                    
                    # Imprimir los datos que devuelve la API
                    logger.info("📊 Datos devueltos por la API:")
                    logger.info(f"Título: {job_details.get('title', 'No disponible')}")
                    logger.info(f"Empresa (companyName): {job_details.get('companyName', 'No disponible')}")
                    logger.info(f"Empresa (company): {job_details.get('company', 'No disponible')}")
                    logger.info(f"Ubicación: {job_details.get('location', 'No disponible')}")
                    logger.info(f"Salario: {job_details.get('salary', 'No disponible')}")
                    logger.info(f"Modo de trabajo: {job_details.get('workplaceType', 'No disponible')}")
                    logger.info(f"Experiencia: {job_details.get('experienceLevel', 'No disponible')}")
                    logger.info(f"Tipo de contrato: {job_details.get('employmentType', 'No disponible')}")
                    logger.info(f"Estudios: {job_details.get('educationRequirements', 'No disponible')}")
                    logger.info(f"Idiomas: {job_details.get('languageRequirements', 'No disponible')}")
                    logger.info(f"Habilidades: {job_details.get('requiredSkills', 'No disponible')}")
                    logger.info(f"Fecha de publicación: {job_details.get('listedAt', 'No disponible')}")
                    logger.info("📋 Datos completos de la oferta:")
                    logger.info(job_details)
                    
                    # Extraer información básica
                    title = job_details.get('title', 'Título no especificado')
                    
                    # Extraer nombre de la empresa
                    company = "Empresa no especificada"
                    if 'companyDetails' in job_details:
                        company_details = job_details['companyDetails']
                        if 'com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany' in company_details:
                            company_info = company_details['com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany']
                            if 'companyResolutionResult' in company_info:
                                company = company_info['companyResolutionResult'].get('name', 'Empresa no especificada')
                    
                    # Extraer ubicación
                    job_location = job_details.get('formattedLocation', location)
                    
                    # Si la ubicación es un código numérico, buscar su nombre en el mapeo
                    if job_location and job_location.isdigit():
                        job_location = linkedin_location_mapping.get(job_location, location)
                    elif not job_location:
                        job_location = location
                    
                    # Extraer número de inscritos/solicitudes
                    inscritos = "No especificado"
                    if 'description' in job_details:
                        description = job_details['description'].get('text', '')
                        # Buscar patrones de número de solicitudes/inscritos
                        inscritos_patterns = [
                            r'(\d+)\s+personas?\s+han\s+hecho\s+clic\s+en\s+«Solicitar»',
                            r'(\d+)\s+solicitudes',
                            r'(\d+)\s+inscritos',
                            r'(\d+)\s+candidatos',
                            r'(\d+)\s+personas?\s+han\s+solicitado',
                            r'(\d+)\s+solicitantes'
                        ]
                        
                        for pattern in inscritos_patterns:
                            inscritos_match = re.search(pattern, description, re.IGNORECASE)
                            if inscritos_match:
                                inscritos = inscritos_match.group(1)
                                break
                    
                    url = f"https://www.linkedin.com/jobs/view/{job_id}"
                    
                    # Extraer salario
                    salary = "No especificado"
                    if 'description' in job_details:
                        description = job_details['description'].get('text', '')
                        # Buscar patrones de salario en la descripción
                        salary_patterns = [
                            r'Salario:?\s*entre\s*(\d+[.,]?\d*)\s*€\s*y\s*(\d+[.,]?\d*)\s*€\s*anuales',
                            r'Salario:?\s*(\d+[.,]?\d*)\s*€\s*anuales',
                            r'Salario:?\s*entre\s*(\d+[.,]?\d*)\s*y\s*(\d+[.,]?\d*)\s*€',
                            r'Salario:?\s*(\d+[.,]?\d*)\s*€'
                        ]
                        
                        for pattern in salary_patterns:
                            salary_match = re.search(pattern, description, re.IGNORECASE)
                            if salary_match:
                                if len(salary_match.groups()) == 2:
                                    salary = f"{salary_match.group(1)} - {salary_match.group(2)} € anuales"
                                else:
                                    salary = f"{salary_match.group(1)} € anuales"
                                break
                    
                    # Extraer modo de trabajo
                    work_mode = "No especificado"
                    if 'workplaceTypes' in job_details:
                        workplace_types = job_details['workplaceTypes']
                        if isinstance(workplace_types, list):
                            for workplace_type in workplace_types:
                                if workplace_type == 'urn:li:fs_workplaceType:1':
                                    work_mode = 'Presencial'
                                elif workplace_type == 'urn:li:fs_workplaceType:2':
                                    work_mode = 'Híbrido'
                                elif workplace_type == 'urn:li:fs_workplaceType:3':
                                    work_mode = 'Remoto'
                    
                    # Si no se encontró en workplaceTypes, buscar en la descripción
                    if work_mode == "No especificado" and 'description' in job_details:
                        description = job_details['description'].get('text', '')
                        if 'híbrido' in description.lower() or 'hibrido' in description.lower():
                            work_mode = 'Híbrido'
                        elif 'presencial' in description.lower():
                            work_mode = 'Presencial'
                        elif 'remoto' in description.lower() or 'teletrabajo' in description.lower():
                            work_mode = 'Remoto'
                    
                    # Extraer experiencia mínima
                    min_experience = "No especificado"
                    if 'description' in job_details:
                        description = job_details['description'].get('text', '')
                        # Buscar años de experiencia en la descripción
                        exp_patterns = [
                            r'(\d+)\s*años?\s*de\s*experiencia',
                            r'experiencia\s*de\s*(\d+)\s*años?',
                            r'experiencia\s*mínima\s*de\s*(\d+)\s*años?',
                            r'experiencia\s*en\s*desarrollo\s*de\s*(\d+)\s*años?'
                        ]
                        
                        for pattern in exp_patterns:
                            exp_match = re.search(pattern, description, re.IGNORECASE)
                            if exp_match:
                                min_experience = f"{exp_match.group(1)} años"
                                break
                    
                    # Extraer tipo de contrato
                    contract_type = "No especificado"
                    if 'description' in job_details:
                        description = job_details['description'].get('text', '')
                        # Buscar patrones de tipo de contrato en la descripción
                        contract_patterns = [
                            r'jornada\s+completa',
                            r'tiempo\s+completo',
                            r'full\s+time',
                            r'jornada\s+parcial',
                            r'tiempo\s+parcial',
                            r'part\s+time',
                            r'contrato\s+indefinido',
                            r'contrato\s+temporal',
                            r'contrato\s+por\s+obra'
                        ]
                        
                        for pattern in contract_patterns:
                            if re.search(pattern, description, re.IGNORECASE):
                                if 'completa' in pattern or 'completo' in pattern or 'full' in pattern:
                                    contract_type = 'Jornada completa'
                                elif 'parcial' in pattern or 'part' in pattern:
                                    contract_type = 'Jornada parcial'
                                elif 'indefinido' in pattern:
                                    contract_type = 'Contrato indefinido'
                                elif 'temporal' in pattern:
                                    contract_type = 'Contrato temporal'
                                elif 'obra' in pattern:
                                    contract_type = 'Contrato por obra'
                                break
                    
                    # Extraer estudios
                    studies = "No especificado"
                    if 'description' in job_details:
                        description = job_details['description'].get('text', '')
                        if 'titulación' in description.lower() or 'grado' in description.lower() or 'licenciatura' in description.lower():
                            studies = 'Titulación requerida'
                    
                    # Extraer idiomas
                    languages = "No especificado"
                    if 'description' in job_details:
                        description = job_details['description'].get('text', '')
                        if 'inglés' in description.lower():
                            languages = 'Inglés'
                    
                    # Extraer habilidades requeridas
                    required_skills = "No especificado"
                    if 'description' in job_details:
                        description = job_details['description'].get('text', '')
                        # Buscar habilidades en la descripción
                        skills = []
                        if 'php' in description.lower():
                            skills.append('PHP')
                        if 'python' in description.lower():
                            skills.append('Python')
                        if 'javascript' in description.lower():
                            skills.append('JavaScript')
                        if 'html' in description.lower():
                            skills.append('HTML')
                        if 'css' in description.lower():
                            skills.append('CSS')
                        if 'django' in description.lower():
                            skills.append('Django')
                        if 'laravel' in description.lower():
                            skills.append('Laravel')
                        if 'symfony' in description.lower():
                            skills.append('Symfony')
                        if 'react' in description.lower():
                            skills.append('React')
                        if 'angular' in description.lower():
                            skills.append('Angular')
                        if 'vue' in description.lower():
                            skills.append('Vue.js')
                        if 'docker' in description.lower():
                            skills.append('Docker')
                        if 'aws' in description.lower():
                            skills.append('AWS')
                        if 'git' in description.lower():
                            skills.append('Git')
                        if skills:
                            required_skills = ', '.join(skills)
                    
                    # Extraer fecha de publicación
                    publication_date = "No especificado"
                    if 'listedAt' in job_details:
                        publication_date = self._parse_date(job_details['listedAt'])
                    
                    logger.info(f"📌 Título: {title}")
                    logger.info(f"🏢 Empresa: {company}")
                    logger.info(f"📍 Ubicación: {job_location}")
                    
                    # Verificar si la oferta ya existe
                    existing_job = JobOffer.objects.filter(url=url).first()
                    if existing_job:
                        # Actualizar la oferta existente
                        existing_job.title = title
                        existing_job.company = company
                        existing_job.location = job_location
                        existing_job.salary = salary
                        existing_job.work_mode = work_mode
                        existing_job.min_experience = min_experience
                        existing_job.contract_type = contract_type
                        existing_job.studies = studies
                        existing_job.languages = languages
                        existing_job.required_skills = required_skills
                        existing_job.publication_date = publication_date
                        existing_job.search_history = search_history
                        existing_job.inscritos = inscritos
                        jobs_to_update.append(existing_job)
                        logger.info(f"✅ Oferta existente actualizada: {title} en {company}")
                    else:
                        # Crear nueva oferta
                        job = JobOffer(
                            title=title,
                            company=company,
                            location=job_location,
                            salary=salary,
                            work_mode=work_mode,
                            min_experience=min_experience,
                            contract_type=contract_type,
                            studies=studies,
                            languages=languages,
                            required_skills=required_skills,
                            url=url,
                            search_history=search_history,
                            publication_date=publication_date,
                            inscritos=inscritos
                        )
                        jobs_to_create.append(job)
                        logger.info(f"✅ Nueva oferta creada: {title} en {company}")
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando oferta {i}: {str(e)}")
                    continue
            
            # Guardar las ofertas en la base de datos
            if jobs_to_create:
                JobOffer.objects.bulk_create(jobs_to_create)
                logger.info(f"✅ Se guardaron {len(jobs_to_create)} nuevas ofertas en la base de datos")
            
            if jobs_to_update:
                for job in jobs_to_update:
                    job.save()
                logger.info(f"✅ Se actualizaron {len(jobs_to_update)} ofertas existentes")
            
            if not jobs_to_create and not jobs_to_update:
                logger.warning("⚠️ No se guardaron ofertas en la base de datos")
            
            return {
                'success': True,
                'count': len(jobs_to_create) + len(jobs_to_update),
                'search_id': search_history.id
            }
            
        except Exception as e:
            logger.error(f"❌ Error en la búsqueda: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_date(self, date_str):
        """
        Convierte una fecha de LinkedIn a un formato legible
        """
        try:
            if isinstance(date_str, int):
                # Si es un timestamp
                return datetime.fromtimestamp(date_str/1000).strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(date_str, str):
                # Si es una cadena de fecha
                return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            else:
                return 'No especificado'
        except Exception as e:
            logger.error(f"Error al parsear fecha: {str(e)}")
            return 'No especificado'

    def random_sleep(self, min_seconds, max_seconds):
        """
        Pausa aleatoria entre dos segundos
        """
        time.sleep(random.uniform(min_seconds, max_seconds)) 