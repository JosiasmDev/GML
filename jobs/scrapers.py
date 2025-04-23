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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InfoJobsScraper:
    BASE_URL = "https://www.infojobs.net"
    
    def __init__(self, headless=False, use_existing_browser=False):
        logger.info("Iniciando InfoJobsScraper...")
        logger.info(f"URL base configurada: {self.BASE_URL}")
        
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
            
            # Lista de User-Agents comunes
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
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
            published_date = ""
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
                    published_date = published_date_elem.text.strip()
                    break
            
            logger.info(f"Detalles extraídos - Salario: {salary}, Modo: {work_mode}, Exp: {min_experience}, Contrato: {contract_type}, Estudios: {studies}, Idiomas: {languages}, Habilidades: {required_skills}, Vacantes: {vacantes}, Inscritos: {inscritos}, Fecha: {published_date}")
            
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
                'published_date': published_date
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

    def search_jobs(self, keywords, location="", limit=5):
        """
        Busca ofertas de trabajo en InfoJobs
        
        Args:
            keywords (str): Palabras clave para la búsqueda
            location (str): Código de la provincia (opcional)
            limit (int): Límite de ofertas a procesar
        """
        try:
            logger.info(f"🔍 Iniciando búsqueda en InfoJobs")
            logger.info(f"📝 Palabras clave: {keywords}")
            logger.info(f"📍 Ubicación: {location}")
            logger.info(f"📊 Límite de resultados: {limit}")
            
            # Navegar a la página principal
            self.driver.get(self.BASE_URL)
            logger.info("✅ Página principal cargada")
            
            # Esperar a que cargue el formulario de búsqueda
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "keywordInput"))
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
                    EC.presence_of_element_located((By.ID, "locationInput"))
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
                    time.sleep(2)
                    
                    # Seleccionar la ubicación
                    location_select.click()
                    time.sleep(1)
                    
                    # Buscar y seleccionar la opción
                    location_option = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//option[contains(text(), '{location}')]"))
                    )
                    location_option.click()
                    logger.info(f"✅ Ubicación seleccionada: {location}")
            
            # Hacer clic en el botón de búsqueda
            try:
                search_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary"))
                )
                
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
            results_header = self.wait_for_element(By.CSS_SELECTOR, "h1.h4.h6-xs.text-center.my-4")
            if results_header:
                logger.info(f"📊 {results_header.text}")
            
            # Crear un historial de búsqueda
            search_history = SearchHistory.objects.create(
                keywords=keywords,
                location=location,
                source='InfoJobs',
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
                        job_details = self.extract_job_details(details['url'])
                        
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