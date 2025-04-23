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
from datetime import datetime, timedelta
import pyautogui
import time
import inspect
from selenium.webdriver.support.ui import Select

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InfoJobsScraper:
    BASE_URL = "https://www.infojobs.net"
    
    def __init__(self, headless=False, use_existing_browser=False):
        logger.info("=== INICIO DE INICIALIZACIÓN DE INFOJOBSSCRAPER ===")
        logger.info(f"URL base configurada: {self.BASE_URL}")
        
        try:
            if use_existing_browser:
                logger.info("Buscando ventana de Firefox existente...")
                
                # Buscar la ventana de Firefox en la barra de tareas
                logger.info("PYAUTOGUI: Buscando ventanas de Firefox...")
                firefox_windows = pyautogui.getWindowsWithTitle("firefox")
                if not firefox_windows:
                    raise Exception("No se encontró ninguna ventana de Firefox abierta")
                
                # Seleccionar la primera ventana de Firefox encontrada
                logger.info("PYAUTOGUI: Activando ventana de Firefox...")
                firefox_window = firefox_windows[0]
                firefox_window.activate()
                time.sleep(1)  # Esperar a que la ventana se active
                
                # Abrir nueva pestaña (Ctrl+T)
                logger.info("PYAUTOGUI: Abriendo nueva pestaña...")
                pyautogui.hotkey('ctrl', 't')
                time.sleep(1)  # Esperar a que se abra la pestaña
                
                # Navegar a la URL base usando pyautogui
                logger.info("PYAUTOGUI: Navegando a la URL base...")
                pyautogui.hotkey('ctrl', 'l')  # Seleccionar la barra de direcciones
                time.sleep(0.5)
                # Verificar y limpiar la URL antes de usarla
                url_to_use = self.BASE_URL.strip()
                if url_to_use.startswith("77"):
                    url_to_use = url_to_use[2:]
                logger.info(f"PYAUTOGUI: Escribiendo URL: {url_to_use}")
                pyautogui.write(url_to_use)
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2)  # Esperar a que la página cargue
                
                # Verificar la URL actual
                current_url = self.driver.current_url
                logger.info(f"URL actual después de la navegación: {current_url}")
                
                # Ahora que la pestaña está abierta y navegando, configuramos Selenium para usar la sesión existente
                logger.info("SELENIUM: Configurando opciones de Firefox...")
                firefox_options = Options()
                firefox_options.profile = webdriver.FirefoxProfile()
                
                # Configurar el servicio con la ruta específica del geckodriver
                logger.info("SELENIUM: Configurando servicio...")
                service = Service('/usr/local/bin/geckodriver')
                
                # Inicializar el driver con el perfil y el servicio
                logger.info("SELENIUM: Inicializando driver...")
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
                    
            else:
                # Configurar opciones de Firefox
                logger.info("SELENIUM: Configurando opciones de Firefox...")
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
                
                # Lista de User-Agents más realistas
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0"
                ]
                
                # Configurar el perfil de Firefox
                logger.info("SELENIUM: Configurando perfil de Firefox...")
                firefox_profile = webdriver.FirefoxProfile() if hasattr(webdriver, 'FirefoxProfile') else None
                if firefox_profile:
                    firefox_profile.set_preference("general.useragent.override", random.choice(user_agents))
                    firefox_profile.set_preference("intl.accept_languages", "es-ES,es")
                    firefox_profile.set_preference("browser.cache.disk.enable", False)
                    firefox_profile.set_preference("browser.cache.memory.enable", False)
                    firefox_profile.set_preference("browser.cache.offline.enable", False)
                    firefox_profile.set_preference("network.http.use-cache", False)
                    firefox_profile.set_preference("privacy.trackingprotection.enabled", False)
                    firefox_profile.set_preference("network.cookie.cookieBehavior", 0)
                    firefox_profile.update_preferences()
                    firefox_options.profile = firefox_profile
                
                try:
                    # Configurar el servicio con la ruta específica del geckodriver
                    logger.info("SELENIUM: Configurando servicio...")
                    service = Service('/usr/local/bin/geckodriver')
                    
                    # Inicializar el driver con el servicio
                    logger.info("SELENIUM: Inicializando driver...")
                    self.driver = webdriver.Firefox(service=service, options=firefox_options)
                    self.driver.implicitly_wait(20)
                    logger.info("Driver de Firefox inicializado correctamente")
                except WebDriverException as e:
                    logger.error(f"Error al inicializar el driver: {str(e)}")
                    raise
            
            # Verificar que el driver se haya inicializado correctamente
            if not hasattr(self, 'driver') or not self.driver:
                raise Exception("El driver de Firefox no se inicializó correctamente")
            
            logger.info("=== FIN DE INICIALIZACIÓN DE INFOJOBSSCRAPER ===")
            
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
            
        except Exception as e:
            logger.error(f"Error en la inicialización del scraper: {str(e)}")
            logger.error(f"Traceback: {inspect.trace()}")
            raise

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
        """Método vacío para mantener compatibilidad con llamadas existentes"""
        return None

    def extract_job_details(self, url):
        try:
            logger.info(f"Extrayendo detalles de la oferta: {url}")
            self.driver.get(url)
            self.random_sleep(2, 3)
            
            # Obtener el HTML de la página
            page_html = self.driver.page_source
            page_soup = BeautifulSoup(page_html, 'html.parser')
            
            # Inicializar variables para los detalles
            salary = ""
            work_mode = ""
            min_experience = ""
            contract_type = ""
            studies = ""
            languages = ""
            required_skills = ""
            vacantes = ""
            inscritos = ""
            publication_date = ""
            
            # Selectores para los detalles
            salary_selectors = [
                "dt:contains('Salario') + dd p",
                "dt:contains('Salario') + dd",
                ".salary p",
                ".salary",
                "[data-test='salary'] p",
                "[data-test='salary']",
                ".ij-OfferDetailHeader-detailsList-item p:contains('Salario')",
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='M12.18 1.334']) p"
            ]
            
            work_mode_selectors = [
                "dt:contains('Jornada') + dd p",
                "dt:contains('Jornada') + dd",
                ".work-mode p",
                ".work-mode",
                "[data-test='work-mode'] p",
                "[data-test='work-mode']",
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='m12.98 5.588']) p",
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='M9.3 9.7']) p"
            ]
            
            experience_selectors = [
                "dt:contains('Experiencia') + dd p",
                "dt:contains('Experiencia') + dd",
                ".experience p",
                ".experience",
                "[data-test='experience'] p",
                "[data-test='experience']",
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='M12.333 3.834']) p",
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='M5.833Zm8 3.333']) p"
            ]
            
            contract_selectors = [
                "dt:contains('Contrato') + dd p",
                "dt:contains('Contrato') + dd",
                ".contract p",
                ".contract",
                "[data-test='contract'] p",
                "[data-test='contract']",
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='M10.973 14.834']) p",
                ".ij-OfferDetailHeader-detailsList-item:has(svg[width='16'][height='16'] path[d*='Zm1.5-2.5V3.667']) p"
            ]
            
            studies_selectors = [
                "dt:contains('Estudios mínimos') + dd p",
                "dt:contains('Estudios mínimos') + dd",
                ".studies p",
                ".studies",
                "[data-test='studies'] p",
                "[data-test='studies']",
                ".ij-Box dt:contains('Estudios mínimos') + dd p",
                ".ij-Box dt.ij-BaseTypography:contains('Estudios mínimos') + dd p",
                ".ij-Box dt.ij-Heading-headline2:contains('Estudios mínimos') + dd p",
                ".ij-Box dt.ij-Heading-headline2.mb-s:contains('Estudios mínimos') + dd p",
                ".ij-Box dt.ij-Heading-headline2.mb-s:contains('Estudios mínimos') + dd.ij-Text-body1 p"
            ]
            
            languages_selectors = [
                "dt:contains('Idiomas') + dd p",
                "dt:contains('Idiomas') + dd",
                ".languages p",
                ".languages",
                "[data-test='languages'] p",
                "[data-test='languages']"
            ]
            
            skills_selectors = [
                "dt:contains('Conocimientos') + dd",
                "dt:contains('Requisitos') + dd",
                ".skills",
                ".requirements",
                "[data-test='skills']",
                "[data-test='requirements']"
            ]
            
            # Nuevos selectores para vacantes e inscritos
            vacantes_selectors = [
                "dt:contains('Vacantes') + dd p",
                "dt:contains('Vacantes') + dd",
                ".vacantes p",
                ".vacantes",
                "[data-test='vacantes'] p",
                "[data-test='vacantes']"
            ]
            
            inscritos_selectors = [
                "h3:contains('inscritos a esta oferta')",
                ".inscritos h3",
                "[data-test='inscritos'] h3",
                ".ij-OfferDetailFooter h3"
            ]
            
            # Intentar extraer los detalles
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
            
            # Extraer vacantes
            for selector in vacantes_selectors:
                vacantes_elem = page_soup.select_one(selector)
                if vacantes_elem:
                    vacantes = vacantes_elem.text.strip()
                    break
            
            # Extraer inscritos
            for selector in inscritos_selectors:
                inscritos_elem = page_soup.select_one(selector)
                if inscritos_elem:
                    inscritos_text = inscritos_elem.text.strip()
                    # Extraer el número de inscritos del texto
                    inscritos_match = re.search(r'(\d+)\s+inscritos', inscritos_text)
                    if inscritos_match:
                        inscritos = inscritos_match.group(1)
                    else:
                        inscritos = inscritos_text
                    break
            
            # Extraer fecha de publicación
            published_date_selectors = [
                ".ij-OfferDetailHeader-publishedAt .ij-FormatterSincedate",
                ".ij-OfferDetailHeader-publishedAt span[data-testid='sincedate-tag']",
                ".ij-OfferDetailHeader-publishedAt li",
                ".published-date",
                ".publication-date",
                ".job-date",
                ".offer-date"
            ]
            
            for selector in published_date_selectors:
                published_date_elem = page_soup.select_one(selector)
                if published_date_elem:
                    publication_date = published_date_elem.text.strip()
                    break
            
            logger.info(f"Detalles extraídos - Salario: {salary}, Modo: {work_mode}, Exp: {min_experience}, Contrato: {contract_type}, Estudios: {studies}, Idiomas: {languages}, Habilidades: {required_skills}, Vacantes: {vacantes}, Inscritos: {inscritos}, Fecha: {publication_date}")
            
            return {
                'salary': salary,
                'work_mode': work_mode,
                'min_experience': min_experience,
                'contract_type': contract_type,
                'studies': studies,
                'languages': languages,
                'required_skills': required_skills,
                'vacantes': vacantes,
                'inscritos': inscritos,
                'publication_date': publication_date
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo detalles de la oferta: {str(e)}")
            return {}

    def parse_relative_date(self, date_text):
        """
        Convierte una fecha relativa como 'Hace 5d' a un objeto datetime
        """
        if not date_text:
            return None
            
        # Patrones comunes para fechas relativas
        patterns = [
            (r'Hace (\d+) min', lambda m: timezone.now() - timedelta(minutes=int(m.group(1)))),
            (r'Hace (\d+)h', lambda m: timezone.now() - timedelta(hours=int(m.group(1)))),
            (r'Hace (\d+)d', lambda m: timezone.now() - timedelta(days=int(m.group(1)))),
            (r'Hace (\d+) sem', lambda m: timezone.now() - timedelta(weeks=int(m.group(1)))),
            (r'Hace (\d+) mes', lambda m: timezone.now() - timedelta(days=int(m.group(1))*30)),
            (r'Hace (\d+) año', lambda m: timezone.now() - timedelta(days=int(m.group(1))*365)),
            (r'(\d{1,2}) de ([a-záéíóúñ]+) de (\d{4})', lambda m: self._parse_spanish_date(m)),
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', lambda m: datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', lambda m: datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))))
        ]
        
        for pattern, converter in patterns:
            match = re.search(pattern, date_text.lower())
            if match:
                try:
                    return converter(match)
                except Exception as e:
                    logger.error(f"Error al convertir fecha '{date_text}': {str(e)}")
                    continue
        
        # Si no se pudo convertir, devolver None
        logger.warning(f"No se pudo convertir la fecha '{date_text}'")
        return None
        
    def _parse_spanish_date(self, match):
        """Convierte una fecha en formato español a datetime"""
        day = int(match.group(1))
        month_name = match.group(2).lower()
        year = int(match.group(3))
        
        # Mapeo de nombres de meses en español a números
        months = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
            'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        month = months.get(month_name)
        if not month:
            raise ValueError(f"Mes no reconocido: {month_name}")
            
        return datetime(year, month, day)

    def human_like_typing(self, element, text):
        """Simula la escritura humana en un elemento"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
            
    def human_like_click(self, element):
        """Simula un clic humano en un elemento"""
        try:
            # Intentar hacer scroll hasta el elemento
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            self.random_sleep(1, 2)
            
            # Intentar el clic normal primero
            try:
                element.click()
                return
            except:
                pass
            
            # Si el clic normal falla, usar ActionChains
            action = ActionChains(self.driver)
            action.move_to_element(element)
            action.pause(random.uniform(0.1, 0.3))
            action.click()
            action.perform()
        except Exception as e:
            logger.error(f"Error al hacer clic en el elemento: {str(e)}")
            # Intentar clic con JavaScript como último recurso
            try:
                self.driver.execute_script("arguments[0].click();", element)
            except Exception as js_error:
                logger.error(f"Error al hacer clic con JavaScript: {str(js_error)}")
                raise

    def search_jobs(self, keywords, location="0", limit=5):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Intento {retry_count + 1} de {max_retries}")
                logger.info("=== INICIO DE BÚSQUEDA DE TRABAJO ===")
                logger.info(f"Parámetros recibidos - Keywords: {keywords}, Location: {location}, Limit: {limit}")
                
                # Obtener el nombre de la ubicación del mapeo
                location_name = self.province_map.get(location, location)
                logger.info(f"Iniciando búsqueda en {location_name} (código: {location})")
                
                # Navegar a la página principal
                logger.info(f"Navegando a la página principal de InfoJobs: {self.BASE_URL}")
                self.driver.get(self.BASE_URL)
                self.random_sleep(3, 5)
                
                # Verificar que la página se haya cargado correctamente
                if not self.driver.current_url.startswith(self.BASE_URL):
                    logger.error(f"Error al cargar la página principal. URL actual: {self.driver.current_url}")
                    return {
                        'success': False,
                        'error': 'Error al cargar la página principal'
                    }
                
                logger.info("Página cargada correctamente")
                
                # Esperar a que la página se cargue completamente
                logger.info("Esperando a que la página se cargue completamente...")
                self.random_sleep(4, 6)
                
                # Verificar la URL actual
                current_url = self.driver.current_url
                logger.info(f"URL actual: {current_url}")
                
                # Manejar el botón de cookies si está presente
                logger.info("Buscando el botón de cookies...")
                try:
                    cookie_button = self.wait_for_clickable("#didomi-notice-agree-button", timeout=5)
                    if cookie_button:
                        logger.info("Botón de cookies encontrado, haciendo clic...")
                        self.human_like_click(cookie_button)
                        self.random_sleep(2, 4)
                except Exception as e:
                    logger.warning(f"No se pudo manejar el botón de cookies: {str(e)}")
                
                # Buscar el campo de búsqueda
                logger.info("Buscando el campo de búsqueda...")
                try:
                    search_input = self.wait_for_element("input[name='palabra']", timeout=10)
                    if not search_input:
                        logger.error("No se encontró el campo de búsqueda")
                        return {
                            'success': False,
                            'error': 'No se encontró el campo de búsqueda'
                        }
                    
                    # Limpiar el campo de búsqueda y escribir las palabras clave
                    logger.info(f"Escribiendo palabras clave: {keywords}")
                    search_input.clear()
                    self.human_like_typing(search_input, keywords)
                    self.random_sleep(2, 4)
                except Exception as e:
                    logger.error(f"Error al manejar el campo de búsqueda: {str(e)}")
                    return {
                        'success': False,
                        'error': f'Error al manejar el campo de búsqueda: {str(e)}'
                    }
                
                # Buscar y manejar el selector de ubicación
                logger.info("Buscando el selector de ubicación...")
                try:
                    location_select = self.wait_for_element("select#of_provincia", timeout=10)
                    if location_select:
                        # Obtener el código de la provincia del mapeo
                        province_code = None
                        for code, name in self.province_map.items():
                            if name == location:
                                province_code = code
                                break
                        
                        if province_code:
                            logger.info(f"Seleccionando ubicación: {location} (código: {province_code})")
                            
                            # Intentar seleccionar la ubicación usando JavaScript
                            self.driver.execute_script(f"document.getElementById('of_provincia').value = '{province_code}';")
                            self.driver.execute_script("document.getElementById('of_provincia').dispatchEvent(new Event('change'));")
                            self.random_sleep(2, 4)
                            
                            # Verificar que la ubicación se haya seleccionado correctamente
                            selected_location = self.driver.find_element(By.CSS_SELECTOR, "#of_provincia_chosen .chosen-single span").text
                            logger.info(f"Ubicación seleccionada: {selected_location}")
                            
                            if selected_location != location:
                                logger.warning(f"La ubicación seleccionada ({selected_location}) no coincide con la solicitada ({location})")
                                # Intentar seleccionar la ubicación usando el índice
                                try:
                                    select = Select(location_select)
                                    # Obtener todas las opciones
                                    options = select.options
                                    # Buscar la opción que coincida con la ubicación
                                    for option in options:
                                        if option.text.strip() == location:
                                            select.select_by_visible_text(location)
                                            self.random_sleep(2, 4)
                                            break
                                except Exception as e:
                                    logger.error(f"Error al seleccionar la ubicación por texto: {str(e)}")
                        else:
                            logger.warning(f"No se encontró el código para la ubicación: {location}")
                    else:
                        logger.warning("No se encontró el selector de ubicación, continuando sin filtrar por ubicación")
                except Exception as e:
                    logger.error(f"Error al manejar el selector de ubicación: {str(e)}")
                    # Continuar con la búsqueda incluso si falla la selección de ubicación
                
                # Buscar el botón de búsqueda
                logger.info("Buscando el botón de búsqueda...")
                try:
                    search_button = self.wait_for_clickable("button[type='submit']", timeout=10)
                    if not search_button:
                        logger.error("No se encontró el botón de búsqueda")
                        return {
                            'success': False,
                            'error': 'No se encontró el botón de búsqueda'
                        }
                    
                    # Hacer clic en el botón de búsqueda
                    logger.info("Haciendo clic en el botón de búsqueda...")
                    self.human_like_click(search_button)
                    
                    # Esperar a que se carguen los resultados
                    logger.info("Esperando a que se carguen los resultados...")
                    self.random_sleep(4, 6)
                    
                    # Verificar la URL después de la búsqueda
                    current_url = self.driver.current_url
                    logger.info(f"URL después de la búsqueda: {current_url}")
                    
                    # Verificar el contenido de la página
                    page_source = self.driver.page_source
                    logger.info("Verificando el contenido de la página...")
                    
                    # Buscar elementos clave en la página
                    try:
                        results_overview = self.driver.find_element(By.CSS_SELECTOR, ".ij-ResultsOverview")
                        if results_overview:
                            logger.info(f"Se encontró el contenedor de resultados: {results_overview.text}")
                    except:
                        logger.warning("No se encontró el contenedor de resultados")
                    
                    try:
                        job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".ij-OfferCard")
                        logger.info(f"Se encontraron {len(job_cards)} ofertas en la página")
                    except:
                        logger.warning("No se encontraron ofertas en la página")
                    
                    # Si llegamos aquí, continuamos con el procesamiento
                    # Obtener el HTML de la página
                    html = self.driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extraer el número total de ofertas
                    total_offers = 0
                    results_count_elem = soup.select_one(".ij-ResultsOverview")
                    if results_count_elem:
                        count_text = results_count_elem.text.strip()
                        logger.info(f"Texto del contador de resultados: {count_text}")
                        count_match = re.search(r'(\d+)\s+ofertas', count_text)
                        if count_match:
                            total_offers = int(count_match.group(1))
                            logger.info(f"Total de ofertas encontradas: {total_offers}")
                
                    # Crear un historial de búsqueda
                    search_history = SearchHistory.objects.create(
                        keywords=keywords,
                        location=location_name,
                        source='InfoJobs',
                        results_count=total_offers
                    )
                    
                    # Extraer las ofertas de la página
                    jobs_to_create = []
                    jobs_to_update = []
                    
                    job_cards = soup.select('.ij-OfferCard, .ij-OfferCardContent-description, .ij-OfferCardContent, .job-card, .offer-card, .search-result-item, .job-list-item')
                    logger.info(f"Ofertas encontradas en la página: {len(job_cards)}")
                    
                    for card in job_cards:
                        try:
                            # Extraer título y URL
                            title_elem = card.select_one('.ij-OfferCardContent-description-title-link, .ij-OfferCardContent-title-link, .job-title a, .offer-title a, .title a, h2 a, h3 a')
                            if not title_elem:
                                continue
                            
                            title = title_elem.text.strip()
                            url = title_elem.get('href', '')
                            if url.startswith('//'):
                                url = 'https:' + url
                            
                            # Extraer empresa
                            company_elem = card.select_one('.ij-OfferCardContent-description-subtitle-link, .ij-OfferCardContent-subtitle-link, .company-name, .employer-name, .company a, .employer a')
                            company = company_elem.text.strip() if company_elem else "Empresa no especificada"
                            
                            # Extraer ubicación
                            location_elem = card.select_one('.ij-OfferCardContent-description-location, .ij-OfferCardContent-location, .location, .job-location, .offer-location')
                            job_location = location_elem.text.strip() if location_elem else location_name
                            
                            # Extraer detalles de la oferta
                            logger.info(f"Extrayendo detalles de la oferta: {title}")
                            job_details = self.extract_job_details(url)
                            
                            # Verificar si la oferta ya existe
                            existing_job = JobOffer.objects.filter(url=url).first()
                            if existing_job:
                                # Actualizar la oferta existente
                                existing_job.title = title
                                existing_job.company = company
                                existing_job.location = job_location
                                existing_job.search_history = search_history
                                # Actualizar los detalles
                                for key, value in job_details.items():
                                    setattr(existing_job, key, value)
                                jobs_to_update.append(existing_job)
                                logger.info(f"✅ Oferta existente actualizada: {title} en {company}")
                            else:
                                # Crear nueva oferta
                                job = JobOffer(
                                    title=title,
                                    company=company,
                                    location=job_location,
                                    url=url,
                                    search_history=search_history,
                                    **job_details
                                )
                                jobs_to_create.append(job)
                                logger.info(f"✅ Nueva oferta creada: {title} en {company}")
                            
                        except Exception as e:
                            logger.error(f"Error procesando oferta: {str(e)}")
                            continue
                    
                    # Guardar las ofertas en la base de datos
                    if jobs_to_create:
                        JobOffer.objects.bulk_create(jobs_to_create)
                        logger.info(f"✅ Se guardaron {len(jobs_to_create)} nuevas ofertas en la base de datos")
                    
                    if jobs_to_update:
                        for job in jobs_to_update:
                            job.save()
                        logger.info(f"✅ Se actualizaron {len(jobs_to_update)} ofertas existentes")
                    
                    logger.info("=== FIN DE BÚSQUEDA DE TRABAJO ===")
                    return {
                        'success': True,
                        'count': len(jobs_to_create) + len(jobs_to_update),
                        'search_id': search_history.id
                    }
                    
                except Exception as e:
                    logger.error(f"Error al manejar el botón de búsqueda: {str(e)}")
                    return {
                        'success': False,
                        'error': f'Error al manejar el botón de búsqueda: {str(e)}'
                    }
                
            except Exception as e:
                logger.error(f"Error en el scraping: {str(e)}")
                logger.error(f"Traceback: {inspect.trace()}")
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Reintentando en {retry_count * 5} segundos...")
                    time.sleep(retry_count * 5)
                    continue
                else:
                    return {
                        'success': False,
                        'error': str(e)
                    } 