"""Punto de entrada: crea la app, monta los archivos estáticos y las rutas."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import router

BASE = Path(__file__).resolve().parent

app = FastAPI(
    title="Vestidor Virtual",
    description="Probador con avatar que te dice si tu outfit combina.",
    version="1.0.0",
)
# el probador trae todo el clóset dibujado en SVG; comprimido pesa mucho menos
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
app.include_router(router)
