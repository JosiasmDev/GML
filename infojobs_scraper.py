"""
Infojobs Scraper - A modern web scraper for Infojobs.net
This module provides functionality to scrape job offers from Infojobs.net
"""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote
import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

# Importar el modelo de Django
from jobs.models import JobOffer

class InfojobsScraper:
    """Main class for scraping Infojobs.net"""
    
    BASE_URL = "https://www.infojobs.net/ofertas-trabajo"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self, headless: bool = False):
        """
        Initialize the scraper
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
        """
        self.driver = self._setup_driver(headless)
        
    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """Setup and configure Chrome WebDriver"""
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        options.add_argument(f'user-agent={self.HEADERS["User-Agent"]}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10)
        return driver

    def search_jobs(self, keywords: str, wait_for_captcha: bool = True) -> List[str]:
        """
        Search for jobs using keywords and return list of job URLs
        
        Args:
            keywords (str): Search keywords
            wait_for_captcha (bool): Whether to wait for manual captcha resolution
            
        Returns:
            List[str]: List of job offer URLs
        """
        try:
            # Usar la URL correcta de búsqueda
            search_url = f"https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword={quote(keywords)}"
            print(f"Accediendo a: {search_url}")
            self.driver.get(search_url)
            
            # Esperar a que la página cargue
            time.sleep(5)
            
            if wait_for_captcha:
                input("Por favor, resuelve el captcha y aplica los filtros deseados. Presiona Enter cuando hayas terminado...")
            
            # Get the filtered URL after captcha resolution
            filtered_url = self.driver.current_url
            print(f"URL después de filtros: {filtered_url}")
            
            # Scroll to load all results
            self._scroll_page()
            
            # Get total number of results
            total_results = self._get_total_results()
            # Limitar a 2 páginas (40 ofertas, ya que cada página tiene 20 ofertas)
            total_pages = min(2, (total_results // 20) + 1)
            
            print(f"\nSe encontraron {total_results} ofertas de trabajo")
            print(f"Se escanearán las primeras {total_pages * 20} ofertas")
            
            # Collect all job URLs
            all_urls = self._get_job_urls_from_page()
            print(f"URLs encontradas en la primera página: {len(all_urls)}")
            
            # Si no se encontraron URLs en la primera página, intentar un enfoque diferente
            if not all_urls:
                print("No se encontraron URLs en la primera página. Intentando un enfoque diferente...")
                # Intentar hacer clic en los enlaces de ofertas directamente
                try:
                    # Buscar todos los enlaces de ofertas
                    offer_links = self.driver.find_elements(By.CSS_SELECTOR, "a.ij-OfferCardContent-description-title-link")
                    print(f"Enlaces encontrados directamente: {len(offer_links)}")
                    
                    # Extraer las URLs
                    for link in offer_links:
                        try:
                            href = link.get_attribute("href")
                            if href and href not in all_urls:
                                all_urls.append(href)
                        except:
                            continue
                    
                    print(f"URLs encontradas con el enfoque alternativo: {len(all_urls)}")
                except Exception as e:
                    print(f"Error al intentar el enfoque alternativo: {str(e)}")
            
            # Scrape remaining pages
            for page in tqdm(range(2, total_pages + 1), desc="Escaneando páginas"):
                try:
                    # Construir la URL de la página correctamente
                    if "page=" in filtered_url:
                        page_url = re.sub(r'page=\d+', f'page={page}', filtered_url)
                    else:
                        page_url = f"{filtered_url}&page={page}"
                    
                    print(f"\nAccediendo a página {page}: {page_url}")
                    self.driver.get(page_url)
                    
                    # Esperar a que la página cargue
                    time.sleep(5)
                    
                    # Scroll to load all results
                    self._scroll_page()
                    
                    # Obtener URLs de esta página
                    page_urls = self._get_job_urls_from_page()
                    print(f"URLs encontradas en la página {page}: {len(page_urls)}")
                    
                    # Añadir URLs a la lista total
                    all_urls.extend(page_urls)
                    
                    # Eliminar duplicados
                    all_urls = list(set(all_urls))
                    
                    # Esperar un poco antes de continuar
                    time.sleep(2)
                except Exception as e:
                    print(f"Error al procesar la página {page}: {str(e)}")
                    continue
            
            print(f"\nTotal de URLs únicas encontradas: {len(all_urls)}")
            return all_urls
            
        except Exception as e:
            print(f"Error durante la búsqueda de trabajos: {str(e)}")
            return []

    def _scroll_page(self):
        """Scroll the page to load all content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _get_total_results(self) -> int:
        """Get total number of search results"""
        try:
            # Esperar a que la página cargue completamente
            time.sleep(5)
            
            # Intentar encontrar el elemento con el número de resultados
            try:
                # Intentar con diferentes selectores
                selectors = [
                    "div.ij-ResultsOverview",
                    "div.ij-ResultsOverview-text",
                    "div.ij-ResultsOverview-count",
                    "div.ij-ResultsOverview-title",
                    "div.ij-ResultsOverview-description"
                ]
                
                for selector in selectors:
                    try:
                        results_elem = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        results_text = results_elem.text
                        print(f"Texto encontrado con selector '{selector}': {results_text}")
                        
                        # Extraer el número de resultados
                        match = re.search(r'(\d+)', results_text)
                        if match:
                            return int(match.group(1))
                    except:
                        continue
                
                # Si no se encontró con los selectores, intentar con JavaScript
                try:
                    # Intentar obtener el número de resultados con JavaScript
                    results_text = self.driver.execute_script(
                        "return document.querySelector('div.ij-ResultsOverview, div.ij-ResultsOverview-text, div.ij-ResultsOverview-count, div.ij-ResultsOverview-title, div.ij-ResultsOverview-description').textContent;"
                    )
                    print(f"Texto encontrado con JavaScript: {results_text}")
                    
                    # Extraer el número de resultados
                    match = re.search(r'(\d+)', results_text)
                    if match:
                        return int(match.group(1))
                except:
                    pass
                
            except Exception as e:
                print(f"Error al buscar el elemento con el número de resultados: {str(e)}")
            
            # Si no se encontró con Selenium, intentar con BeautifulSoup
            try:
                # Buscar el texto que contiene el número de resultados
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")
                
                # Intentar con diferentes selectores
                selectors = [
                    "div.ij-ResultsOverview",
                    "div.ij-ResultsOverview-text",
                    "div.ij-ResultsOverview-count",
                    "div.ij-ResultsOverview-title",
                    "div.ij-ResultsOverview-description"
                ]
                
                for selector in selectors:
                    results_elem = soup.select_one(selector)
                    if results_elem:
                        results_text = results_elem.text
                        print(f"Texto encontrado con BeautifulSoup y selector '{selector}': {results_text}")
                        
                        # Extraer el número de resultados
                        match = re.search(r'(\d+)', results_text)
                        if match:
                            return int(match.group(1))
                
                # Si no se encontró con los selectores, buscar cualquier texto que contenga un número seguido de "ofertas"
                for elem in soup.find_all(text=re.compile(r'\d+\s+ofertas')):
                    match = re.search(r'(\d+)', elem)
                    if match:
                        return int(match.group(1))
                
            except Exception as e:
                print(f"Error al intentar el método alternativo: {str(e)}")
            
            # Si todo falla, contar los elementos de ofertas de trabajo
            try:
                offer_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.ij-OfferCardContent")
                count = len(offer_elements)
                print(f"Contando elementos de ofertas directamente: {count}")
                if count > 0:
                    return count * 25  # Estimación basada en el número de ofertas visibles
            except:
                pass
            
            print("No se pudo determinar el número total de resultados. Usando valor por defecto.")
            return 20  # Valor por defecto
            
        except Exception as e:
            print(f"Error al obtener el número total de resultados: {str(e)}")
            return 20  # Valor por defecto

    def _get_job_urls_from_page(self) -> List[str]:
        """Get all job offer URLs from the current page"""
        try:
            # Esperar a que la página cargue completamente
            time.sleep(5)
            
            # Obtener el HTML de la página
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            
            # Lista para almacenar las URLs encontradas
            job_urls = []
            
            # Método 1: Buscar todos los enlaces de ofertas de trabajo usando el selector correcto
            # Basado en la estructura actual de Infojobs
            offer_links = soup.select("a.ij-OfferCardContent-description-title-link")
            print(f"Enlaces encontrados con selector 'a.ij-OfferCardContent-description-title-link': {len(offer_links)}")
            
            # Extraer las URLs
            for link in offer_links:
                href = link.get("href", "")
                if href:
                    # Asegurarse de que la URL es absoluta
                    if href.startswith("//"):
                        href = "https:" + href
                    elif not href.startswith("http"):
                        href = "https://www.infojobs.net" + href
                    
                    # Añadir la URL si no está ya en la lista
                    if href not in job_urls:
                        job_urls.append(href)
            
            # Método 2: Si no se encontraron URLs con el selector principal, intentar con otros selectores
            if not job_urls:
                print("Intentando con otros selectores para encontrar URLs...")
                selectors = [
                    "a.ij-OfferCardContent-description-title-link",
                    "a.ij-OfferCardContent-description-title",
                    "a.ij-OfferCardContent-description-link",
                    "a.ij-OfferCardContent-link",
                    "a[href*='/of-i']"
                ]
                
                for selector in selectors:
                    offer_links = soup.select(selector)
                    print(f"Enlaces encontrados con selector '{selector}': {len(offer_links)}")
                    
                    for link in offer_links:
                        href = link.get("href", "")
                        if href and "/of-i" in href and href not in job_urls:
                            # Asegurarse de que la URL es absoluta
                            if href.startswith("//"):
                                href = "https:" + href
                            elif not href.startswith("http"):
                                href = "https://www.infojobs.net" + href
                            job_urls.append(href)
            
            # Método 3: Si aún no se encontraron URLs, buscar todos los enlaces en la página
            if not job_urls:
                print("Intentando método alternativo para encontrar URLs...")
                # Buscar todos los enlaces en la página
                all_links = soup.find_all("a", href=True)
                
                # Filtrar solo las URLs de ofertas de trabajo
                for link in all_links:
                    href = link.get("href", "")
                    if "/of-i" in href and href not in job_urls:
                        # Asegurarse de que la URL es absoluta
                        if href.startswith("//"):
                            href = "https:" + href
                        elif not href.startswith("http"):
                            href = "https://www.infojobs.net" + href
                        job_urls.append(href)
            
            # Método 4: Usar Selenium directamente para encontrar los enlaces
            if not job_urls:
                print("Intentando encontrar enlaces con Selenium directamente...")
                try:
                    # Buscar todos los enlaces de ofertas
                    offer_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/of-i']")
                    print(f"Enlaces encontrados con Selenium: {len(offer_links)}")
                    
                    # Extraer las URLs
                    for link in offer_links:
                        try:
                            href = link.get_attribute("href")
                            if href and href not in job_urls:
                                job_urls.append(href)
                        except:
                            continue
                except Exception as e:
                    print(f"Error al intentar encontrar enlaces con Selenium: {str(e)}")
            
            print(f"Se encontraron {len(job_urls)} URLs de ofertas de trabajo")
            return job_urls
            
        except Exception as e:
            print(f"Error al obtener URLs de la página: {str(e)}")
            return []

    def scrape_job_details(self, url: str) -> Dict:
        """
        Scrape details from a single job offer
        
        Args:
            url (str): URL of the job offer
            
        Returns:
            Dict: Job offer details
        """
        try:
            print(f"\nEscaneando detalles de: {url}")
            
            # Usar Selenium en lugar de requests para cargar la página
            self.driver.get(url)
            time.sleep(5)  # Esperar a que la página cargue
            
            # Obtener el HTML de la página
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Inicializar diccionario para almacenar los detalles
            job_info = {}
            
            # Extraer título del trabajo
            title_elem = soup.select_one("h1.ij-OfferHeader-title")
            if title_elem:
                job_info["position"] = title_elem.text.strip()
                # Limitar la longitud del título a 200 caracteres
                if len(job_info["position"]) > 200:
                    job_info["position"] = job_info["position"][:197] + "..."
            else:
                # Intentar con selectores alternativos
                title_elem = soup.select_one("h1.ij-OfferHeader-title-text")
                if title_elem:
                    job_info["position"] = title_elem.text.strip()
                    if len(job_info["position"]) > 200:
                        job_info["position"] = job_info["position"][:197] + "..."
                else:
                    job_info["position"] = "N/A"
            
            print(f"Puesto: {job_info['position']}")
            
            # Extraer nombre de la empresa
            company_elem = soup.select_one("a.ij-OfferHeader-companyName")
            if company_elem:
                job_info["company"] = company_elem.text.strip()
                # Limitar la longitud del nombre de la empresa a 200 caracteres
                if len(job_info["company"]) > 200:
                    job_info["company"] = job_info["company"][:197] + "..."
            else:
                # Intentar con selectores alternativos
                company_elem = soup.select_one("div.ij-OfferHeader-companyName")
                if company_elem:
                    job_info["company"] = company_elem.text.strip()
                    if len(job_info["company"]) > 200:
                        job_info["company"] = job_info["company"][:197] + "..."
                else:
                    job_info["company"] = "N/A"
            
            print(f"Empresa: {job_info['company']}")
            
            # Extraer valoración de la empresa
            company_valuation_elem = soup.select_one("div.ij-OfferHeader-companyRating")
            if company_valuation_elem:
                rating_text = company_valuation_elem.text.strip()
                match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                if match:
                    job_info["company_valuation"] = float(match.group(1))
                else:
                    job_info["company_valuation"] = None
            else:
                job_info["company_valuation"] = None
            print(f"Valoración empresa: {job_info['company_valuation']}")
            
            # Extraer ubicación
            location_elem = soup.select_one("div.ij-OfferHeader-location")
            if location_elem:
                location_text = location_elem.text.strip()
                # Separar ciudad y país si es posible
                parts = location_text.split(',')
                job_info["city"] = parts[0].strip() if parts else "N/A"
                # Limitar la longitud de la ciudad a 200 caracteres
                if len(job_info["city"]) > 200:
                    job_info["city"] = job_info["city"][:197] + "..."
                
                job_info["country"] = parts[1].strip() if len(parts) > 1 else "España"
                # Limitar la longitud del país a 200 caracteres
                if len(job_info["country"]) > 200:
                    job_info["country"] = job_info["country"][:197] + "..."
            else:
                job_info["city"] = "N/A"
                job_info["country"] = "España"
            print(f"Ciudad: {job_info['city']}")
            print(f"País: {job_info['country']}")
            
            # Extraer modalidad de trabajo (presencial, híbrido, teletrabajo)
            work_mode_text = ""
            work_mode_elements = soup.select("div.ij-OfferHeader-detailsList-item")
            for elem in work_mode_elements:
                text = elem.text.strip().lower()
                if "teletrabajo" in text or "remoto" in text:
                    work_mode_text = "Teletrabajo"
                    break
                elif "híbrido" in text:
                    work_mode_text = "Híbrido"
                    break
                elif "presencial" in text:
                    work_mode_text = "Presencial"
                    break
            
            job_info["work_mode"] = work_mode_text if work_mode_text else "N/A"
            print(f"Modalidad de trabajo: {job_info['work_mode']}")
            
            # Extraer tipo de contrato
            contract_elem = soup.select_one("div.ij-OfferHeader-contractType")
            if contract_elem:
                job_info["contract_type"] = contract_elem.text.strip()
                # Limitar la longitud del tipo de contrato a 200 caracteres
                if len(job_info["contract_type"]) > 200:
                    job_info["contract_type"] = job_info["contract_type"][:197] + "..."
            else:
                # Intentar con selectores alternativos
                contract_elem = soup.select_one("div.ij-OfferHeader-contractType-text")
                if contract_elem:
                    job_info["contract_type"] = contract_elem.text.strip()
                    if len(job_info["contract_type"]) > 200:
                        job_info["contract_type"] = job_info["contract_type"][:197] + "..."
                else:
                    job_info["contract_type"] = "N/A"
            
            print(f"Tipo de contrato: {job_info['contract_type']}")
            
            # Extraer salario
            salary_elem = soup.select_one("div.ij-OfferHeader-salary")
            if salary_elem:
                job_info["salary"] = salary_elem.text.strip()
                # Limitar la longitud del salario a 200 caracteres
                if len(job_info["salary"]) > 200:
                    job_info["salary"] = job_info["salary"][:197] + "..."
            else:
                # Intentar con selectores alternativos
                salary_elem = soup.select_one("div.ij-OfferHeader-salary-text")
                if salary_elem:
                    job_info["salary"] = salary_elem.text.strip()
                    if len(job_info["salary"]) > 200:
                        job_info["salary"] = job_info["salary"][:197] + "..."
                else:
                    job_info["salary"] = "N/A"
            
            print(f"Salario: {job_info['salary']}")
            
            # Extraer experiencia mínima
            exp_elem = soup.select_one("div.ij-OfferHeader-experience")
            if exp_elem:
                job_info["min_exp"] = exp_elem.text.strip()
                # Limitar la longitud de la experiencia mínima a 200 caracteres
                if len(job_info["min_exp"]) > 200:
                    job_info["min_exp"] = job_info["min_exp"][:197] + "..."
            else:
                # Intentar con selectores alternativos
                exp_elem = soup.select_one("div.ij-OfferHeader-experience-text")
                if exp_elem:
                    job_info["min_exp"] = exp_elem.text.strip()
                    if len(job_info["min_exp"]) > 200:
                        job_info["min_exp"] = job_info["min_exp"][:197] + "..."
                else:
                    job_info["min_exp"] = "N/A"
            
            print(f"Experiencia mínima: {job_info['min_exp']}")
            
            # Extraer estudios mínimos
            education_elem = soup.select_one("div.ij-OfferHeader-education")
            if education_elem:
                job_info["min_education"] = education_elem.text.strip()
                # Limitar la longitud de los estudios mínimos a 200 caracteres
                if len(job_info["min_education"]) > 200:
                    job_info["min_education"] = job_info["min_education"][:197] + "..."
            else:
                # Intentar con selectores alternativos
                education_elem = soup.select_one("div.ij-OfferHeader-education-text")
                if education_elem:
                    job_info["min_education"] = education_elem.text.strip()
                    if len(job_info["min_education"]) > 200:
                        job_info["min_education"] = job_info["min_education"][:197] + "..."
                else:
                    job_info["min_education"] = "N/A"
            
            print(f"Estudios mínimos: {job_info['min_education']}")
            
            # Extraer tipo de industria
            industry_elem = soup.select_one("div.ij-OfferHeader-industry")
            if industry_elem:
                job_info["industry"] = industry_elem.text.strip()
                # Limitar la longitud de la industria a 200 caracteres
                if len(job_info["industry"]) > 200:
                    job_info["industry"] = job_info["industry"][:197] + "..."
            else:
                # Intentar con selectores alternativos
                industry_elem = soup.select_one("div.ij-OfferHeader-industry-text")
                if industry_elem:
                    job_info["industry"] = industry_elem.text.strip()
                    if len(job_info["industry"]) > 200:
                        job_info["industry"] = job_info["industry"][:197] + "..."
                else:
                    job_info["industry"] = "N/A"
            
            print(f"Tipo de industria: {job_info['industry']}")
            
            # Extraer categoría
            category_elem = soup.select_one("div.ij-OfferHeader-category")
            if category_elem:
                job_info["category"] = category_elem.text.strip()
                # Limitar la longitud de la categoría a 200 caracteres
                if len(job_info["category"]) > 200:
                    job_info["category"] = job_info["category"][:197] + "..."
            else:
                # Intentar con selectores alternativos
                category_elem = soup.select_one("div.ij-OfferHeader-category-text")
                if category_elem:
                    job_info["category"] = category_elem.text.strip()
                    if len(job_info["category"]) > 200:
                        job_info["category"] = job_info["category"][:197] + "..."
                else:
                    job_info["category"] = "N/A"
            
            print(f"Categoría: {job_info['category']}")
            
            # Extraer nivel
            level_elem = soup.select_one("div.ij-OfferHeader-level")
            if level_elem:
                job_info["level"] = level_elem.text.strip()
                # Limitar la longitud del nivel a 200 caracteres
                if len(job_info["level"]) > 200:
                    job_info["level"] = job_info["level"][:197] + "..."
            else:
                # Intentar con selectores alternativos
                level_elem = soup.select_one("div.ij-OfferHeader-level-text")
                if level_elem:
                    job_info["level"] = level_elem.text.strip()
                    if len(job_info["level"]) > 200:
                        job_info["level"] = job_info["level"][:197] + "..."
                else:
                    job_info["level"] = "N/A"
            
            print(f"Nivel: {job_info['level']}")
            
            # Extraer número de vacantes
            vacancies_elem = soup.select_one("div.ij-OfferHeader-vacancies")
            if vacancies_elem:
                vacancies_text = vacancies_elem.text.strip()
                match = re.search(r'(\d+)', vacancies_text)
                if match:
                    job_info["vacancies"] = int(match.group(1))
                else:
                    job_info["vacancies"] = 1
            else:
                job_info["vacancies"] = 1
            
            print(f"Número de vacantes: {job_info['vacancies']}")
            
            # Extraer número de inscritos
            applicants_elem = soup.select_one("div.ij-OfferHeader-applicants")
            if applicants_elem:
                applicants_text = applicants_elem.text.strip()
                match = re.search(r'(\d+)', applicants_text)
                if match:
                    job_info["applicants"] = int(match.group(1))
                else:
                    job_info["applicants"] = 0
            else:
                job_info["applicants"] = 0
            
            print(f"Número de inscritos: {job_info['applicants']}")
            
            # Extraer descripción, requisitos, funciones y condiciones
            description_section = soup.select_one("div.ij-OfferBody")
            if description_section:
                # Descripción
                desc_elem = description_section.select_one("div.ij-OfferBody-description")
                if desc_elem:
                    job_info["description"] = desc_elem.text.strip()
                else:
                    job_info["description"] = ""
                
                # Requisitos
                req_elem = description_section.select_one("div.ij-OfferBody-requirements")
                if req_elem:
                    job_info["requirements"] = req_elem.text.strip()
                else:
                    job_info["requirements"] = ""
                
                # Funciones
                func_elem = description_section.select_one("div.ij-OfferBody-functions")
                if func_elem:
                    job_info["functions"] = func_elem.text.strip()
                else:
                    job_info["functions"] = ""
                
                # Condiciones
                cond_elem = description_section.select_one("div.ij-OfferBody-conditions")
                if cond_elem:
                    job_info["conditions"] = cond_elem.text.strip()
                else:
                    job_info["conditions"] = ""
                
                # Beneficios
                benefits_elem = description_section.select_one("div.ij-OfferBody-benefits")
                if benefits_elem:
                    job_info["benefits"] = benefits_elem.text.strip()
                else:
                    job_info["benefits"] = ""
            else:
                job_info["description"] = ""
                job_info["requirements"] = ""
                job_info["functions"] = ""
                job_info["conditions"] = ""
                job_info["benefits"] = ""
            
            # URL
            job_info["url"] = url
            # Limitar la longitud de la URL a 200 caracteres
            if len(job_info["url"]) > 200:
                job_info["url"] = job_info["url"][:197] + "..."
            
            return job_info
            
        except Exception as e:
            print(f"Error al escanear {url}: {str(e)}")
            return {}

    def scrape_jobs(self, keywords: str) -> int:
        """
        Main method to scrape jobs and save results to database
        
        Args:
            keywords (str): Search keywords
            
        Returns:
            int: Number of job offers saved to database
        """
        try:
            # Buscar trabajos
            job_urls = self.search_jobs(keywords)
            print(f"\nSe encontraron {len(job_urls)} ofertas de trabajo para escanear")
            
            if not job_urls:
                print("No se encontraron URLs de ofertas para escanear. Verifica la búsqueda o los filtros aplicados.")
                return 0
            
            # Escanear detalles de los trabajos
            jobs_saved = 0
            for url in tqdm(job_urls, desc="Escaneando detalles de ofertas"):
                try:
                    job_info = self.scrape_job_details(url)
                    if job_info:
                        # Verificar si la oferta ya existe en la base de datos
                        existing_job = JobOffer.objects.filter(url=job_info["url"]).first()
                        
                        if not existing_job:
                            # Crear un nuevo objeto JobOffer
                            job_offer = JobOffer(
                                position=job_info["position"],
                                company=job_info["company"],
                                company_valuation=job_info["company_valuation"],
                                city=job_info["city"],
                                country=job_info["country"],
                                work_mode=job_info["work_mode"],
                                contract_type=job_info["contract_type"],
                                salary=job_info["salary"],
                                min_exp=job_info["min_exp"],
                                min_education=job_info["min_education"],
                                description=job_info["description"],
                                requirements=job_info["requirements"],
                                functions=job_info["functions"],
                                conditions=job_info["conditions"],
                                industry=job_info["industry"],
                                category=job_info["category"],
                                level=job_info["level"],
                                vacancies=job_info["vacancies"],
                                applicants=job_info["applicants"],
                                benefits=job_info["benefits"],
                                url=job_info["url"]
                            )
                            
                            # Guardar en la base de datos
                            job_offer.save()
                            jobs_saved += 1
                            print(f"Oferta guardada: {job_info['position']} en {job_info['company']}")
                        else:
                            print(f"Oferta ya existe en la base de datos: {job_info['position']} en {job_info['company']}")
                    else:
                        print(f"No se pudieron extraer detalles de la oferta: {url}")
                    
                    # Esperar un poco antes de continuar
                    time.sleep(1)
                except Exception as e:
                    print(f"Error al procesar la oferta {url}: {str(e)}")
                    continue
            
            print(f"\nSe guardaron {jobs_saved} ofertas de trabajo en la base de datos")
            return jobs_saved
                
        except Exception as e:
            print(f"Error durante el escaneo: {str(e)}")
            return 0
            
        finally:
            self.driver.quit()

def main():
    """Main function to run the scraper"""
    print("Infojobs Scraper")
    print("===============")
    
    keywords = input("\nIntroduce palabras clave para buscar (por defecto: 'Data Scientist'): ").strip() or "Data Scientist"
    
    scraper = InfojobsScraper(headless=False)
    scraper.scrape_jobs(keywords)

if __name__ == "__main__":
    main() 