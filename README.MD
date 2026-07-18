
```markdown
# Caronte Architecture Blueprint

This document details the software architecture, database design, and structure for the **Caronte** project. 

## 🛠️ System Architecture (UML Sequence)

This sequence diagram illustrates how the Front-end (Next.js) interacts with the pure RESTful Django Back-end through the API layer, bypassing templates, handling CORS, and isolating business logic inside Services.

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Browser)
    participant Front as Front-end<br/>(Next.js + Shadcn UI)
    participant CORS as CORS Middleware<br/>(Django)
    participant View as View / Router<br/>(Django REST)
    participant Service as Service Layer<br/>(auth_service.py)
    participant Model as Model / DB<br/>(Django ORM)

    User->>Front: Inputs credentials and clicks "Login"
    Front->>CORS: POST /api/auth/login/ (JSON)
    
    alt Unauthorized Origin?
        CORS-->>Front: Blocks request (CORS Error)
    else Valid Origin
        CORS->>View: Forwards request
    end

    View->>Service: authenticate_user(username, password)
    
    critical Validate Credentials
        Service->>Model: Queries user from DB
        Model-->>Service: Returns user data
    end

    alt Invalid Credentials
        Service-->>View: Raises Exception (AuthenticationFailed)
        View-->>Front: Returns 401 Unauthorized
        Front-->>User: Displays "Invalid username or password"
    else Correct Credentials
        Service->>Service: Generates JWT Token Pair (Access & Refresh)
        Service-->>View: Returns tokens
        View-->>Front: Returns 200 OK + Tokens (JSON)
        Front->>Front: Stores tokens (Secure / HttpOnly Cookies)
        Front-->>User: Redirects to Dashboard
    end

```

---

## 📊 Database Design (Entity-Relationship Diagram)

The data models have been optimized for relational structures and support both **MySQL** and **PostgreSQL** architectures natively through Django ORM.

### Suggested Improvements Added:

* `is_active` / `is_staff`: Standard Django user management flags.
* `last_login_ip`: Auditing parameter to block suspicious login patterns.
* `updated_at` / `created_at`: Standard timestamp fields for database integrity.

```mermaid
erDiagram
    User {
        bigint id PK
        varchar(150) name
        varchar(254) email UK
        varchar(128) password_hash
        boolean is_active
        boolean is_staff
        boolean force_password_change
        boolean generic_password_in_use
        char(36) jwt_token_version "Used to invalidate tokens globally if needed"
        datetime date_joined
        datetime created_at
        datetime updated_at
    }

    UserData {
        bigint id PK
        bigint user_id FK "One-to-One"
        varchar(100) city
        varchar(100) country
        varchar(255) address
        char(11) cpf UK "Optional / Localized Tax ID"
        char(14) cnpj UK "Optional / Localized Company Tax ID"
        varchar(20) cell_phone
        datetime created_at
        datetime updated_at
    }

    AccessControl {
        bigint id PK
        bigint user_id FK "One-to-One"
        smallint failed_login_attempts
        datetime lockout_until
        varchar(45) last_login_ip
        datetime last_login_at
        datetime updated_at
    }

    PasswordReset {
        bigint id PK
        bigint user_id FK "One-to-Many"
        varchar(128) reset_token UK
        boolean is_used
        datetime expires_at
        datetime created_at
    }

    User ||--|| UserData : "has profile details"
    User ||--|| AccessControl : "tracked by security controls"
    User ||--o{ PasswordReset : "requests zero or many resets"

```

---

## 📂 Backend Directory Structure

To fulfill the MV (Model-View) pattern and integrate dedicated services, the structure for the **Caronte** application is defined as follows:

```text
caronte_backend/
│
├── core/                         # Global configuration directory
│   ├── __init__.py
│   ├── settings.py               # Configured for Multi-DB (MySQL/Postgres), CORS, and SimpleJWT
│   ├── urls.py                   # Main routing file
│   └── wsgi.py
│
├── apps/                         # App encapsulation directory
│   └── caronte/                  # Main authentication & core app
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py             # Contains database schemas and ORM mapping (User, UserData, etc.)
│       ├── views.py              # Pure HTTP controller (handles requests, delegates to services)
│       ├── serializers.py        # Validates incoming JSON data and formats outgoing JSON payloads
│       ├── urls.py               # Localized endpoints for caronte app
│       │
│       └── services/             # 🧠 Pure Business Logic Layer
│           ├── __init__.py
│           ├── auth_service.py   # User authentication, JWT generation, and login constraints
│           └── user_service.py   # Handles password resets, user updates, and registrations
│
└── manage.py

```

---

## 🎯 Technical Requirements

Make sure to initialize your environment installing the dependencies required to connect both **MySQL** or **PostgreSQL** interchangeably, alongside handling tokens and web permissions:

1. **`djangorestframework`**: Turns Django into a robust REST API framework.
2. **`django-cors-headers`**: Essential middleware allowing your Next.js application (`localhost:3000`) to communicate across origins to Django (`localhost:8000`).
3. **`djangorestframework-simplejwt`**: Handles standard Json Web Token workflows natively.
4. **`mysqlclient`**: Engine connector used if choosing **MySQL**.
5. **`psycopg2-binary`**: Engine connector used if choosing **PostgreSQL**.

---

## 🚀 Local Setup Tutorial

This tutorial covers the minimum steps to run the project locally on WSL Ubuntu, Ubuntu, Windows, and macOS.

### 1) Prerequisites

Install these tools first:

* Python 3.11 or newer
* Node.js 18 or newer
* npm or pnpm
* Git
* A database server: MySQL or PostgreSQL

Recommended Python packages for the backend:

* djangorestframework
* django-cors-headers
* djangorestframework-simplejwt
* mysqlclient or psycopg2-binary, depending on the chosen database

### 2) Ubuntu / WSL Ubuntu

Install system packages:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential libpq-dev pkg-config git curl
```

If you will use MySQL, also install:

```bash
sudo apt install -y default-libmysqlclient-dev
```

If you will use PostgreSQL, also install:

```bash
sudo apt install -y libpq-dev
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install the backend dependencies:

```bash
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt
```

Install the database driver that matches your database:

```bash
pip install mysqlclient
```

or:

```bash
pip install psycopg2-binary
```

### 3) Windows

Install these tools:

* Python from python.org, and enable "Add Python to PATH"
* Git for Windows
* Node.js LTS from nodejs.org
* Visual Studio Build Tools or the C++ Build Tools workload if you use `mysqlclient`
* MySQL or PostgreSQL desktop/server installer

Create and activate the virtual environment:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install the backend dependencies:

```powershell
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt
```

Install the driver:

```powershell
pip install mysqlclient
```

or:

```powershell
pip install psycopg2-binary
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 4) macOS

Install Homebrew first, then use it to install the base tools:

```bash
brew install python git node pkg-config
```

If you will use PostgreSQL, install the client libraries:

```bash
brew install libpq
```

If you will use MySQL, install the client libraries:

```bash
brew install mysql-client
```

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install the backend dependencies:

```bash
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt
```

Install the matching driver:

```bash
pip install psycopg2-binary
```

or:

```bash
pip install mysqlclient
```

### 5) Run the project locally

After installing the dependencies, run the backend and frontend with the commands defined by your project structure.

Typical Django commands:

```bash
python manage.py migrate
python manage.py runserver
```

Typical Next.js commands:

```bash
npm install
npm run dev
```

### 6) Environment variables

Create a `.env` file and configure at least:

* `SECRET_KEY`
* `DEBUG`
* `ALLOWED_HOSTS`
* `DATABASE_URL` or the equivalent database settings
* `CORS_ALLOWED_ORIGINS`

Example local CORS origin:

```text
http://localhost:3000
```

### 7) Final verification

Check that:

* Django starts without migration errors
* The database driver matches the selected database
* The frontend can call the backend API on the configured CORS origin

---

## ⚖️ Project License

This project is open-source and licensed under the **GNU Lesser General Public License v3 (LGPLv3)**.

```

```