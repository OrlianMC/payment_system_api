from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from fastapi.responses import RedirectResponse

from app.core.logging import setup_logging
from app.routes.payment_router import router as payment_router


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
    logger.info("🚀 Starting payment processor service...")
    yield
    logger.info("🛑 Shutting down payment processor service...")


# --------------------------------------------------
# ⚙️ App
# --------------------------------------------------
app = FastAPI(
    title="Payment Processor Microservice",
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
app.include_router(payment_router)


# --------------------------------------------------
# 🔄 Redirect Docs
# --------------------------------------------------
@app.get("/")
def root():
    return RedirectResponse(url="/docs")


logger.info("✅ Main configuration loaded successfully")
