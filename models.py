"""
Modelos para la base de datos de ofertas de trabajo
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Crear la base de datos
Base = declarative_base()

class JobOffer(Base):
    """Modelo para las ofertas de trabajo"""
    __tablename__ = 'job_offers'
    
    id = Column(Integer, primary_key=True)
    position = Column(String)
    company = Column(String)
    company_valuation = Column(Float, nullable=True)
    city = Column(String)
    country = Column(String)
    contract_type = Column(String)
    salary = Column(String)
    min_exp = Column(String)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<JobOffer(position='{self.position}', company='{self.company}')>"

# Configuración de la conexión a la base de datos
DB_USER = 'postgres'
DB_PASSWORD = 'aaaaaa'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'gml_db'

# Crear el motor de la base de datos
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Crear todas las tablas
def init_db():
    Base.metadata.create_all(engine)

# Crear una sesión
Session = sessionmaker(bind=engine)

def get_session():
    return Session() 