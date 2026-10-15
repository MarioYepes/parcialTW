# Sistema de Autenticacion con OTP

Base del backend para el proyecto academico de autenticacion en dos pasos.
El repositorio contiene la estructura inicial de FastAPI, la configuracion de
SQLAlchemy/SQLite, modelos, esquemas y espacios para rutas y servicios.

## Requisitos

- Python 3.9 o superior
- pip

## Instalacion y ejecucion local

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`. La documentacion interactiva
de OpenAPI se encuentra en `http://127.0.0.1:8000/docs` y el endpoint de estado
en `http://127.0.0.1:8000/health`.

## Estructura

```text
app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  middleware.py
  routes/
    auth.py
    users.py
  services/
    email_service.py
    otp_service.py
```

## Estado

Esta primera etapa establece la estructura y los contratos iniciales. Los
endpoints de autenticacion, la validacion JWT, el envio SMTP, el rate limiting
y las pruebas se implementaran en las siguientes etapas. No configurar
credenciales reales en `.env.example`; usar `.env` local y no versionarlo.
