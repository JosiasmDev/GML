# Manual de Usuario: GML - Gestor de Ofertas de Trabajo

## 1. Aplicación Web

### 1.1 Acceso al Sistema

#### Registro de Usuario
1. Accede a `http://127.0.0.1:8000/proyectos/registro/`
2. Completa el formulario con:
   - Nombre de usuario
   - Correo electrónico
   - Contraseña
   - Confirmación de contraseña
3. Haz clic en "Registrarse"

#### Inicio de Sesión
1. Accede a `http://127.0.0.1:8000/login/`
2. Introduce tus credenciales:
   - Nombre de usuario
   - Contraseña
3. Haz clic en "Iniciar Sesión"

### 1.2 Búsqueda de Ofertas

#### Búsqueda en InfoJobs
1. Accede a `/infojobs/`
2. Completa el formulario:
   - Palabras clave (ej: "Python Developer")
   - Ubicación (ej: "Madrid")
   - Límite de resultados (1-100)
3. Haz clic en "Buscar"
4. Espera a que se complete la búsqueda
5. Revisa los resultados en el dashboard

#### Búsqueda en LinkedIn
1. Accede a `/linkedin/`
2. Completa el formulario:
   - Palabras clave
   - Ubicación
   - Límite de resultados
3. Haz clic en "Buscar"
4. Espera a que se complete la búsqueda
5. Revisa los resultados en el dashboard

#### Búsqueda en TecnoEmpleo
1. Accede a `/tecnoempleo/`
2. Completa el formulario:
   - Palabras clave
   - Ubicación
   - Límite de resultados
3. Haz clic en "Buscar"
4. Espera a que se complete la búsqueda
5. Revisa los resultados en el dashboard

### 1.3 Gestión de Ofertas

#### Ver Detalles de una Oferta
1. En el dashboard, haz clic en el título de la oferta
2. Se mostrará:
   - Título del puesto
   - Empresa
   - Ubicación
   - Salario
   - Descripción
   - Requisitos
   - Enlace original

#### Marcar como Favorita
1. En el dashboard, haz clic en el icono de estrella
2. La oferta se marcará como favorita
3. Puedes ver todas tus ofertas favoritas en la sección "Favoritos"

#### Eliminar Oferta
1. En el dashboard, haz clic en el icono de papelera
2. Confirma la eliminación
3. La oferta se eliminará de tu lista

#### Compartir con Equipo
1. En el dashboard, haz clic en el icono de compartir
2. Selecciona el proyecto o grupo
3. Añade un mensaje opcional
4. Haz clic en "Compartir"

### 1.4 Dashboard

#### Estadísticas
- Total de ofertas encontradas
- Ofertas por portal
- Ofertas por ubicación
- Tendencias salariales

#### Favoritos
- Lista de ofertas marcadas como favoritas
- Filtros por portal y ubicación
- Ordenación por fecha o relevancia

#### Notificaciones
- Nuevas ofertas relevantes
- Actualizaciones de ofertas favoritas
- Mensajes del equipo
- Recordatorios de proyectos

### 1.5 Gestión de Proyectos

#### Crear Proyecto
1. Accede a `/proyectos/`
2. Haz clic en "Nuevo Proyecto"
3. Completa el formulario:
   - Título
   - Descripción
   - Fecha de inicio
   - Fecha de fin
4. Haz clic en "Crear"

#### Asignar Tareas
1. En el proyecto, haz clic en "Nueva Tarea"
2. Completa el formulario:
   - Título
   - Descripción
   - Fecha límite
   - Asignados
3. Haz clic en "Crear"

#### Gestionar Grupos
1. En el proyecto, haz clic en "Gestionar Grupos"
2. Crea un nuevo grupo o edita uno existente
3. Añade o elimina miembros
4. Asigna roles

## 2. Aplicación de Escritorio

### 2.1 Instalación

#### Windows
1. Descarga el instalador desde la página de releases
2. Ejecuta el instalador
3. Sigue las instrucciones del asistente
4. La aplicación se instalará en `C:\Program Files\GML`

#### Linux
1. Descarga el paquete .deb
2. Instala con:
```bash
sudo dpkg -i gml-desktop.deb
```

#### macOS
1. Descarga el archivo .dmg
2. Arrastra la aplicación a la carpeta Aplicaciones
3. Ejecuta la aplicación

### 2.2 Uso Básico

#### Iniciar Sesión
1. Abre la aplicación
2. Introduce tus credenciales:
   - URL del servidor (ej: http://localhost:8000)
   - Nombre de usuario
   - Contraseña
3. Haz clic en "Conectar"

#### Sincronización
1. La aplicación se sincronizará automáticamente
2. Verás el estado de la sincronización en la barra de estado
3. Puedes forzar una sincronización manual desde el menú

### 2.3 Gestión de Ofertas

#### Ver Ofertas
1. En el panel izquierdo, selecciona "Ofertas"
2. Verás la lista de ofertas sincronizadas
3. Usa los filtros para buscar ofertas específicas

#### Editar Oferta
1. Haz doble clic en una oferta
2. Edita los campos necesarios
3. Haz clic en "Guardar"

#### Eliminar Oferta
1. Selecciona la oferta
2. Haz clic en el botón "Eliminar"
3. Confirma la eliminación

### 2.4 Exportación

#### Exportar a Excel
1. Selecciona las ofertas a exportar
2. Haz clic en "Exportar" > "Excel"
3. Elige la ubicación del archivo
4. Haz clic en "Guardar"

#### Exportar a PDF
1. Selecciona las ofertas a exportar
2. Haz clic en "Exportar" > "PDF"
3. Elige la ubicación del archivo
4. Haz clic en "Guardar"

### 2.5 Configuración

#### Preferencias
1. Accede a "Configuración" > "Preferencias"
2. Configura:
   - Idioma
   - Tema
   - Notificaciones
   - Sincronización automática

#### Conexión
1. Accede a "Configuración" > "Conexión"
2. Configura:
   - URL del servidor
   - Puerto
   - Timeout
   - Proxy (si es necesario)

## 3. Solución de Problemas

### 3.1 Problemas Comunes

#### Error de Conexión
- Verifica que el servidor esté en ejecución
- Comprueba la URL y el puerto
- Verifica tu conexión a internet

#### Error de Sincronización
- Verifica tus credenciales
- Comprueba el espacio en disco
- Reinicia la aplicación

#### Error de Scraping
- Espera unos minutos
- Intenta con otro portal
- Verifica las credenciales de LinkedIn

### 3.2 Contacto con Soporte

#### Enviar Reporte
1. Accede a "Ayuda" > "Enviar Reporte"
2. Describe el problema
3. Adjunta capturas de pantalla si es necesario
4. Haz clic en "Enviar"

#### Contacto Directo
- Email: soporte@gml.com
- Teléfono: +34 900 123 456
- Horario: L-V 9:00-18:00 