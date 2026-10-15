# Sistema de Autenticacion con OTP (FastAPI)

Backend completo para autenticacion en dos pasos con FastAPI, SQLAlchemy/SQLite,
JWT y codigos OTP enviados por correo.

## Requisitos

- Python 3.9 o superior
- pip

## Instalacion y ejecucion local

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`. La documentacion interactiva
de OpenAPI se encuentra en `http://127.0.0.1:8000/docs` y el endpoint de estado
en `http://127.0.0.1:8000/health`.

## Estructura

```text
app/
  config.py
  database.py
  limiter.py
  middleware.py
  models.py
  schemas.py
  security.py
  routes/
    auth.py
    users.py
  services/
    email_service.py
    otp_service.py
main.py
tests/
```

## Variables de entorno

Copia `.env.example` a `.env` y completa los valores (especialmente `JWT_SECRET_KEY`
y las credenciales SMTP). En produccion configuralas en el panel del proveedor.

## Pruebas

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
```

## Despliegue

Para Render/Railway se incluyen `Procfile`, `runtime.txt` y `render.yaml`.
Comando de inicio:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```