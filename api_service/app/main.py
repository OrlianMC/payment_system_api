from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.logging import setup_logging
from app.core.database import create_db_and_tables

from app.routes import (
    auth_router,
    user_router,
    profile_router,
    card_router,
    payment_router,
)

# --------------------------------------------------
# 🔧 Logging
# --------------------------------------------------
setup_logging()
logger = logging.getLogger(__name__)


# --------------------------------------------------
# 🔄 Lifespan
# --------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando aplicación...")
    create_db_and_tables()
    yield
    logger.info("🛑 Cerrando aplicación...")


# --------------------------------------------------
# ⚙️ App
# --------------------------------------------------
app = FastAPI(
    title="Sistema de Pagos",
    version="1.0.0",
    lifespan=lifespan,
)

# --------------------------------------------------
# 🌐 CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# 🔗 Routers
# --------------------------------------------------
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(profile_router.router, prefix="/profiles", tags=["Profiles"])
app.include_router(card_router.router, prefix="/cards", tags=["Cards"])
app.include_router(payment_router.router, prefix="/payments", tags=["Payments"])


# --------------------------------------------------
# ❤️ Health Check
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


logger.info("✅ Configuración principal cargada")
