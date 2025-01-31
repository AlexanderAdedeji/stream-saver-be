from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
import logging
from src.core.settings.configurations.config import settings
from src.api.routers.routes import router as global_router
from src.database.base import Base
from src.database.sessions.session import engine
from src.database.sessions.mongo_client import client

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database schema (For relational databases)
Base.metadata.create_all(bind=engine)

def create_application() -> FastAPI:
    """Initialize FastAPI app with configurations."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="StreamSaver API for downloading videos & images from various platforms.",
        version=settings.VERSION,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS.split(","),
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(global_router, prefix=settings.API_URL_PREFIX)

    # Exception handlers
    register_exception_handlers(app)

    # Event handlers
    register_event_handlers(app)

    return app

def register_exception_handlers(app: FastAPI):
    """Handles exceptions globally."""
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP {exc.status_code}: {exc.detail} | {request.method} {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc.errors()} | {request.method} {request.url}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {str(exc)} | {request.method} {request.url}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred."},
        )

def register_event_handlers(app: FastAPI):
    """Handles startup and shutdown events."""
    @app.on_event("startup")
    async def startup_db_client():
        app.mongodb_client = client
        app.mongodb = app.mongodb_client.get_database(settings.MONGO_DB_NAME)
        logger.info("MongoDB client started successfully")

    @app.on_event("shutdown")
    async def shutdown_db_client():
        logger.info("Shutting down MongoDB client...")
        app.mongodb_client.close()
        logger.info("MongoDB client shutdown complete")

app = create_application()

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")
