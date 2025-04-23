from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import logging
import time
from datetime import datetime
from .models import JobOffer, SearchHistory

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tecnoempleo_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TecnoEmpleoScraper:
    def __init__(self):
        """Inicializa el scraper de TecnoEmpleo"""
        self.base_url = "https://www.tecnoempleo.com"
        self.driver = None
        self.logger = logging.getLogger(__name__)
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
            
    def _wait_for_element(self, by, value, timeout=10):
        """Espera a que un elemento esté presente en la página"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Timeout esperando elemento: {value}")
            return None
            
    def _parse_date(self, date_str):
        """Convierte una fecha de TecnoEmpleo a un formato legible"""
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        except:
            return 'No especificado'
            
    def search_jobs(self, keywords, location="", limit=35):
        """
        Busca ofertas de trabajo en TecnoEmpleo
        
        Args:
            keywords (str): Palabras clave para la búsqueda
            location (str): Código de la provincia (opcional)
            limit (int): Límite de ofertas a procesar
        """
        try:
            logger.info(f"🔍 Iniciando búsqueda en TecnoEmpleo")
            logger.info(f"📝 Palabras clave: {keywords}")
            logger.info(f"📍 Ubicación: {location}")
            
            # Navegar a la página principal
            self.driver.get(self.base_url)
            logger.info("✅ Página principal cargada")
            
            # Esperar a que cargue el formulario de búsqueda
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "te"))
            )
            if not search_input:
                raise Exception("No se pudo encontrar el campo de búsqueda")
            
            # Hacer scroll hasta el campo de búsqueda
            self.driver.execute_script("""
                var element = arguments[0];
                var headerOffset = 100;
                var elementPosition = element.getBoundingClientRect().top;
                var offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            """, search_input)
            time.sleep(2)  # Esperar a que se complete el scroll
            
            # Introducir palabras clave
            search_input.clear()  # Limpiar el campo primero
            search_input.send_keys(keywords)
            logger.info("✅ Palabras clave introducidas")
            
            # Si se especifica una ubicación, seleccionarla
            if location:
                # Esperar a que el selector de ubicación esté presente
                location_select = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "pr"))
                )
                
                if location_select:
                    # Hacer scroll hasta el selector usando JavaScript
                    self.driver.execute_script("""
                        var element = arguments[0];
                        var headerOffset = 100;
                        var elementPosition = element.getBoundingClientRect().top;
                        var offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                        window.scrollTo({
                            top: offsetPosition,
                            behavior: 'smooth'
                        });
                    """, location_select)
                    time.sleep(2)  # Esperar a que se complete el scroll
                    
                    # Intentar seleccionar la ubicación usando JavaScript
                    try:
                        self.driver.execute_script("""
                            var select = arguments[0];
                            var value = arguments[1];
                            select.value = value;
                            var event = new Event('change', { bubbles: true });
                            select.dispatchEvent(event);
                        """, location_select, location)
                        logger.info(f"✅ Ubicación seleccionada: {location}")
                    except Exception as e:
                        logger.warning(f"⚠️ No se pudo seleccionar la ubicación usando JavaScript: {str(e)}")
                        # Intentar con Selenium como fallback
                        try:
                            from selenium.webdriver.support.ui import Select
                            select = Select(location_select)
                            select.select_by_value(location)
                            logger.info(f"✅ Ubicación seleccionada (fallback): {location}")
                        except Exception as e:
                            logger.error(f"❌ Error al seleccionar ubicación: {str(e)}")
                            # Continuar sin ubicación
                            location = ""
            
            # Esperar a que el botón de búsqueda esté presente y sea clickeable
            try:
                logger.info("🔍 Buscando botón de búsqueda...")
                search_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-warning.btn-block.mb-3.font-weight-medium"))
                )
                
                if not search_button:
                    raise Exception("No se pudo encontrar el botón de búsqueda")
                
                # Hacer scroll hasta el botón
                logger.info("🔄 Haciendo scroll hasta el botón...")
                self.driver.execute_script("""
                    var element = arguments[0];
                    var headerOffset = 100;
                    var elementPosition = element.getBoundingClientRect().top;
                    var offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                """, search_button)
                time.sleep(2)  # Esperar a que se complete el scroll
                
                # Intentar hacer clic en el botón
                logger.info("🖱️ Intentando hacer clic en el botón...")
                try:
                    # Primero intentar con JavaScript
                    self.driver.execute_script("arguments[0].click();", search_button)
                    logger.info("✅ Clic realizado con JavaScript")
                except Exception as js_error:
                    logger.warning(f"⚠️ Fallo al hacer clic con JavaScript: {str(js_error)}")
                    # Si falla, intentar con Selenium
                    try:
                        search_button.click()
                        logger.info("✅ Clic realizado con Selenium")
                    except Exception as selenium_error:
                        logger.error(f"❌ Fallo al hacer clic con Selenium: {str(selenium_error)}")
                        raise Exception(f"No se pudo hacer clic en el botón: {str(selenium_error)}")
                
                logger.info("✅ Botón de búsqueda pulsado")
                
            except Exception as e:
                logger.error(f"❌ Error al interactuar con el botón de búsqueda: {str(e)}")
                raise Exception(f"Error al interactuar con el botón de búsqueda: {str(e)}")
            
            # Esperar a que carguen los resultados
            logger.info("⏳ Esperando resultados...")
            time.sleep(5)  # Esperar a que carguen los resultados
            
            # Obtener el número de ofertas encontradas
            results_header = self._wait_for_element(By.CSS_SELECTOR, "h1.h4.h6-xs.text-center.my-4")
            if results_header:
                logger.info(f"📊 {results_header.text}")
            
            # Crear un historial de búsqueda
            search_history = SearchHistory.objects.create(
                keywords=keywords,
                location=location,
                source='TecnoEmpleo',
                results_count=0  # Se actualizará al final
            )
            
            # Procesar las ofertas
            jobs_to_create = []
            jobs_to_update = []
            total_offers = 0
            current_page = 1
            
            while total_offers < limit:
                # Extraer las ofertas de la página actual
                job_offers = self.driver.find_elements(By.CSS_SELECTOR, "div.p-3.border.rounded.mb-3.bg-white")
                logger.info(f"📋 Se encontraron {len(job_offers)} ofertas en la página {current_page}")
                
                # Obtener todas las URLs y detalles básicos de las ofertas primero
                offer_details = []
                for offer in job_offers:
                    try:
                        title_elem = offer.find_element(By.CSS_SELECTOR, "a.font-weight-bold.text-cyan-700")
                        company_elem = offer.find_element(By.CSS_SELECTOR, "a.text-primary.link-muted")
                        
                        url = title_elem.get_attribute("href")
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        
                        offer_details.append({
                            'url': url,
                            'title': title,
                            'company': company
                        })
                        logger.info(f"📌 Título: {title}")
                        logger.info(f"🏢 Empresa: {company}")
                    except Exception as e:
                        logger.warning(f"⚠️ No se pudo obtener los detalles básicos de una oferta: {str(e)}")
                        continue
                
                # Procesar cada oferta
                for i, details in enumerate(offer_details, 1):
                    if total_offers >= limit:
                        break
                        
                    try:
                        logger.info(f"\n📋 Procesando oferta {total_offers + 1}/{limit}")
                        
                        # Navegar a la página de detalles de la oferta
                        self.driver.get(details['url'])
                        time.sleep(2)  # Esperar a que cargue la página
                        
                        # Extraer detalles adicionales de la oferta
                        job_details = self._extract_job_details()
                        
                        # Verificar si la oferta ya existe
                        existing_job = JobOffer.objects.filter(url=details['url']).first()
                        if existing_job:
                            # Actualizar la oferta existente
                            self._update_existing_job(existing_job, job_details, search_history)
                            jobs_to_update.append(existing_job)
                            logger.info(f"✅ Oferta existente actualizada: {details['title']} en {details['company']}")
                        else:
                            # Crear nueva oferta
                            job = JobOffer(
                                title=details['title'],
                                company=details['company'],
                                url=details['url'],
                                search_history=search_history,
                                **job_details
                            )
                            jobs_to_create.append(job)
                            logger.info(f"✅ Nueva oferta creada: {details['title']} en {details['company']}")
                        
                        total_offers += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error procesando oferta {total_offers + 1}: {str(e)}")
                        continue
                
                # Verificar si hay más páginas y si necesitamos continuar
                if total_offers < limit:
                    try:
                        next_page = self.driver.find_element(By.CSS_SELECTOR, "a.page-link[href*='pagina=" + str(current_page + 1) + "']")
                        if next_page:
                            logger.info(f"🔄 Navegando a la página {current_page + 1}")
                            next_page.click()
                            time.sleep(3)  # Esperar a que cargue la nueva página
                            current_page += 1
                            continue
                    except:
                        logger.info("ℹ️ No hay más páginas disponibles")
                        break
                else:
                    break
            
            # Actualizar el número total de ofertas en el historial de búsqueda
            search_history.results_count = total_offers
            search_history.save()
            
            # Guardar las ofertas en la base de datos
            if jobs_to_create:
                JobOffer.objects.bulk_create(jobs_to_create)
                logger.info(f"✅ Se guardaron {len(jobs_to_create)} nuevas ofertas")
            
            if jobs_to_update:
                for job in jobs_to_update:
                    job.save()
                logger.info(f"✅ Se actualizaron {len(jobs_to_update)} ofertas existentes")
            
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
            
    def _extract_job_details(self):
        """Extrae los detalles de una oferta de trabajo"""
        try:
            # Esperar a que la página cargue completamente
            time.sleep(2)
            
            # Extraer ubicación
            location = ""
            try:
                location_elem = self.driver.find_element(By.CSS_SELECTOR, "li.list-item.clearfix.border-bottom.py-2 span.float-end")
                location = location_elem.text.strip()
            except:
                pass
            
            # Extraer salario
            salary = ""
            try:
                salary_elem = self.driver.find_element(By.XPATH, "//li[contains(., 'Salario')]/span[@class='float-end']")
                salary = salary_elem.text.strip()
            except:
                pass
            
            # Extraer modo de trabajo
            work_mode = ""
            try:
                work_mode_elem = self.driver.find_element(By.XPATH, "//li[contains(., 'En remoto')]/span[@class='float-end']")
                work_mode = work_mode_elem.text.strip()
            except:
                pass
            
            # Extraer experiencia mínima
            min_experience = ""
            try:
                exp_elem = self.driver.find_element(By.XPATH, "//li[contains(., 'Experiencia')]/span[@class='float-end']")
                min_experience = exp_elem.text.strip()
            except:
                pass
            
            # Extraer tipo de contrato
            contract_type = ""
            try:
                contract_elem = self.driver.find_element(By.XPATH, "//li[contains(., 'Tipo contrato')]/span[@class='float-end']")
                contract_type = contract_elem.text.strip()
            except:
                pass
            
            # Extraer estudios
            studies = ""
            try:
                studies_elem = self.driver.find_element(By.XPATH, "//div[contains(., 'Formación Mínima')]/p[@class='m-0']")
                studies = studies_elem.text.replace('Formación Mínima:', '').strip()
            except:
                pass
            
            # Extraer idiomas
            languages = ""
            try:
                lang_elem = self.driver.find_element(By.XPATH, "//div[contains(., 'Idiomas')]/p[@class='m-0']")
                languages = lang_elem.text.replace('Idiomas:', '').strip()
            except:
                pass
            
            # Extraer habilidades requeridas
            required_skills = ""
            try:
                skills_elems = self.driver.find_elements(By.CSS_SELECTOR, "div.pl--12.pr--12 a.btn.btn-primary.btn-soft.btn-sm")
                required_skills = ', '.join([skill.text.strip() for skill in skills_elems])
            except:
                pass
            
            # Extraer descripción
            description = ""
            try:
                desc_elem = self.driver.find_element(By.XPATH, "//li[contains(., 'Funciones')]/span[@class='float-end']")
                description = desc_elem.text.strip()
            except:
                pass
            
            # Extraer fecha de publicación
            publication_date = ""
            try:
                date_elem = self.driver.find_element(By.CSS_SELECTOR, "span.ml-4")
                publication_date = self._parse_date(date_elem.text.strip())
            except:
                pass
            
            # Extraer número de vacantes
            vacantes = ""
            try:
                vacantes_elem = self.driver.find_element(By.XPATH, "//div[contains(., 'Número de puestos')]/p[@class='m-0']")
                vacantes = vacantes_elem.text.replace('Número de puestos:', '').strip()
            except:
                pass
            
            # Extraer número de inscritos
            inscritos = ""
            try:
                inscritos_elem = self.driver.find_element(By.XPATH, "//div[contains(., 'CVs inscritos en el proceso')]/p[@class='m-0']")
                inscritos = inscritos_elem.text.replace('CVs inscritos en el proceso:', '').strip()
            except:
                pass
            
            return {
                'location': location,
                'salary': salary,
                'work_mode': work_mode,
                'min_experience': min_experience,
                'contract_type': contract_type,
                'studies': studies,
                'languages': languages,
                'required_skills': required_skills,
                'description': description,
                'publication_date': publication_date,
                'vacantes': vacantes,
                'inscritos': inscritos
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo detalles: {str(e)}")
            # Devolver un diccionario vacío en caso de error
            return {
                'location': '',
                'salary': '',
                'work_mode': '',
                'min_experience': '',
                'contract_type': '',
                'studies': '',
                'languages': '',
                'required_skills': '',
                'description': '',
                'publication_date': '',
                'vacantes': '',
                'inscritos': ''
            }
        
    def _update_existing_job(self, job, details, search_history):
        """Actualiza una oferta de trabajo existente"""
        job.location = details['location']
        job.salary = details['salary']
        job.work_mode = details['work_mode']
        job.min_experience = details['min_experience']
        job.contract_type = details['contract_type']
        job.studies = details['studies']
        job.languages = details['languages']
        job.required_skills = details['required_skills']
        job.vacantes = details['vacantes']
        job.inscritos = details['inscritos']
        job.publication_date = details['publication_date']
        job.search_history = search_history
        
    def __del__(self):
        """Cierra el driver al destruir el objeto"""
        if self.driver:
            self.driver.quit() 