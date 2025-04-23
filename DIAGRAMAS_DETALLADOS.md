# Diagramas Detallados: GML - Gestor de Ofertas de Trabajo

## 1. Diagrama ER Detallado

```mermaid
erDiagram
    User {
        int id PK
        string username
        string email
        string password
        string first_name
        string last_name
        datetime created_at
        datetime last_login
        bool is_active
        bool is_staff
    }
    
    JobOffer {
        int id PK
        string title
        string company
        string location
        string salary
        string url
        string description
        string requirements
        string benefits
        bool is_favorite
        datetime created_at
        datetime updated_at
        int user_id FK
        int search_history_id FK
    }
    
    SearchHistory {
        int id PK
        string keywords
        string location
        string source
        int results_count
        datetime created_at
        int user_id FK
    }
    
    Proyecto {
        int id PK
        string titulo
        string descripcion
        datetime fecha_inicio
        datetime fecha_fin
        string estado
        int creador_id FK
    }
    
    Tarea {
        int id PK
        string titulo
        string descripcion
        string estado
        datetime fecha_limite
        int proyecto_id FK
    }
    
    Comentario {
        int id PK
        string contenido
        datetime created_at
        int tarea_id FK
        int autor_id FK
    }
    
    Mensaje {
        int id PK
        string contenido
        datetime created_at
        bool leido
        int remitente_id FK
        int destinatario_id FK
    }
    
    MensajeProyecto {
        int id PK
        string contenido
        datetime created_at
        int proyecto_id FK
        int remitente_id FK
    }
    
    Grupo {
        int id PK
        string nombre
        int proyecto_id FK
    }
    
    Rol {
        int id PK
        string nombre
        int usuario_id FK
        int proyecto_id FK
    }
    
    User ||--o{ JobOffer : "crea"
    User ||--o{ SearchHistory : "realiza"
    User ||--o{ Proyecto : "participa"
    User ||--o{ Tarea : "asignada"
    User ||--o{ Comentario : "escribe"
    User ||--o{ Mensaje : "envía/recibe"
    User ||--o{ MensajeProyecto : "envía"
    User ||--o{ Grupo : "pertenece"
    User ||--o{ Rol : "tiene"
    
    Proyecto ||--o{ Tarea : "contiene"
    Proyecto ||--o{ MensajeProyecto : "tiene"
    Proyecto ||--o{ Grupo : "tiene"
    
    Tarea ||--o{ Comentario : "tiene"
    
    JobOffer }o--|| SearchHistory : "pertenece"
```

## 2. Componentes Modulares y su Interacción

### 2.1 Arquitectura de Módulos
```mermaid
graph TB
    subgraph Core
        A[Autenticación]
        B[Base de Datos]
        C[Caché]
        D[Configuración]
    end

    subgraph Scrapers
        E[InfoJobs Scraper]
        F[LinkedIn Scraper]
        G[TecnoEmpleo Scraper]
        H[Scraper Manager]
    end

    subgraph Análisis
        I[Procesamiento NLP]
        J[Análisis de Tendencias]
        K[Recomendaciones]
        L[Clasificación]
    end

    subgraph UI
        M[Web Interface]
        N[Desktop App]
        O[API REST]
    end

    subgraph Comunicación
        P[Mensajería]
        Q[Notificaciones]
        R[Compartir]
    end

    subgraph Gestión
        S[Proyectos]
        T[Tareas]
        U[Grupos]
        V[Roles]
    end

    %% Conexiones Core
    A --> B
    B --> C
    D --> A
    D --> B
    D --> C

    %% Conexiones Scrapers
    H --> E
    H --> F
    H --> G
    E --> B
    F --> B
    G --> B

    %% Conexiones Análisis
    I --> J
    J --> K
    L --> K
    B --> I
    B --> J
    B --> L

    %% Conexiones UI
    M --> O
    N --> O
    O --> A
    O --> B
    O --> C

    %% Conexiones Comunicación
    P --> B
    Q --> B
    R --> B
    P --> O
    Q --> O
    R --> O

    %% Conexiones Gestión
    S --> B
    T --> B
    U --> B
    V --> B
    S --> O
    T --> O
    U --> O
    V --> O
```

### 2.2 Flujo de Interacción entre Módulos
```mermaid
sequenceDiagram
    participant UI as Interfaz de Usuario
    participant API as API REST
    participant Auth as Autenticación
    participant DB as Base de Datos
    participant Scraper as Scraper Manager
    participant Analysis as Análisis
    participant Comm as Comunicación
    participant Gest as Gestión

    UI->>API: Solicitud de búsqueda
    API->>Auth: Verificar token
    Auth-->>API: Token válido
    API->>Scraper: Iniciar scraping
    Scraper->>DB: Guardar resultados
    DB-->>Scraper: Confirmación
    Scraper->>Analysis: Procesar resultados
    Analysis->>DB: Guardar análisis
    DB-->>Analysis: Confirmación
    Analysis->>Comm: Notificar resultados
    Comm->>DB: Registrar notificación
    DB-->>Comm: Confirmación
    Comm->>Gest: Actualizar proyecto
    Gest->>DB: Guardar cambios
    DB-->>Gest: Confirmación
    Gest-->>API: Respuesta completa
    API-->>UI: Mostrar resultados
```

### 2.3 Dependencias entre Módulos
```mermaid
graph LR
    subgraph Dependencias
        A[Core] --> B[Scrapers]
        A --> C[Análisis]
        A --> D[UI]
        A --> E[Comunicación]
        A --> F[Gestión]
        
        B --> C
        B --> E
        
        C --> E
        C --> F
        
        D --> E
        D --> F
        
        E --> F
    end
``` 