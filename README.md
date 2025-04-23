# GML - Gestor de Ofertas de Trabajo

## Sistema Integrado de Búsqueda y Gestión de Ofertas de Trabajo

Este proyecto es una aplicación web desarrollada con Django que permite la búsqueda y gestión de ofertas de trabajo en múltiples portales (InfoJobs, LinkedIn y TecnoEmpleo). Se integra con el Sistema de Comunicación Empresarial (ent_com_sis) para proporcionar una experiencia completa de gestión de proyectos y ofertas de trabajo.

## Descripción general

La aplicación facilita la búsqueda y gestión de ofertas de trabajo mediante la integración con múltiples portales de empleo. Los usuarios pueden realizar búsquedas personalizadas, guardar ofertas favoritas y recibir notificaciones sobre nuevas ofertas relevantes. Todo esto se integra con el sistema de comunicación empresarial existente para una gestión completa de proyectos y equipos.

## Requisitos previos

- **Python**: Versión 3.13.1 (o superior compatible con Django 5.1.6)
- **PostgreSQL**: Base de datos utilizada para almacenar los datos de la aplicación
- **Entorno virtual**: Recomendado para gestionar dependencias (por ejemplo, venv)
- **Sistema operativo**: Probado en Windows (compatible con Linux/Mac con ajustes menores)
- **Navegador web**: Chrome o Firefox para el scraping de ofertas

## Instalación

Sigue estos pasos para instalar y configurar el proyecto en tu máquina local:

### 1. Clonar el repositorio

```bash
git clone https://github.com/JosiasmDev/GML.git
cd GML
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
./venv/Scripts/activate   # En Windows
```

### 3. Instalar las dependencias

Asegúrate de tener el archivo `requirements.txt` generado previamente y luego instala las dependencias:

```bash
pip install -r requirements.txt
```

#### Dependencias principales:

- `Django==5.1.6`: Framework web
- `django-notifications-hq==1.7.0`: Sistema de notificaciones
- `psycopg2-binary==2.9.9`: Adaptador de PostgreSQL
- `selenium==4.18.1`: Para el scraping de ofertas
- `beautifulsoup4==4.12.3`: Para el parsing de HTML
- `linkedin-api==2.0.0a5`: Para la integración con LinkedIn

### 4. Configurar la base de datos

1. Instala PostgreSQL y crea una base de datos llamada `gml_db`
2. Edita `jobs/settings.py` con tus credenciales de PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gml_db',
        'USER': 'postgres',  # Cambia según tu usuario
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Configurar las credenciales de LinkedIn

1. Crea un archivo `.env` en la raíz del proyecto
2. Añade tus credenciales de LinkedIn:

```
LINKEDIN_EMAIL=tu_email
LINKEDIN_PASSWORD=tu_contraseña
```

### 6. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear un superusuario

```bash
python manage.py createsuperuser
```

## Ejecución

### Iniciar el servidor

```bash
python manage.py runserver
```

### Acceder a la aplicación

- Abre tu navegador en [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Inicia sesión con el superusuario o regístrate en `/proyectos/registro/`

### Rutas principales

- `/`: Dashboard principal
- `/infojobs/`: Búsqueda en InfoJobs
- `/linkedin/`: Búsqueda en LinkedIn
- `/tecnoempleo/`: Búsqueda en TecnoEmpleo
- `/proyectos/`: Lista de proyectos (integración con ent_com_sis)
- `/proyectos/notificaciones/`: Lista de notificaciones
- `/login/`: Inicio de sesión
- `/proyectos/registro/`: Registro de nuevos usuarios

## Arquitectura del proyecto

### Estructura de directorios

```
GML/
├── jobs/                    # Aplicación principal
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── scrapers/           # Módulos de scraping
│   │   ├── infojobs_scraper.py
│   │   ├── linkedin_scraper.py
│   │   └── tecnoempleo_scraper.py
│   └── templates/
│       └── jobs/
├── ent_com_sis/            # Sistema de comunicación empresarial
│   ├── gestion/
│   └── templates/
├── static/                 # Archivos estáticos
├── templates/              # Plantillas base
├── manage.py
└── requirements.txt
```

### Modelos principales

- **JobOffer**: Representa una oferta de trabajo con título, empresa, ubicación, etc.
- **SearchHistory**: Historial de búsquedas realizadas
- **Proyecto**: Proyectos del sistema de comunicación empresarial
- **Tarea**: Tareas asociadas a proyectos
- **Mensaje**: Mensajes privados entre usuarios
- **Grupo**: Grupos de usuarios
- **Rol**: Roles de usuarios en proyectos

### Vistas principales

- **Dashboard**: Vista general con estadísticas
- **Búsqueda de ofertas**: Formularios de búsqueda para cada portal
- **Gestión de ofertas**: Ver, marcar favoritas y eliminar ofertas
- **Proyectos**: Gestión de proyectos (integración con ent_com_sis)
- **Notificaciones**: Sistema de notificaciones unificado

## Dependencias externas

- **Django**: Framework principal
- **django-notifications-hq**: Sistema de notificaciones
- **Selenium**: Automatización de navegador para scraping
- **BeautifulSoup4**: Parsing de HTML
- **LinkedIn API**: Integración con LinkedIn
- **Bootstrap 5**: Framework CSS
- **Font Awesome**: Iconos
- **jQuery**: Manipulación del DOM
- **Chosen**: Mejora de selectores

## Decisiones de diseño

### Arquitectura modular
- **Razón**: Separación clara entre scraping y gestión
- **Impacto**: Facilita el mantenimiento y la extensión

### Base de datos PostgreSQL
- **Razón**: Soporte robusto para relaciones complejas
- **Impacto**: Mayor rendimiento y fiabilidad

### Sistema de notificaciones unificado
- **Razón**: Integración con el sistema existente
- **Impacto**: Experiencia de usuario coherente

### Diseño oscuro
- **Razón**: Estética profesional y reducción de fatiga visual
- **Impacto**: Consistencia visual con el sistema existente

## Problemas conocidos y soluciones

- **Scraping bloqueado**: Implementado sistema de reintentos y delays
- **Credenciales de LinkedIn**: Almacenamiento seguro en variables de entorno
- **Rendimiento de búsquedas**: Optimización de consultas y paginación

## Contribución

1. Clona el repositorio y crea una rama:

   ```bash
   git checkout -b nueva-funcionalidad
   ```

2. Realiza cambios y haz un commit:

   ```bash
   git add .
   git commit -m "Descripción de los cambios"
   ```

3. Envía un pull request al repositorio principal.

## Licencia

Este proyecto no tiene una licencia explícita definida. Se considera de uso privado a menos que se especifique lo contrario. 