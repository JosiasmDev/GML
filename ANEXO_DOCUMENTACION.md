# Anexo de Documentación: GML - Gestor de Ofertas de Trabajo

Este anexo amplía la documentación del proyecto "GML - Gestor de Ofertas de Trabajo" con detalles técnicos y funcionales para desarrolladores y usuarios finales. Se basa en el archivo `README.md` existente y aborda aspectos específicos de implementación, uso y mantenimiento.

---

## 1. Documentación Técnica (para desarrolladores)

### 📌 Requisitos del Proyecto

#### Objetivo del proyecto
Desarrollar una aplicación web que integre la búsqueda y gestión de ofertas de trabajo con un sistema de comunicación empresarial existente, permitiendo a los usuarios buscar ofertas en múltiples portales, gestionar sus favoritos y recibir notificaciones relevantes.

#### Alcance y funcionalidades principales
- Búsqueda de ofertas en InfoJobs, LinkedIn y TecnoEmpleo
- Gestión de ofertas favoritas
- Historial de búsquedas
- Notificaciones automáticas
- Integración con sistema de comunicación empresarial
- Dashboard con estadísticas
- Gestión de proyectos y equipos

#### Tecnologías utilizadas
- **Django 5.1.6**: Framework web para backend
- **PostgreSQL**: Base de datos relacional
- **Selenium**: Automatización de navegador para scraping
- **BeautifulSoup4**: Parsing de HTML
- **LinkedIn API**: Integración con LinkedIn
- **django-notifications-hq**: Sistema de notificaciones
- **Bootstrap 5**: Framework CSS
- **Font Awesome**: Iconos
- **jQuery**: Manipulación del DOM
- **Chosen**: Mejora de selectores

#### Requisitos del sistema (hardware/software)
- **Hardware**: Mínimo 4 GB de RAM, 10 GB de espacio libre (desarrollo)
- **Software**: 
  - Sistema operativo: Windows, Linux o MacOS
  - Python 3.13.1
  - PostgreSQL 13+
  - Navegador moderno (Chrome, Firefox, Edge)
  - Geckodriver para Selenium (Firefox)

### 📌 Guía de Instalación y Configuración

#### Requisitos previos
- Python 3.13.1 instalado
- PostgreSQL instalado y corriendo
- Dependencias listadas en `requirements.txt`
- Entorno virtual (`venv`) recomendado
- Geckodriver instalado y en el PATH

#### Instalación del proyecto
1. Clonar el repositorio:

```bash
git clone https://github.com/JosiasmDev/GML.git
cd GML
```

2. Crear y activar un entorno virtual:

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

#### Configuración del entorno
1. Crear un archivo `.env` en la raíz para variables sensibles:

```
DATABASE_NAME=gml_db
DATABASE_USER=postgres
DATABASE_PASSWORD=tu_contraseña
DATABASE_HOST=localhost
DATABASE_PORT=5432
LINKEDIN_EMAIL=tu_email
LINKEDIN_PASSWORD=tu_contraseña
```

2. Editar `jobs/settings.py` para usar las variables de entorno:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}
```

#### Ejecución del servidor

```bash
python manage.py runserver
```

#### Migraciones de la base de datos
1. Crear migraciones:

```bash
python manage.py makemigrations
```

2. Aplicar migraciones:

```bash
python manage.py migrate
```

### 📌 Estructura del Proyecto

#### Explicación de los directorios y archivos clave
- `jobs/`:
  - `models.py`: Definición de modelos (JobOffer, SearchHistory)
  - `views.py`: Lógica de las vistas (búsqueda, gestión de ofertas)
  - `urls.py`: Rutas específicas de la app `jobs`
  - `scrapers/`: Módulos de scraping para cada portal
  - `templates/jobs/`: Plantillas HTML (dashboard, búsqueda, ofertas)
- `ent_com_sis/`:
  - `gestion/`: Aplicación de comunicación empresarial
  - `templates/`: Plantillas del sistema de comunicación
- `static/`: Archivos CSS, JS y fuentes
- `templates/`: Plantillas base
- `manage.py`: Script de gestión de Django

#### Uso de Django Apps
El proyecto usa dos apps principales:
- `jobs`: Para la gestión de ofertas de trabajo
- `gestion`: Para el sistema de comunicación empresarial

#### Arquitectura del software
- **Patrón MVC**: Django implementa Model-View-Controller
- **Modelos**: Definidos en `models.py`
- **Vistas**: Lógica en `views.py`
- **Controladores**: URLs en `urls.py`
- **Patrones usados**: 
  - **Decorator Pattern**: Uso de `@login_required`
  - **Factory Pattern**: Para la creación de scrapers
  - **Strategy Pattern**: Para diferentes estrategias de búsqueda
  - **Observer Pattern**: Para el sistema de notificaciones

### 📌 Base de Datos y Modelos

#### Diagrama de la base de datos (ERD)

[User] ---M:N--- [Proyecto] ---1:N--- [Tarea] ---1:N--- [Comentario]
|                |                |
|                |---1:N--- [MensajeProyecto]
|                |
|---M:N--- [Grupo]
|
|---1:N--- [Rol]
|
|---1:N--- [Mensaje]
|
|---1:N--- [JobOffer]
|
|---1:N--- [SearchHistory]

- **User**: Modelo de Django (`auth_user`)
- **JobOffer**: Campos: `title`, `company`, `location`, `salary`, `url`, `search_history`, `is_favorite`
- **SearchHistory**: Campos: `keywords`, `location`, `source`, `results_count`, `user`
- **Proyecto**: Campos: `titulo`, `descripcion`, `fecha_inicio`, `fecha_fin`, `creador`, `usuarios`
- **Tarea**: Campos: `titulo`, `descripcion`, `estado`, `fecha_limite`, `proyecto`, `asignados`
- **Comentario**: Campos: `contenido`, `autor`, `tarea`
- **Mensaje**: Campos: `contenido`, `remitente`, `destinatario`, `leido`
- **MensajeProyecto**: Campos: `contenido`, `remitente`, `proyecto`
- **Grupo**: Campos: `nombre`, `proyecto`, `miembros`
- **Rol**: Campos: `usuario`, `proyecto`, `rol`

#### Explicación de cada modelo y relaciones
- **JobOffer**: Relaciona búsquedas (`ForeignKey` a `SearchHistory`) y usuarios (`ForeignKey` a `User`)
- **SearchHistory**: Registra búsquedas realizadas por usuarios
- **Proyecto**: Relaciona usuarios (`ManyToMany`) y tiene tareas/mensajes (`ForeignKey`)
- **Tarea**: Pertenece a un proyecto y tiene asignados (`ManyToMany` con `User`)
- **Mensaje**: Comunicación uno-a-uno entre usuarios
- **MensajeProyecto**: Comunicación grupal en un proyecto
- **Grupo**: Agrupa usuarios dentro de un proyecto
- **Rol**: Define permisos por usuario en proyectos

### 📌 Scrapers y APIs

#### InfoJobs Scraper
- **Tecnología**: Selenium + BeautifulSoup4
- **Funcionalidades**:
  - Búsqueda por palabras clave
  - Filtrado por ubicación
  - Extracción de detalles de ofertas
  - Manejo de paginación
- **Consideraciones**:
  - Delays entre peticiones
  - Manejo de captchas
  - Rotación de user agents

#### LinkedIn Scraper
- **Tecnología**: LinkedIn API + Selenium
- **Funcionalidades**:
  - Autenticación con credenciales
  - Búsqueda de ofertas
  - Extracción de detalles
  - Manejo de límites de API
- **Consideraciones**:
  - Almacenamiento seguro de credenciales
  - Rate limiting
  - Manejo de sesiones

#### TecnoEmpleo Scraper
- **Tecnología**: Selenium + BeautifulSoup4
- **Funcionalidades**:
  - Búsqueda por palabras clave
  - Filtrado por ubicación
  - Extracción de detalles
  - Manejo de paginación
- **Consideraciones**:
  - Delays entre peticiones
  - Manejo de errores
  - Rotación de user agents

### 📌 Manejo de Errores y Logs

#### Políticas de manejo de errores
- Uso de `try-except` en scrapers
- Manejo de excepciones específicas por portal
- Sistema de reintentos para fallos de red
- Logging detallado de errores

#### Registro de logs
- Configurado en `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'gml.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

#### Mensajes de error comunes y soluciones
- **Scraping bloqueado**: Implementar delays y rotación de user agents
- **API rate limit**: Implementar sistema de colas
- **DatabaseError**: Verificar conexión y credenciales
- **TemplateDoesNotExist**: Crear plantillas faltantes

### 📌 Pruebas y Deployment

#### Pruebas unitarias y de integración
- Usar `unittest` o `pytest`
- Probar scrapers de forma aislada
- Mockear respuestas de APIs
- Probar integración con base de datos

#### Deployment
- **Docker**: Crear un `Dockerfile`:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

- **Heroku**: Usar `Procfile` y `gunicorn`

#### Configuración de CI/CD
- Ejemplo con GitHub Actions:

```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run migrations
        run: python manage.py migrate
```

## 2. Documentación Funcional (para usuarios o clientes)

### 📌 Manual de Usuario

#### Cómo acceder al sistema
1. Abre el navegador en `http://127.0.0.1:8000/`
2. Inicia sesión en `/login/` con tu usuario y contraseña
3. Si eres nuevo, regístrate en `/proyectos/registro/`

#### Búsqueda de ofertas
1. Selecciona el portal (InfoJobs, LinkedIn o TecnoEmpleo)
2. Introduce palabras clave
3. Selecciona ubicación
4. Establece límite de resultados
5. Haz clic en "Buscar"

#### Gestión de ofertas
- Ver detalles completos
- Marcar como favorita
- Eliminar oferta
- Compartir con equipo

#### Dashboard
- Estadísticas de búsquedas
- Ofertas favoritas
- Notificaciones
- Proyectos activos

#### Integración con sistema de comunicación
- Crear proyectos
- Asignar tareas
- Enviar mensajes
- Gestionar grupos

### 📌 Guía de Troubleshooting

#### Problemas comunes
1. **Búsqueda sin resultados**
   - Verificar palabras clave
   - Comprobar ubicación
   - Aumentar límite de resultados

2. **Error de scraping**
   - Esperar unos minutos
   - Intentar con otro portal
   - Contactar con soporte

3. **Problemas de login**
   - Verificar credenciales
   - Restablecer contraseña
   - Contactar con administrador

### 📌 Mejores prácticas

#### Búsqueda efectiva
- Usar palabras clave específicas
- Combinar términos relevantes
- Filtrar por ubicación precisa
- Establecer límites razonables

#### Gestión de ofertas
- Revisar regularmente favoritos
- Organizar por categorías
- Compartir con equipo
- Mantener historial actualizado

#### Uso del sistema
- Mantener sesión activa
- Revisar notificaciones
- Participar en proyectos
- Comunicar con equipo 