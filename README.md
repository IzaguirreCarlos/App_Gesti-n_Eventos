# 🎟️ Izag Gestión Eventos — Plataforma SaaS de Gestión de Eventos

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-5.0-green?style=flat-square&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-red?style=flat-square&logo=redis)
![Docker](https://img.shields.io/badge/Docker-ready-blue?style=flat-square&logo=docker)
![Render](https://img.shields.io/badge/Render-deploy--ready-46E3B7?style=flat-square)

**Plataforma SaaS profesional para gestión de eventos — lista para producción**

</div>

---

## ✨ Características

- 🎪 **Gestión completa de eventos** — CRUD, estados, tipos (presencial/virtual/híbrido)
- 👥 **Sistema de inscripciones** — Con aforo, lista de espera, check-in y QR
- 📅 **Calendario interactivo** — FullCalendar con vistas mensual, semanal y diaria
- 📧 **Notificaciones automáticas** — Celery + Redis para emails async
- 🔐 **Autenticación segura** — JWT para API, sesiones para web
- 🛡️ **Seguridad enterprise** — CSRF, XSS, rate limiting, HTTPS
- 📊 **Dashboard analítico** — Métricas, exportación CSV, gestión de asistentes
- 🌐 **API REST** — DRF completo con Swagger/ReDoc
- 🎨 **UI moderna** — TailwindCSS + HTMX + Alpine.js
- 🐳 **Docker ready** — Compose para desarrollo local
- 🚀 **Render ready** — Configuración automática de producción

---

## 🚀 Instalación local rápida

### Con Docker (recomendado)

```bash
git clone https://github.com/IzaguirreCarlos/App_Gesti-n_Eventos.git
cd App_Gesti-n_Eventos
cp .env.example .env
docker-compose up --build
```

Abre http://localhost:8000

### Sin Docker

```bash
git clone https://github.com/IzaguirreCarlos/App_Gesti-n_Eventos.git
cd App_Gesti-n_Eventos

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencias
pip install -r requirements/development.txt

# Variables de entorno
cp .env.example .env
# Edita .env con tus configuraciones

# Base de datos y migraciones
python manage.py migrate --settings=config.settings.development

# Superusuario
python manage.py createsuperuser --settings=config.settings.development

# Datos de ejemplo
python manage.py loaddata fixtures/initial_data.json --settings=config.settings.development || true

# Ejecutar
python manage.py runserver --settings=config.settings.development
```

---

## 🚀 Deploy en Render

### Paso 1 — Conectar repositorio

1. Ve a [render.com](https://render.com) y crea una cuenta
2. Clic en **New → Blueprint**
3. Conecta tu repositorio de GitHub
4. Render detectará automáticamente el `render.yaml`

### Paso 2 — Configurar variables de entorno

En el dashboard de Render configura:

| Variable | Valor |
|---|---|
| `SECRET_KEY` | Auto-generada |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `DATABASE_URL` | Auto-generada (PostgreSQL) |
| `REDIS_URL` | Auto-generada (Redis) |
| `EMAIL_HOST_USER` | Tu email |
| `EMAIL_HOST_PASSWORD` | App password de Gmail |

### Paso 3 — Deploy

Render ejecuta automáticamente:
1. `build.sh` → instala deps, collectstatic, migrate
2. `start.sh` → inicia Gunicorn

---

## 📁 Estructura del proyecto

```
izag/
├── apps/
│   ├── users/          # Custom User Model, auth
│   ├── events/         # Eventos (modelos, vistas, servicios)
│   ├── registrations/  # Inscripciones, check-in, QR
│   ├── notifications/  # Emails async con Celery
│   ├── dashboard/      # Analytics, exportaciones
│   └── api/            # REST API con JWT
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── celery.py
├── templates/          # Templates HTML (Tailwind + HTMX)
├── static/             # Assets estáticos
├── requirements/       # base, dev, prod
├── Dockerfile
├── docker-compose.yml
├── render.yaml         # ← Deploy automático en Render
├── build.sh
└── start.sh
```

---

## 🔌 API REST

Documentación interactiva disponible en:
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **Schema**: `/api/schema/`

### Endpoints principales

```
POST   /api/v1/auth/token/          # Obtener JWT
POST   /api/v1/auth/token/refresh/  # Renovar token

GET    /api/v1/events/              # Listar eventos
POST   /api/v1/events/              # Crear evento (organizer)
GET    /api/v1/events/{id}/         # Detalle evento
PUT    /api/v1/events/{id}/         # Actualizar (owner)
DELETE /api/v1/events/{id}/         # Eliminar (owner)
POST   /api/v1/events/{id}/register/ # Inscribirse

GET    /api/v1/registrations/       # Mis inscripciones
DELETE /api/v1/registrations/{id}/  # Cancelar inscripción

GET    /api/v1/categories/          # Listar categorías
```

---

## 🧪 Tests

```bash
# Correr todos los tests
python manage.py test --settings=config.settings.development

# Con cobertura
coverage run manage.py test --settings=config.settings.development
coverage report
coverage html
```

---

## ⚙️ Variables de entorno

Ver `.env.example` para la lista completa de variables requeridas.

---

## 🛡️ Seguridad implementada

- CSRF Protection en todos los formularios
- XSS Prevention con Django templating
- SQL Injection prevention (ORM)
- Rate limiting en API
- Secure cookies en producción
- HTTPS redirect en producción
- HSTS headers
- Content Security Policy
- Password validation robusta
- JWT con rotación de tokens

---

## 📄 Licencia

MIT License — Carlos Izaguirre © 2024
