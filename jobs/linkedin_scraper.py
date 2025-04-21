from linkedin_api import Linkedin
import logging
import os
import time
from datetime import datetime
from django.conf import settings
from .models import JobOffer, SearchHistory
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
        # Verificar credenciales
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        
        if not self.email or not self.password:
            logger.error("No se encontraron las credenciales de LinkedIn en el archivo .env")
            raise ValueError("No se encontraron las credenciales de LinkedIn en el archivo .env")
        
        logger.info("Credenciales de LinkedIn cargadas correctamente")
        
        self._setup_driver()
        
    def _setup_driver(self):
        """Configura el driver de Selenium"""
        try:
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Configurar el user agent
            options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Configurar preferencias de caché
            options.set_preference("browser.cache.disk.enable", False)
            options.set_preference("browser.cache.memory.enable", False)
            options.set_preference("browser.cache.offline.enable", False)
            options.set_preference("network.http.use-cache", False)
            
            self.driver = webdriver.Firefox(options=options)
            self.driver.set_page_load_timeout(30)
            logger.info("Driver de Selenium configurado correctamente")
            
        except Exception as e:
            logger.error(f"Error al configurar el driver: {str(e)}")
            raise
        
    def search_jobs(self, keywords, location="Spain", limit=2):
        """
        Busca ofertas de trabajo en LinkedIn
        """
        try:
            logger.info(f"🔍 Iniciando búsqueda en LinkedIn")
            logger.info(f"📝 Palabras clave: {keywords}")
            logger.info(f"📍 Ubicación: {location}")
            logger.info(f"📊 Límite de resultados: {limit}")
            
            # Mapeo de códigos a nombres de ubicación
            location_mapping = {
                "Toda España",
                "El extranjero",
                "A Coruña",
                "Álava/Araba",
                "Albacete",
                "Alicante/Alacant",
                "Almería",
                "Asturias",
                "Ávila",
                "Badajoz",
                "Barcelona",
                "Burgos",
                "Cáceres",
                "Cádiz",
                "Cantabria",
                "Castellón/Castelló",
                "Ceuta",
                "Ciudad Real",
                "Córdoba",
                "Cuenca",
                "Girona",
                "Granada",
                "Guadalajara",
                "Guipúzcoa/Gipuzkoa",
                "Huelva",
                "Huesca",
                "Islas Baleares/Illes Balears",
                "Jaén",
                "La Rioja",
                "Las Palmas",
                "León",
                "Lleida",
                "Lugo",
                "Madrid",
                "Málaga",
                "Melilla",
                "Murcia",
                "Navarra",
                "Ourense",
                "Palencia",
                "Pontevedra",
                "Salamanca",
                "Santa Cruz de Tenerife",
                "Segovia",
                "Sevilla",
                "Soria",
                "Tarragona",
                "Teruel",
                "Toledo",
                "Valencia/València",
                "Valladolid",
                "Vizcaya/Bizkaia",
                "Zamora",
                "Zaragoza"
            }
            
            # Inicializar la API de LinkedIn
            logger.info("🔄 Conectando a LinkedIn...")
            api = Linkedin(self.email, self.password)
            
            # Mapeo de ubicaciones comunes a códigos de LinkedIn
            linkedin_location_mapping = {
                "Asturias": "102454443",
                "Madrid": "105646813",
                "Barcelona": "105646813",
                "Valencia": "105646813",
                "Sevilla": "105646813",
                "Bilbao": "105646813",
                "Málaga": "105646813",
                "Zaragoza": "105646813",
                "Spain": "105646813"
            }
            
            # Obtener el código de ubicación para LinkedIn
            location_code = linkedin_location_mapping.get(location, "105646813")  # Por defecto, España
            
            logger.info("🔍 Realizando búsqueda...")
            # Realizar la búsqueda con límite de 2 ofertas
            search_results = api.search_jobs(
                keywords=keywords,
                location_name=location_code,
                limit=2  # Forzamos el límite a 2 ofertas
            )
            
            # Asegurarnos de que solo procesamos 2 ofertas
            search_results = search_results[:2]
            
            logger.info(f"✅ Búsqueda completada. Se encontraron {len(search_results)} ofertas")
            
            # Crear un historial de búsqueda
            logger.info("💾 Guardando búsqueda en el historial...")
            search_history = SearchHistory.objects.create(
                keywords=keywords,
                location=location,  # Usar el nombre de la ubicación, no el código
                source='LinkedIn',
                results_count=len(search_results)
            )
            logger.info(f"✅ Búsqueda guardada con ID: {search_history.id}")
            
            # Guardar las ofertas en la base de datos
            logger.info("💾 Guardando ofertas en la base de datos...")
            jobs_to_create = []
            jobs_to_update = []
            
            for i, result in enumerate(search_results, 1):
                try:
                    logger.info(f"\n📋 Procesando oferta {i}/2")
                    
                    # Obtener el ID de la oferta
                    job_id = result.get('jobPosting', {}).get('id') or result.get('dashEntityUrn', '').split(':')[-1] or result.get('entityUrn', '').split(':')[-1]
                    
                    if not job_id:
                        logger.warning("No se pudo obtener el ID de la oferta")
                        continue
                    
                    logger.info(f"🔑 ID de la oferta: {job_id}")
                    
                    # Obtener detalles de la oferta
                    job_details = api.get_job(job_id)
                    
                    # Extraer información básica
                    title = job_details.get('title', '')
                    company = job_details.get('companyName', '')
                    job_location = job_details.get('location', '')
                    
                    # Si la ubicación es un código numérico, buscar su nombre en el mapeo
                    if job_location and job_location.isdigit():
                        job_location = location_mapping.get(job_location, location)  # Si no encuentra el código, usar la ubicación original
                    elif not job_location:
                        job_location = location  # Usar la ubicación original de la búsqueda
                    
                    url = f"https://www.linkedin.com/jobs/view/{job_id}"
                    
                    logger.info(f"📌 Título: {title}")
                    logger.info(f"🏢 Empresa: {company}")
                    logger.info(f"📍 Ubicación: {job_location}")
                    
                    # Extraer salario
                    salary = 'No especificado'
                    if 'salary' in job_details:
                        salary_info = job_details['salary']
                        if isinstance(salary_info, dict):
                            if 'min' in salary_info and 'max' in salary_info:
                                salary = f"{salary_info['min']} - {salary_info['max']} {salary_info.get('currency', '')}"
                            elif 'amount' in salary_info:
                                salary = f"{salary_info['amount']} {salary_info.get('currency', '')}"
                    logger.info(f"💰 Salario extraído: {salary}")
                    
                    # Extraer modo de trabajo
                    work_mode = 'No especificado'
                    if 'workplaceType' in job_details:
                        work_mode = job_details['workplaceType']
                        if work_mode.startswith('urn:li:fs_workplaceType:'):
                            work_mode = work_mode.split(':')[-1]
                            if work_mode == '1':
                                work_mode = 'Presencial'
                            elif work_mode == '2':
                                work_mode = 'Híbrido'
                            elif work_mode == '3':
                                work_mode = 'Remoto'
                    logger.info(f"🏠 Modo de trabajo extraído: {work_mode}")
                    
                    # Extraer experiencia mínima
                    min_experience = 'No especificado'
                    if 'experienceLevel' in job_details:
                        exp = job_details['experienceLevel']
                        if isinstance(exp, dict):
                            min_experience = exp.get('value', '')
                        elif isinstance(exp, str):
                            min_experience = exp
                    logger.info(f"👨‍💼 Experiencia extraída: {min_experience}")
                    
                    # Extraer tipo de contrato
                    contract_type = 'No especificado'
                    if 'employmentType' in job_details:
                        contract = job_details['employmentType']
                        if isinstance(contract, dict):
                            contract_type = contract.get('value', '')
                        elif isinstance(contract, str):
                            contract_type = contract
                    logger.info(f"📄 Tipo de contrato extraído: {contract_type}")
                    
                    # Extraer estudios
                    studies = 'No especificado'
                    if 'educationRequirements' in job_details:
                        education = job_details['educationRequirements']
                        if isinstance(education, dict):
                            studies = education.get('value', '')
                        elif isinstance(education, str):
                            studies = education
                    logger.info(f"🎓 Estudios extraídos: {studies}")
                    
                    # Extraer idiomas
                    languages = 'No especificado'
                    if 'languageRequirements' in job_details:
                        langs = job_details['languageRequirements']
                        if isinstance(langs, list):
                            languages = ', '.join([lang.get('name', '') for lang in langs])
                        elif isinstance(langs, str):
                            languages = langs
                    logger.info(f"🌐 Idiomas extraídos: {languages}")
                    
                    # Extraer habilidades requeridas
                    required_skills = 'No especificado'
                    if 'requiredSkills' in job_details:
                        skills = job_details['requiredSkills']
                        if isinstance(skills, list):
                            required_skills = ', '.join([skill.get('name', '') for skill in skills])
                        elif isinstance(skills, str):
                            required_skills = skills
                    logger.info(f"💡 Habilidades extraídas: {required_skills}")
                    
                    # Extraer vacantes e inscritos
                    vacantes = 'No especificado'
                    inscritos = 'No especificado'
                    if 'openPositions' in job_details:
                        vacantes = str(job_details['openPositions'])
                    if 'applicants' in job_details:
                        inscritos = str(job_details['applicants'])
                    logger.info(f"👥 Vacantes: {vacantes}, Inscritos: {inscritos}")
                    
                    # Extraer fecha de publicación
                    publication_date = 'No especificado'
                    if 'listedAt' in job_details:
                        publication_date = self._parse_date(job_details['listedAt'])
                    logger.info(f"📅 Fecha de publicación: {publication_date}")
                    
                    # Verificar si la oferta ya existe
                    existing_job = JobOffer.objects.filter(url=url).first()
                    if existing_job:
                        # Actualizar la oferta existente
                        existing_job.title = title
                        existing_job.company = company
                        existing_job.location = job_location  # Usar la ubicación procesada
                        existing_job.salary = salary
                        existing_job.work_mode = work_mode
                        existing_job.min_experience = min_experience
                        existing_job.contract_type = contract_type
                        existing_job.studies = studies
                        existing_job.languages = languages
                        existing_job.required_skills = required_skills
                        existing_job.vacantes = vacantes
                        existing_job.inscritos = inscritos
                        existing_job.publication_date = publication_date
                        existing_job.search_history = search_history
                        jobs_to_update.append(existing_job)
                        logger.info(f"✅ Oferta existente actualizada: {title} en {company}")
                    else:
                        # Crear nueva oferta
                        job = JobOffer(
                            title=title,
                            company=company,
                            location=job_location,  # Usar la ubicación procesada
                            salary=salary,
                            work_mode=work_mode,
                            min_experience=min_experience,
                            contract_type=contract_type,
                            studies=studies,
                            languages=languages,
                            required_skills=required_skills,
                            url=url,
                            search_history=search_history,
                            vacantes=vacantes,
                            inscritos=inscritos,
                            publication_date=publication_date
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