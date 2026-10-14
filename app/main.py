"""Punto de entrada ASGI para ejecutar la API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import Base, engine
from app.limiter import limiter
from app.routes import auth, users


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Crea las tablas definidas al iniciar la aplicacion."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Sistema de Autenticacion con OTP",
    description="API de autenticacion de dos pasos con FastAPI.",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(auth.router, prefix="/auth", tags=["Autenticacion"])
app.include_router(users.router, prefix="/users", tags=["Usuarios"])


@app.get("/health", tags=["Estado"])
def health_check() -> dict[str, str]:
    """Confirma que la API esta respondiendo."""
    return {"status": "ok"}
