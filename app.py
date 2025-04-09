"""
Aplicación web para mostrar las ofertas de trabajo de Infojobs
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from models import get_session, JobOffer, init_db
from infojobs_scraper import InfojobsScraper
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inicializar la base de datos
init_db()

@app.route('/')
def index():
    """Página principal que muestra las ofertas de trabajo"""
    session = get_session()
    # Obtener todas las ofertas de trabajo ordenadas por fecha de creación
    job_offers = session.query(JobOffer).order_by(JobOffer.created_at.desc()).all()
    session.close()
    return render_template('index.html', job_offers=job_offers)

@app.route('/search', methods=['POST'])
def search():
    """Buscar ofertas de trabajo con palabras clave"""
    keywords = request.form.get('keywords', '')
    if not keywords:
        flash('Por favor, introduce palabras clave para buscar', 'error')
        return redirect(url_for('index'))
    
    # Iniciar el scraper
    scraper = InfojobsScraper(headless=False)
    jobs_saved = scraper.scrape_jobs(keywords)
    
    if jobs_saved > 0:
        flash(f'Se encontraron y guardaron {jobs_saved} ofertas de trabajo', 'success')
    else:
        flash('No se encontraron ofertas de trabajo o hubo un error durante el escaneo', 'error')
    
    return redirect(url_for('index'))

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Mostrar detalles de una oferta de trabajo específica"""
    session = get_session()
    job = session.query(JobOffer).filter_by(id=job_id).first()
    session.close()
    
    if not job:
        flash('Oferta de trabajo no encontrada', 'error')
        return redirect(url_for('index'))
    
    return render_template('job_detail.html', job=job)

@app.route('/filter', methods=['GET'])
def filter_jobs():
    """Filtrar ofertas de trabajo por diferentes criterios"""
    session = get_session()
    
    # Obtener parámetros de filtrado
    city = request.args.get('city', '')
    company = request.args.get('company', '')
    contract_type = request.args.get('contract_type', '')
    
    # Construir la consulta base
    query = session.query(JobOffer)
    
    # Aplicar filtros si se proporcionan
    if city:
        query = query.filter(JobOffer.city.ilike(f'%{city}%'))
    if company:
        query = query.filter(JobOffer.company.ilike(f'%{company}%'))
    if contract_type:
        query = query.filter(JobOffer.contract_type.ilike(f'%{contract_type}%'))
    
    # Obtener resultados ordenados por fecha
    job_offers = query.order_by(JobOffer.created_at.desc()).all()
    
    # Obtener valores únicos para los filtros
    cities = [job.city for job in session.query(JobOffer.city).distinct().all()]
    companies = [job.company for job in session.query(JobOffer.company).distinct().all()]
    contract_types = [job.contract_type for job in session.query(JobOffer.contract_type).distinct().all()]
    
    session.close()
    
    return render_template('index.html', 
                          job_offers=job_offers, 
                          cities=cities, 
                          companies=companies, 
                          contract_types=contract_types,
                          selected_city=city,
                          selected_company=company,
                          selected_contract_type=contract_type)

if __name__ == '__main__':
    app.run(debug=True) 