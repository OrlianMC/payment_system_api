from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from fastapi.responses import RedirectResponse

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
    logger.info("🚀 Starting payment system API...")
    create_db_and_tables()
    logger.info("📦 Database initialized successfully")
    yield
    logger.info("🛑 Shutting down payment system API...")


# --------------------------------------------------
# ⚙️ App
# --------------------------------------------------
app = FastAPI(
    title="Payment System API",
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
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(profile_router.router)
app.include_router(card_router.router)
app.include_router(payment_router.router)

logger.info("🔗 API routers registered successfully")


# --------------------------------------------------
# ❤️ Health Check
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# 🔄 Redirect Docs
# --------------------------------------------------
@app.get("/")
def root():
    return RedirectResponse(url="/docs")


logger.info("✅ Main configuration loaded successfully")
