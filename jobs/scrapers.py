import time
from django.utils import timezone
from .models import JobOffer, SearchHistory
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import re
import logging
import random
from urllib.parse import quote
import os
import tempfile

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InfoJobsScraper:
    BASE_URL = "https://www.infojobs.net"
    
    def __init__(self, headless=False, use_existing_browser=False):
        logger.info("Iniciando InfoJobsScraper...")
        
        if use_existing_browser:
            logger.info("Conectando a una instancia existente de Firefox...")
            try:
                # Crear un perfil temporal para Firefox
                temp_dir = tempfile.mkdtemp()
                firefox_profile = webdriver.FirefoxProfile(temp_dir)
                
                # Configurar opciones para usar el perfil existente
                firefox_options = Options()
                firefox_options.profile = firefox_profile
                
                # Configurar el servicio con la ruta específica del geckodriver
                service = Service('/home/josias/.wdm/drivers/geckodriver/linux64/v0.36.0/geckodriver')
                
                # Inicializar el driver con el perfil y el servicio
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
                
                # Abrir una nueva pestaña
                self.driver.execute_script("window.open('about:blank', '_blank');")
                
                # Cambiar a la nueva pestaña
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                logger.info("Conexión exitosa a Firefox existente y nueva pestaña abierta")
            except Exception as e:
                logger.error(f"Error al conectar a Firefox existente: {str(e)}")
                raise
        else:
            # Configurar opciones de Firefox
            firefox_options = Options()
            if headless:
                firefox_options.add_argument('--headless')
            firefox_options.add_argument('--disable-gpu')
            firefox_options.add_argument('--no-sandbox')
            firefox_options.add_argument('--disable-dev-shm-usage')
            firefox_options.add_argument('--window-size=1920,1080')
            firefox_options.add_argument('--disable-extensions')
            firefox_options.add_argument('--disable-infobars')
            firefox_options.add_argument('--disable-notifications')
            firefox_options.add_argument('--disable-popup-blocking')
            
            # Lista de User-Agents comunes
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
            ]
            
            # Configurar el perfil de Firefox
            firefox_profile = webdriver.FirefoxProfile() if hasattr(webdriver, 'FirefoxProfile') else None
            if firefox_profile:
                firefox_profile.set_preference("general.useragent.override", random.choice(user_agents))
                firefox_profile.set_preference("intl.accept_languages", "es-ES,es")
                firefox_profile.set_preference("browser.cache.disk.enable", False)
                firefox_profile.set_preference("browser.cache.memory.enable", False)
                firefox_profile.set_preference("browser.cache.offline.enable", False)
                firefox_profile.set_preference("network.http.use-cache", False)
                firefox_profile.update_preferences()
                firefox_options.profile = firefox_profile
            
            try:
                # Configurar el servicio con la ruta específica del geckodriver
                service = Service('/home/josias/.wdm/drivers/geckodriver/linux64/v0.36.0/geckodriver')
                
                # Inicializar el driver con el servicio
                logger.info("Inicializando el driver de Firefox...")
                self.driver = webdriver.Firefox(
                    service=service,
                    options=firefox_options
                )
                self.driver.implicitly_wait(20)
                logger.info("Driver de Firefox inicializado correctamente")
            except WebDriverException as e:
                logger.error(f"Error al inicializar el driver: {str(e)}")
                raise
        
        # Mapeo manual de códigos de provincia a nombres
        self.province_map = {
            "0": "Toda España",
            "foreign": "El extranjero",
            "28": "A Coruña",
            "2": "Álava/Araba",
            "3": "Albacete",
            "4": "Alicante/Alacant",
            "5": "Almería",
            "6": "Asturias",
            "7": "Ávila",
            "8": "Badajoz",
            "9": "Barcelona",
            "10": "Burgos",
            "11": "Cáceres",
            "12": "Cádiz",
            "13": "Cantabria",
            "14": "Castellón/Castelló",
            "15": "Ceuta",
            "16": "Ciudad Real",
            "17": "Córdoba",
            "18": "Cuenca",
            "19": "Girona",
            "21": "Granada",
            "22": "Guadalajara",
            "23": "Guipúzcoa/Gipuzkoa",
            "24": "Huelva",
            "25": "Huesca",
            "26": "Islas Baleares/Illes Balears",
            "27": "Jaén",
            "29": "La Rioja",
            "20": "Las Palmas",
            "30": "León",
            "31": "Lleida",
            "32": "Lugo",
            "33": "Madrid",
            "34": "Málaga",
            "35": "Melilla",
            "36": "Murcia",
            "37": "Navarra",
            "38": "Ourense",
            "39": "Palencia",
            "40": "Pontevedra",
            "41": "Salamanca",
            "46": "Santa Cruz de Tenerife",
            "42": "Segovia",
            "43": "Sevilla",
            "44": "Soria",
            "45": "Tarragona",
            "47": "Teruel",
            "48": "Toledo",
            "49": "Valencia/València",
            "50": "Valladolid",
            "51": "Vizcaya/Bizkaia",
            "52": "Zamora",
            "53": "Zaragoza"
        }
    
    def __del__(self):
        if hasattr(self, 'driver'):
            logger.info("Cerrando el driver de Firefox...")
            try:
                self.driver.quit()
                logger.info("Driver cerrado correctamente")
            except Exception as e:
                logger.error(f"Error al cerrar el driver: {str(e)}")

    def wait_for_element(self, selector, timeout=30, by=By.CSS_SELECTOR):
        """Espera a que un elemento esté presente y visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            logger.error(f"Timeout esperando el elemento: {selector}")
            return None

    def wait_for_clickable(self, selector, timeout=30, by=By.CSS_SELECTOR):
        """Espera a que un elemento esté presente y clickeable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            return element
        except TimeoutException:
            logger.error(f"Timeout esperando el elemento clickeable: {selector}")
            return None

    def random_sleep(self, min_seconds=1, max_seconds=3):
        """Espera un tiempo aleatorio para simular comportamiento humano"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def take_screenshot(self, name="error"):
        """Captura una captura de pantalla para depuración"""
        try:
            # Crear directorio para capturas de pantalla si no existe
            screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'screenshots')
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            
            # Generar nombre de archivo con timestamp
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(screenshot_dir, filename)
            
            # Capturar pantalla
            self.driver.save_screenshot(filepath)
            logger.info(f"Captura de pantalla guardada en: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error al capturar pantalla: {str(e)}")
            return None

    def extract_job_details(self, url):
        """Extrae los detalles de una oferta de trabajo visitando su página"""
        try:
            logger.info(f"Extrayendo detalles de la oferta: {url}")
            self.driver.get(url)
            
            # Reducir el tiempo de espera inicial al mínimo
            self.random_sleep(0.3, 0.5)
            
            # Obtener el HTML de la página completa
            page_html = self.driver.page_source
            page_soup = BeautifulSoup(page_html, 'html.parser')
            
            # Extraer salario
            salary = ""
            salary_selectors = [
                ".ij-OfferDetailHeader-detailsList-item:contains('€')",
                ".ij-OfferDetailHeader-detailsList-item p:contains('€')",
                ".ij-OfferDetailHeader-detailsList-item .ij-Text:contains('€')",
                ".salary",
                ".job-salary",
                ".ij-OfferDetailHeader-descriptionList-item:contains('€')",
                ".ij-OfferDetailHeader-descriptionList-item p:contains('€')",
                ".ij-OfferDetailHeader-descriptionList-item .ij-Text:contains('€')",
                "p:contains('€')",
                ".ij-Text:contains('€')",
                "span:contains('€')",
                "div:contains('€')"
            ]
            
            for selector in salary_selectors:
                salary_elem = page_soup.select_one(selector)
                if salary_elem:
                    salary = salary_elem.text.strip()
                    break
            
            # Extraer modo de trabajo
            work_mode = ""
            work_mode_selectors = [
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='m12.98 5.588'])",
                ".ij-OfferDetailHeader-detailsList-item:has(svg path[d*='m12.98 5.588'])",
                ".ij-OfferDetailHeader-detailsList-item p:contains('Presencial')",
                ".ij-OfferDetailHeader-detailsList-item p:contains('Teletrabajo')",
                ".ij-OfferDetailHeader-detailsList-item p:contains('Híbrido')",
                ".work-mode",
                ".job-work-mode",
                ".ij-OfferDetailHeader-descriptionList-item:has(svg[width='16'][height='16'] path[d*='m12.98 5.588'])",
                ".ij-OfferDetailHeader-descriptionList-item:has(svg path[d*='m12.98 5.588'])",
                ".ij-OfferDetailHeader-descriptionList-item p:contains('Presencial')",
                ".ij-OfferDetailHeader-descriptionList-item p:contains('Teletrabajo')",
                ".ij-OfferDetailHeader-descriptionList-item p:contains('Híbrido')",
                "p:contains('Presencial')",
                "p:contains('Teletrabajo')",
                "p:contains('Híbrido')",
                "span:contains('Presencial')",
                "span:contains('Teletrabajo')",
                "span:contains('Híbrido')",
                "div:contains('Presencial')",
                "div:contains('Teletrabajo')",
                "div:contains('Híbrido')"
            ]
            
            for selector in work_mode_selectors:
                work_mode_elem = page_soup.select_one(selector)
                if work_mode_elem:
                    # Intentar obtener solo el texto del párrafo dentro del elemento
                    p_elem = work_mode_elem.select_one("p")
                    if p_elem:
                        work_mode = p_elem.text.strip()
                    else:
                        work_mode = work_mode_elem.text.strip()
                    break
            
            # Extraer experiencia mínima
            min_experience = ""
            experience_selectors = [
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='M12.333 3.834'])",
                ".ij-OfferDetailHeader-detailsList-item:has(svg path[d*='M12.333 3.834'])",
                ".ij-OfferDetailHeader-detailsList-item p:contains('Experiencia mínima')",
                ".experience",
                ".job-experience",
                ".ij-OfferDetailHeader-descriptionList-item:has(svg[width='16'][height='16'] path[d*='M12.333 3.834'])",
                ".ij-OfferDetailHeader-descriptionList-item:has(svg path[d*='M12.333 3.834'])",
                ".ij-OfferDetailHeader-descriptionList-item p:contains('Experiencia mínima')",
                "p:contains('Experiencia mínima')",
                "span:contains('Experiencia mínima')",
                "div:contains('Experiencia mínima')"
            ]
            
            for selector in experience_selectors:
                experience_elem = page_soup.select_one(selector)
                if experience_elem:
                    # Intentar obtener solo el texto del párrafo dentro del elemento
                    p_elem = experience_elem.select_one("p")
                    if p_elem:
                        min_experience = p_elem.text.strip()
                    else:
                        min_experience = experience_elem.text.strip()
                    break
            
            # Extraer tipo de contrato
            contract_type = ""
            contract_selectors = [
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='M10.973 14.834'])",
                ".ij-OfferDetailHeader-detailsList-item:has(svg path[d*='M10.973 14.834'])",
                ".ij-OfferDetailHeader-detailsList-item p:contains('Contrato')",
                ".contract-type",
                ".job-contract",
                ".ij-OfferDetailHeader-descriptionList-item:has(svg[width='16'][height='16'] path[d*='M10.973 14.834'])",
                ".ij-OfferDetailHeader-descriptionList-item:has(svg path[d*='M10.973 14.834'])",
                ".ij-OfferDetailHeader-descriptionList-item p:contains('Contrato')",
                "p:contains('Contrato')",
                "span:contains('Contrato')",
                "div:contains('Contrato')"
            ]
            
            for selector in contract_selectors:
                contract_elem = page_soup.select_one(selector)
                if contract_elem:
                    # Intentar obtener solo el texto del párrafo dentro del elemento
                    p_elem = contract_elem.select_one("p")
                    if p_elem:
                        contract_type = p_elem.text.strip()
                    else:
                        contract_type = contract_elem.text.strip()
                    break
            
            # Extraer estudios mínimos
            studies = ""
            studies_selectors = [
                "dt:contains('Estudios mínimos') + dd p",
                "dt:contains('Estudios mínimos') + dd",
                "h3:contains('Requisitos') + dl dt:contains('Estudios mínimos') + dd p",
                "h3:contains('Requisitos') + dl dt:contains('Estudios mínimos') + dd"
            ]
            
            for selector in studies_selectors:
                studies_elem = page_soup.select_one(selector)
                if studies_elem:
                    studies = studies_elem.text.strip()
                    break
            
            # Extraer idiomas requeridos
            languages = ""
            languages_selectors = [
                "dt:contains('Idiomas requeridos') + dd ul li p",
                "dt:contains('Idiomas requeridos') + dd ul li",
                "dt:contains('Idiomas requeridos') + dd",
                "h3:contains('Requisitos') + dl dt:contains('Idiomas requeridos') + dd ul li p",
                "h3:contains('Requisitos') + dl dt:contains('Idiomas requeridos') + dd ul li",
                "h3:contains('Requisitos') + dl dt:contains('Idiomas requeridos') + dd"
            ]
            
            for selector in languages_selectors:
                languages_elem = page_soup.select_one(selector)
                if languages_elem:
                    languages = languages_elem.text.strip()
                    break
            
            # Extraer conocimientos necesarios
            required_skills = ""
            skills_selectors = [
                "dt:contains('Conocimientos necesarios') + dd .ij-OfferDetailRequirements-requiredSkills",
                "dt:contains('Conocimientos necesarios') + dd",
                "h3:contains('Requisitos') + dl dt:contains('Conocimientos necesarios') + dd .ij-OfferDetailRequirements-requiredSkills",
                "h3:contains('Requisitos') + dl dt:contains('Conocimientos necesarios') + dd"
            ]
            
            for selector in skills_selectors:
                skills_elem = page_soup.select_one(selector)
                if skills_elem:
                    # Extraer todos los tags de habilidades
                    skill_tags = skills_elem.select(".sui-AtomTag-label")
                    if skill_tags:
                        required_skills = ", ".join([tag.text.strip() for tag in skill_tags])
                    else:
                        required_skills = skills_elem.text.strip()
                    break
            
            # Si no se encontraron los detalles, intentar una segunda vez con un tiempo de espera más largo
            if not any([salary, work_mode, min_experience, contract_type, studies, languages, required_skills]):
                logger.info("No se encontraron detalles en el primer intento, reintentando...")
                self.random_sleep(0.5, 1)  # Reducir el tiempo de espera en el segundo intento
                
                # Obtener el HTML actualizado
                page_html = self.driver.page_source
                page_soup = BeautifulSoup(page_html, 'html.parser')
                
                # Intentar extraer los detalles nuevamente
                for selector in salary_selectors:
                    salary_elem = page_soup.select_one(selector)
                    if salary_elem:
                        salary = salary_elem.text.strip()
                        break
                
                for selector in work_mode_selectors:
                    work_mode_elem = page_soup.select_one(selector)
                    if work_mode_elem:
                        p_elem = work_mode_elem.select_one("p")
                        if p_elem:
                            work_mode = p_elem.text.strip()
                        else:
                            work_mode = work_mode_elem.text.strip()
                        break
                
                for selector in experience_selectors:
                    experience_elem = page_soup.select_one(selector)
                    if experience_elem:
                        p_elem = experience_elem.select_one("p")
                        if p_elem:
                            min_experience = p_elem.text.strip()
                        else:
                            min_experience = experience_elem.text.strip()
                        break
                
                for selector in contract_selectors:
                    contract_elem = page_soup.select_one(selector)
                    if contract_elem:
                        p_elem = contract_elem.select_one("p")
                        if p_elem:
                            contract_type = p_elem.text.strip()
                        else:
                            contract_type = contract_elem.text.strip()
                        break
                
                for selector in studies_selectors:
                    studies_elem = page_soup.select_one(selector)
                    if studies_elem:
                        studies = studies_elem.text.strip()
                        break
                
                for selector in languages_selectors:
                    languages_elem = page_soup.select_one(selector)
                    if languages_elem:
                        languages = languages_elem.text.strip()
                        break
                
                for selector in skills_selectors:
                    skills_elem = page_soup.select_one(selector)
                    if skills_elem:
                        # Extraer todos los tags de habilidades
                        skill_tags = skills_elem.select(".sui-AtomTag-label")
                        if skill_tags:
                            required_skills = ", ".join([tag.text.strip() for tag in skill_tags])
                        else:
                            required_skills = skills_elem.text.strip()
                        break
            
            logger.info(f"Detalles extraídos - Salario: {salary}, Modo: {work_mode}, Exp: {min_experience}, Contrato: {contract_type}, Estudios: {studies}, Idiomas: {languages}, Habilidades: {required_skills}")
            
            return {
                'salary': salary,
                'work_mode': work_mode,
                'min_experience': min_experience,
                'contract_type': contract_type,
                'studies': studies,
                'languages': languages,
                'required_skills': required_skills
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo detalles de la oferta: {str(e)}")
            return {}

    def search_jobs(self, keywords, location="0"):
        try:
            # Obtener el nombre de la ubicación del mapeo
            location_name = self.province_map.get(location, "Toda España")
            logger.info(f"Iniciando búsqueda en {location_name} (código: {location})")
            
            # Navegar a la página principal de InfoJobs
            logger.info("Navegando a la página principal de InfoJobs...")
            self.driver.get(self.BASE_URL)
            
            # Esperar más tiempo para que la página se cargue completamente
            logger.info("Esperando a que la página se cargue completamente...")
            self.random_sleep(8, 10)
            
            # Imprimir la URL actual para depuración
            current_url = self.driver.current_url
            logger.info(f"URL actual: {current_url}")
            
            # Capturar pantalla inicial para depuración
            self.take_screenshot("initial_page")
            
            # Manejar el botón de cookies si está presente
            logger.info("Buscando el botón de cookies...")
            cookie_button_selectors = [
                "#didomi-notice-agree-button",
                "button[id*='cookie-accept']",
                "button[id*='cookie-consent']",
                "button[class*='cookie-accept']",
                "button[class*='cookie-consent']",
                "button[class*='cookies-accept']",
                ".cookie-accept-button",
                ".cookie-consent-button",
                "#accept-cookies",
                "#acceptCookies",
                "button[aria-label*='Aceptar']",
                "button[aria-label*='aceptar']",
                "button[aria-label*='Cookies']",
                "button[aria-label*='cookies']",
                ".didomi-button-highlight",
                ".didomi-button"
            ]
            
            for selector in cookie_button_selectors:
                logger.info(f"Intentando selector de cookies: {selector}")
                try:
                    cookie_button = self.wait_for_clickable(selector, timeout=5)
                    if cookie_button:
                        logger.info("Botón de cookies encontrado, haciendo clic...")
                        cookie_button.click()
                        self.random_sleep(2, 3)  # Aumentamos el tiempo de espera después de cerrar las cookies
                        break
                except Exception as e:
                    logger.info(f"No se encontró el botón de cookies con selector {selector}: {str(e)}")
                    continue
            
            # Buscar el campo de búsqueda con diferentes selectores
            logger.info("Buscando el campo de búsqueda...")
            search_input = None
            
            # Intentar diferentes selectores para el campo de búsqueda
            search_selectors = [
                "input[name='palabra']",
                "input#palabra",
                "input[placeholder*='Puesto, empresa o palabra clave']",
                "input.ui-autocomplete-input",
                "input[name='keyword']",
                "input[placeholder*='buscar']",
                "input[placeholder*='Buscar']",
                "input[placeholder*='empleo']",
                "input[placeholder*='Empleo']",
                "input.ij-SearchBar-input",
                "input.search-input",
                "input.search",
                "#keyword",
                ".ij-SearchBar input",
                ".search-bar input",
                "input[type='text']",
                "input[aria-label*='buscar']",
                "input[aria-label*='Buscar']"
            ]
            
            for selector in search_selectors:
                logger.info(f"Intentando selector: {selector}")
                search_input = self.wait_for_element(selector, timeout=5)
                if search_input:
                    logger.info(f"Campo de búsqueda encontrado con selector: {selector}")
                    break
            
            if not search_input:
                logger.error("No se encontró el campo de búsqueda")
                self.take_screenshot("search_field_not_found")
                return {
                    'success': False,
                    'error': 'No se encontró el campo de búsqueda'
                }
            
            # Limpiar el campo de búsqueda y escribir las palabras clave
            logger.info(f"Escribiendo palabras clave: {keywords}")
            search_input.clear()
            search_input.send_keys(keywords)
            self.random_sleep(1, 2)
            
            # Buscar el campo de ubicación con diferentes selectores
            logger.info("Buscando el campo de ubicación...")
            location_input = None
            
            # Intentar diferentes selectores para el campo de ubicación
            location_selectors = [
                "select#of_provincia",
                "select[name='of_provincia']",
                "select.chosen-select",
                ".chosen-container input",
                ".chosen-search input",
                "input[name='provinceIds']",
                "input[placeholder*='ubicación']",
                "input[placeholder*='Ubicación']",
                "input[placeholder*='localidad']",
                "input[placeholder*='Localidad']",
                "input.ij-SearchBar-location-input",
                "input.location-input",
                "input.location"
            ]
            
            for selector in location_selectors:
                logger.info(f"Intentando selector de ubicación: {selector}")
                location_input = self.wait_for_element(selector, timeout=5)
                if location_input:
                    logger.info(f"Campo de ubicación encontrado con selector: {selector}")
                    break
            
            if location_input:
                # Si es un select, usar el método select_by_value
                if location_input.tag_name == 'select':
                    logger.info(f"Seleccionando ubicación por valor: {location}")
                    try:
                        # Intentar usar Select directamente
                        from selenium.webdriver.support.ui import Select
                        select = Select(location_input)
                        select.select_by_value(location)
                        logger.info("Ubicación seleccionada usando Select")
                    except Exception as e:
                        logger.info(f"Error al usar Select directamente: {str(e)}")
                        logger.info("Intentando método alternativo para Chosen...")
                        
                        # Método alternativo para Chosen
                        try:
                            # Hacer clic en el contenedor de Chosen para abrir el desplegable
                            chosen_container = self.driver.find_element(By.CSS_SELECTOR, f"#{location_input.get_attribute('id')}_chosen")
                            chosen_container.click()
                            self.random_sleep(1, 2)
                            
                            # Buscar la opción por texto
                            option_text = self.province_map.get(location, "Toda España")
                            option = self.driver.find_element(By.XPATH, f"//li[contains(@class, 'active-result') and contains(text(), '{option_text}')]")
                            option.click()
                            logger.info(f"Ubicación seleccionada usando método alternativo: {option_text}")
                        except Exception as e2:
                            logger.error(f"Error al usar método alternativo: {str(e2)}")
                            # Intentar un último método usando JavaScript
                            try:
                                self.driver.execute_script(f"document.getElementById('{location_input.get_attribute('id')}').value = '{location}';")
                                self.driver.execute_script(f"document.getElementById('{location_input.get_attribute('id')}').dispatchEvent(new Event('change'));")
                                logger.info("Ubicación seleccionada usando JavaScript")
                            except Exception as e3:
                                logger.error(f"Error al usar JavaScript: {str(e3)}")
                                return {
                                    'success': False,
                                    'error': f'No se pudo seleccionar la ubicación: {str(e)}'
                                }
                    
                    self.random_sleep(1, 2)
                else:
                    # Limpiar el campo de ubicación y escribir la ubicación
                    logger.info(f"Escribiendo ubicación: {location_name}")
                    location_input.clear()
                    location_input.send_keys(location_name)
                    self.random_sleep(1, 2)
                    
                    # Esperar a que aparezcan las sugerencias y seleccionar la primera
                    suggestions_selectors = [
                        ".chosen-results",
                        ".ij-SearchBar-suggestions",
                        ".search-suggestions",
                        ".suggestions",
                        ".location-suggestions",
                        ".autocomplete-suggestions"
                    ]
                    
                    suggestions = None
                    for selector in suggestions_selectors:
                        logger.info(f"Intentando selector de sugerencias: {selector}")
                        suggestions = self.wait_for_element(selector, timeout=5)
                        if suggestions:
                            logger.info(f"Sugerencias encontradas con selector: {selector}")
                            break
                    
                    if suggestions:
                        suggestion_item_selectors = [
                            ".chosen-results li.active-result",
                            ".ij-SearchBar-suggestion-item",
                            ".suggestion-item",
                            ".location-suggestion",
                            "li.suggestion",
                            "li.autocomplete-item"
                        ]
                        
                        first_suggestion = None
                        for selector in suggestion_item_selectors:
                            logger.info(f"Intentando selector de item de sugerencia: {selector}")
                            first_suggestion = self.wait_for_clickable(selector, timeout=5)
                            if first_suggestion:
                                logger.info(f"Item de sugerencia encontrado con selector: {selector}")
                                break
                        
                        if first_suggestion:
                            first_suggestion.click()
                            self.random_sleep(1, 2)
            
            # Buscar el botón de búsqueda con diferentes selectores
            logger.info("Buscando el botón de búsqueda...")
            search_button = None
            
            # Intentar diferentes selectores para el botón de búsqueda
            button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button.ij-SearchBar-submit",
                "button.search-button",
                "button.search",
                "input.ij-SearchBar-submit",
                "input.search-button",
                "input.search",
                "button.btn-search",
                "button.btn-search-primary",
                "button.btn-primary",
                "button.btn",
                "button:contains('Buscar')",
                "button:contains('buscar')",
                "input:contains('Buscar')",
                "input:contains('buscar')"
            ]
            
            for selector in button_selectors:
                logger.info(f"Intentando selector de botón: {selector}")
                search_button = self.wait_for_clickable(selector, timeout=5)
                if search_button:
                    logger.info(f"Botón de búsqueda encontrado con selector: {selector}")
                    break
            
            if not search_button:
                # Intentar encontrar el botón por texto
                logger.info("Intentando encontrar el botón por texto...")
                try:
                    search_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar') or contains(text(), 'buscar')]")
                    logger.info("Botón de búsqueda encontrado por texto")
                except NoSuchElementException:
                    try:
                        search_button = self.driver.find_element(By.XPATH, "//input[@value='Buscar' or @value='buscar']")
                        logger.info("Botón de búsqueda encontrado por valor")
                    except NoSuchElementException:
                        logger.error("No se encontró el botón de búsqueda")
                        self.take_screenshot("search_button_not_found")
                        return {
                            'success': False,
                            'error': 'No se encontró el botón de búsqueda'
                        }
            
            # Hacer clic en el botón de búsqueda
            logger.info("Haciendo clic en el botón de búsqueda...")
            search_button.click()
            
            # Esperar a que se carguen los resultados
            logger.info("Esperando a que se carguen los resultados...")
            self.random_sleep(3, 5)
            
            # Imprimir la URL actual para depuración
            current_url = self.driver.current_url
            logger.info(f"URL después de la búsqueda: {current_url}")
            
            # Intentar diferentes selectores para detectar cuando la página está cargada
            selectors = [
                ".ij-ResultsOverview",
                "h1.ij-ResultsOverview",
                "#main-heading",
                ".ij-SearchResults-count",
                ".ij-OfferCardContent",
                ".ij-OfferCardContent-description",
                "#filterSideBar",
                ".ij-SearchResults",
                ".ij-Page",
                ".search-results",
                ".results-count",
                ".job-list",
                ".job-card"
            ]
            
            # Intentar hasta 3 veces con diferentes tiempos de espera
            max_retries = 3
            for retry in range(max_retries):
                logger.info(f"Intento {retry + 1} de {max_retries}")
                
                element_found = False
                for selector in selectors:
                    logger.info(f"Intentando encontrar el elemento: {selector}")
                    element = self.wait_for_element(selector, timeout=20 + (retry * 10))
                    if element:
                        element_found = True
                        logger.info(f"Elemento encontrado: {selector}")
                        break
                
                if element_found:
                    break
                
                if retry < max_retries - 1:
                    wait_time = 5 + (retry * 5)
                    logger.info(f"Reintentando en {wait_time} segundos...")
                    time.sleep(wait_time)
                    self.driver.refresh()
            
            if not element_found:
                logger.error("No se pudo detectar ningún elemento en la página después de varios intentos")
                self.take_screenshot("results_page_not_loaded")
                return {
                    'success': False,
                    'error': 'No se pudo cargar la página de resultados'
                }
            
            # Dar tiempo adicional para que se cargue todo el contenido
            logger.info("Esperando a que se cargue todo el contenido...")
            self.random_sleep(3, 5)
            
            # Obtener el HTML de la página
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extraer el número total de ofertas
            total_offers = 0
            results_count_selectors = [
                ".ij-ResultsOverview",
                "h1.ij-ResultsOverview",
                "#main-heading",
                ".ij-SearchResults-count",
                ".results-count",
                ".search-results-count",
                ".count-results"
            ]
            
            results_count_elem = None
            for selector in results_count_selectors:
                results_count_elem = soup.select_one(selector)
                if results_count_elem:
                    break
            
            if results_count_elem:
                count_text = results_count_elem.text.strip()
                logger.info(f"Texto del contador de resultados: {count_text}")
                # Buscar patrones como "465 ofertas de python en España" o "465 ofertas"
                count_match = re.search(r'(\d+)\s+ofertas', count_text)
                if count_match:
                    total_offers = int(count_match.group(1))
                    logger.info(f"Total de ofertas encontradas: {total_offers}")
            
            # Calcular el número total de páginas (20 ofertas por página)
            total_pages = (total_offers + 19) // 20
            logger.info(f"Total de páginas a procesar: {total_pages}")
            
            # Lista para almacenar todas las ofertas
            all_job_cards = []
            
            # Procesar cada página
            for page in range(1, total_pages + 1):
                logger.info(f"Procesando página {page} de {total_pages}")
                
                # Si no es la primera página, hacer clic en el botón "Siguiente"
                if page > 1:
                    # Buscar el botón "Siguiente" con diferentes selectores
                    next_button_selectors = [
                        "button.sui-AtomButton--primary span.sui-AtomButton-content:contains('Siguiente')",
                        "button.sui-AtomButton span.sui-AtomButton-content:contains('Siguiente')",
                        "button.sui-AtomButton--primary:contains('Siguiente')",
                        "button.sui-AtomButton:contains('Siguiente')",
                        "button:contains('Siguiente')",
                        ".sui-MoleculePagination-item button:contains('Siguiente')",
                        ".pagination button:contains('Siguiente')",
                        ".next-page button",
                        ".next button"
                    ]
                    
                    next_button = None
                    for selector in next_button_selectors:
                        logger.info(f"Intentando selector de botón siguiente: {selector}")
                        try:
                            next_button = self.wait_for_clickable(selector, timeout=5)
                            if next_button:
                                logger.info(f"Botón siguiente encontrado con selector: {selector}")
                                break
                        except Exception as e:
                            logger.info(f"No se encontró el botón siguiente con selector {selector}: {str(e)}")
                            continue
                    
                    if not next_button:
                        # Intentar encontrar el botón por texto usando XPath
                        try:
                            next_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Siguiente')]")
                            logger.info("Botón siguiente encontrado por texto")
                        except NoSuchElementException:
                            logger.error("No se encontró el botón siguiente")
                            self.take_screenshot("next_button_not_found")
                            break
                    
                    # Hacer clic en el botón "Siguiente"
                    logger.info("Haciendo clic en el botón siguiente...")
                    next_button.click()
                    
                    # Esperar a que se carguen los resultados
                    self.random_sleep(3, 5)
                    
                    # Obtener el HTML de la página
                    html = self.driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                
                # Extraer las ofertas de trabajo de la página actual
                job_cards_selectors = [
                    ".ij-OfferCardContent-description, .ij-OfferCardContent",
                    ".job-card",
                    ".offer-card",
                    ".search-result-item",
                    ".job-list-item"
                ]
                
                page_job_cards = []
                for selector in job_cards_selectors:
                    page_job_cards = soup.select(selector)
                    if page_job_cards:
                        logger.info(f"Ofertas encontradas en la página {page} con selector: {selector}")
                        break
                
                logger.info(f"Ofertas extraídas de la página {page}: {len(page_job_cards)}")
                all_job_cards.extend(page_job_cards)
            
            logger.info(f"Total de ofertas extraídas de todas las páginas: {len(all_job_cards)}")
            
            if not all_job_cards:
                logger.warning("No se encontraron ofertas de trabajo")
                return {
                    'success': True,
                    'count': 0,
                    'message': 'No se encontraron ofertas de trabajo'
                }
            
            # Guardar la búsqueda en el historial
            search_history = SearchHistory.objects.create(
                keywords=keywords,
                location=location_name,
                source='InfoJobs',
                results_count=total_offers if total_offers > 0 else len(all_job_cards)
            )
            
            jobs = []
            for i, card in enumerate(all_job_cards):
                try:
                    logger.info(f"Procesando oferta {i+1}/{len(all_job_cards)}")
                    
                    # Extraer título y enlace
                    title_selectors = [
                        ".ij-OfferCardContent-description-title-link, .ij-OfferCardContent-title-link",
                        ".job-title a",
                        ".offer-title a",
                        ".title a",
                        "h2 a",
                        "h3 a"
                    ]
                    
                    title_elem = None
                    for selector in title_selectors:
                        title_elem = card.select_one(selector)
                        if title_elem:
                            break
                    
                    if not title_elem:
                        logger.warning("No se encontró el elemento del título")
                        continue
                    
                    title = title_elem.text.strip()
                    url = title_elem.get('href', '')
                    if url.startswith('//'):
                        url = 'https:' + url
                    logger.info(f"Título: {title}")
                    logger.info(f"URL: {url}")
                    
                    # Extraer detalles adicionales de la oferta
                    details = self.extract_job_details(url)
                    
                    # Extraer empresa
                    company_selectors = [
                        ".ij-OfferCardContent-description-subtitle-link, .ij-OfferCardContent-subtitle-link",
                        ".company-name",
                        ".employer-name",
                        ".company a",
                        ".employer a"
                    ]
                    
                    company_elem = None
                    for selector in company_selectors:
                        company_elem = card.select_one(selector)
                        if company_elem:
                            break
                    
                    company = company_elem.text.strip() if company_elem else "Empresa no especificada"
                    logger.info(f"Empresa: {company}")
                    
                    # Extraer ubicación específica de la oferta
                    location_selectors = [
                        ".ij-OfferCardContent-description-location, .ij-OfferCardContent-location",
                        ".location",
                        ".job-location",
                        ".offer-location"
                    ]
                    
                    location_elem = None
                    for selector in location_selectors:
                        location_elem = card.select_one(selector)
                        if location_elem:
                            break
                    
                    job_location = location_elem.text.strip() if location_elem else location_name
                    logger.info(f"Ubicación: {job_location}")
                    
                    # Extraer fecha de publicación
                    date_selectors = [
                        ".ij-OfferCardContent-description-date, .ij-OfferCardContent-date",
                        ".date",
                        ".publication-date",
                        ".job-date",
                        ".offer-date"
                    ]
                    
                    date_elem = None
                    for selector in date_selectors:
                        date_elem = card.select_one(selector)
                        if date_elem:
                            break
                    
                    published_date = date_elem.text.strip() if date_elem else ""
                    logger.info(f"Fecha de publicación: {published_date}")
                    
                    logger.info(f"Oferta encontrada: {title} - {company} - {job_location}")
                    
                    job = JobOffer(
                        title=title,
                        company=company,
                        url=url,
                        location=job_location,
                        salary=details.get('salary', ''),
                        work_mode=details.get('work_mode', ''),
                        min_experience=details.get('min_experience', ''),
                        contract_type=details.get('contract_type', ''),
                        studies=details.get('studies', ''),
                        languages=details.get('languages', ''),
                        required_skills=details.get('required_skills', ''),
                        search_history=search_history
                    )
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Error procesando oferta: {str(e)}")
                    continue
            
            # Guardar todas las ofertas en la base de datos
            if jobs:
                JobOffer.objects.bulk_create(jobs)
                logger.info(f"Se guardaron {len(jobs)} ofertas en la base de datos")
                
                # Volver a intentar extraer los detalles de la primera oferta
                if len(jobs) > 0:
                    logger.info("Volviendo a intentar extraer los detalles de la primera oferta...")
                    first_job = jobs[0]
                    first_job_details = self.extract_job_details(first_job.url)
                    
                    if first_job_details:
                        # Actualizar los detalles de la primera oferta
                        first_job.salary = first_job_details.get('salary', first_job.salary)
                        first_job.work_mode = first_job_details.get('work_mode', first_job.work_mode)
                        first_job.min_experience = first_job_details.get('min_experience', first_job.min_experience)
                        first_job.contract_type = first_job_details.get('contract_type', first_job.contract_type)
                        first_job.studies = first_job_details.get('studies', first_job.studies)
                        first_job.languages = first_job_details.get('languages', first_job.languages)
                        first_job.required_skills = first_job_details.get('required_skills', first_job.required_skills)
                        first_job.save()
                        logger.info("Detalles de la primera oferta actualizados correctamente")
                    else:
                        logger.warning("No se pudieron extraer los detalles de la primera oferta en el segundo intento")
            else:
                logger.warning("No se guardaron ofertas en la base de datos")
            
            return {
                'success': True,
                'count': len(jobs),
                'search_id': search_history.id
            }
            
        except Exception as e:
            logger.error(f"Error en el scraping: {str(e)}")
            self.take_screenshot("unexpected_error")
            return {
                'success': False,
                'error': str(e)
            } 