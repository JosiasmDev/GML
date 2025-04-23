# Diagramas del Sistema: GML - Gestor de Ofertas de Trabajo

## 1. Diagramas de Arquitectura

### 1.1 Arquitectura General del Sistema
```mermaid
graph TB
    subgraph Cliente
        Web[Cliente Web]
        Desktop[Aplicación Desktop]
    end

    subgraph Servidor
        API[API REST]
        Scrapers[Scrapers]
        Cache[Caché]
        DB[(Base de Datos)]
    end

    subgraph Externos
        InfoJobs[InfoJobs]
        LinkedIn[LinkedIn]
        TecnoEmpleo[TecnoEmpleo]
    end

    Web --> API
    Desktop --> API
    API --> Scrapers
    API --> Cache
    API --> DB
    Scrapers --> InfoJobs
    Scrapers --> LinkedIn
    Scrapers --> TecnoEmpleo
```

### 1.2 Arquitectura de Componentes
```mermaid
graph LR
    subgraph Frontend
        UI[Interfaz de Usuario]
        JS[JavaScript]
        CSS[Estilos]
    end

    subgraph Backend
        Views[Vistas]
        Models[Modelos]
        Scrapers[Scrapers]
        Auth[Autenticación]
    end

    subgraph Base de Datos
        DB[(PostgreSQL)]
        Cache[(Redis)]
    end

    UI --> JS
    JS --> Views
    Views --> Models
    Views --> Auth
    Models --> DB
    Scrapers --> Cache
```

## 2. Diagramas de Flujo

### 2.1 Flujo de Búsqueda de Ofertas
```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend
    participant S as Scraper
    participant P as Portal
    participant DB as Base de Datos

    U->>F: Inicia búsqueda
    F->>B: Envía parámetros
    B->>S: Solicita scraping
    S->>P: Realiza búsqueda
    P-->>S: Devuelve resultados
    S->>B: Procesa resultados
    B->>DB: Guarda ofertas
    DB-->>B: Confirma guardado
    B-->>F: Devuelve resultados
    F-->>U: Muestra ofertas
```

### 2.2 Flujo de Autenticación
```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend
    participant DB as Base de Datos

    U->>F: Ingresa credenciales
    F->>B: Envía credenciales
    B->>DB: Verifica usuario
    DB-->>B: Confirma usuario
    B->>B: Genera token
    B-->>F: Devuelve token
    F-->>U: Redirige a dashboard
```

## 3. Diagramas de Base de Datos

### 3.1 Modelo Entidad-Relación Completo
```mermaid
erDiagram
    User {
        int id PK
        string username
        string email
        string password
        datetime created_at
    }
    
    JobOffer {
        int id PK
        string title
        string company
        string location
        string salary
        string url
        bool is_favorite
        datetime created_at
    }
    
    SearchHistory {
        int id PK
        string keywords
        string location
        string source
        int results_count
        datetime created_at
    }
    
    Proyecto {
        int id PK
        string titulo
        string descripcion
        datetime fecha_inicio
        datetime fecha_fin
    }
    
    Tarea {
        int id PK
        string titulo
        string descripcion
        string estado
        datetime fecha_limite
    }
    
    User ||--o{ JobOffer : "crea"
    User ||--o{ SearchHistory : "realiza"
    User ||--o{ Proyecto : "participa"
    User ||--o{ Tarea : "asignada"
    Proyecto ||--o{ Tarea : "contiene"
    JobOffer }o--|| SearchHistory : "pertenece"
```

### 3.2 Diagrama de Tablas
```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string email
        +string password
        +datetime created_at
        +create_job_offer()
        +perform_search()
        +join_project()
    }
    
    class JobOffer {
        +int id
        +string title
        +string company
        +string location
        +string salary
        +string url
        +bool is_favorite
        +datetime created_at
        +mark_as_favorite()
        +share_with_team()
    }
    
    class SearchHistory {
        +int id
        +string keywords
        +string location
        +string source
        +int results_count
        +datetime created_at
        +get_results()
        +export_results()
    }
    
    User "1" -- "*" JobOffer : creates
    User "1" -- "*" SearchHistory : performs
    JobOffer "*" -- "1" SearchHistory : belongs_to
```

## 4. Diagramas de Componentes

### 4.1 Estructura de Módulos
```mermaid
graph TD
    subgraph Core
        A[Autenticación]
        B[Base de Datos]
        C[Caché]
    end

    subgraph Scrapers
        D[InfoJobs]
        E[LinkedIn]
        F[TecnoEmpleo]
    end

    subgraph Análisis
        G[Procesamiento NLP]
        H[Análisis de Tendencias]
        I[Recomendaciones]
    end

    subgraph UI
        J[Web Interface]
        K[Desktop App]
    end

    A --> B
    B --> C
    D --> B
    E --> B
    F --> B
    B --> G
    G --> H
    H --> I
    J --> A
    K --> A
```

### 4.2 Flujo de Datos
```mermaid
flowchart LR
    subgraph Input
        A[Palabras Clave]
        B[Ubicación]
        C[Límite]
    end

    subgraph Procesamiento
        D[Scraping]
        E[Análisis]
        F[Clasificación]
    end

    subgraph Output
        G[Resultados]
        H[Estadísticas]
        I[Recomendaciones]
    end

    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
```

## 5. Diagramas de Despliegue

### 5.1 Arquitectura de Despliegue
```mermaid
graph TB
    subgraph Cliente
        Browser[Navegador Web]
        Desktop[App Desktop]
    end

    subgraph Servidor
        Nginx[Nginx]
        Gunicorn[Gunicorn]
        Django[Django]
        Redis[Redis]
    end

    subgraph Base de Datos
        PostgreSQL[(PostgreSQL)]
    end

    Browser --> Nginx
    Desktop --> Nginx
    Nginx --> Gunicorn
    Gunicorn --> Django
    Django --> Redis
    Django --> PostgreSQL
```

### 5.2 Pipeline de CI/CD
```mermaid
graph LR
    subgraph Desarrollo
        A[Git]
        B[Tests]
        C[Build]
    end

    subgraph Staging
        D[Deploy]
        E[QA]
    end

    subgraph Producción
        F[Deploy]
        G[Monitor]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
``` 