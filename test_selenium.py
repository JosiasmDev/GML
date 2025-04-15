from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument('--headless')  # Quitar esta línea si querés ver el navegador

service = Service("/usr/local/bin/geckodriver")  # Ruta explícita al driver

try:
    driver = webdriver.Firefox(service=service, options=options)
    driver.get("https://www.python.org")
    print("Título de la página:", driver.title)
    driver.quit()
except Exception as e:
    print("Error lanzando Firefox:", e)
