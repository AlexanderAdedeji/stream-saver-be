import time
import uuid
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from src.api.routers import analytics_routes
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from slowapi import  _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from src.commonLib.utils.logger_config import logger
from src.core.settings.configurations.config import settings
from src.api.routers.routes import router as global_router
from src.database.base import Base
from src.database.sessions.session import engine
from src.limiter import limiter
from src.database.sessions.mongo_client import client




# Initialize database schema (For relational databases)
Base.metadata.create_all(bind=engine)

def create_application() -> FastAPI:
    """Initialize FastAPI app with configurations."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="StreamSaver API for downloading videos & images from various platforms.",
        version=settings.VERSION,
    )

    # Apply CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS.split(","),
        allow_headers=["*"],
    )

    # Apply Rate-Limiting Middleware
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)


    register_exception_handlers(app)


    register_event_handlers(app)


    app.include_router(global_router, prefix=settings.API_URL_PREFIX)

    return app

async def request_logging_middleware(request: Request, call_next):
    """Middleware to log all incoming API requests and response times."""
    start_time = time.time()
    trace_id = str(uuid.uuid4())  


    logger.info(f" [TRACE {trace_id}] {request.method} {request.url}")

    # Process request
    response = await call_next(request)

   
    duration = time.time() - start_time

  
    logger.info(f"📤 [TRACE {trace_id}] {request.method} {request.url} | Status: {response.status_code} | Time: {duration:.3f}s")

    return response

def register_exception_handlers(app: FastAPI):
    """Handles exceptions globally with detailed logging."""
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        trace_id = str(uuid.uuid4())
        logger.warning(f" [TRACE {trace_id}] HTTP {exc.status_code}: {exc.detail} | {request.method} {request.url}")

        return JSONResponse(
            status_code=exc.status_code,
            content={"trace_id": trace_id, "detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        trace_id = str(uuid.uuid4())
        logger.warning(f" [TRACE {trace_id}] Validation Error: {exc.errors()} | {request.method} {request.url}")

        return JSONResponse(
            status_code=422,
            content={"trace_id": trace_id, "detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        trace_id = str(uuid.uuid4())
        logger.error(f" [TRACE {trace_id}] Unhandled Error: {str(exc)} | {request.method} {request.url}")

        return JSONResponse(
            status_code=500,
            content={"trace_id": trace_id, "detail": "An unexpected error occurred."},
        )

def register_event_handlers(app: FastAPI):
    """Handles startup and shutdown events for database connections."""
    @app.on_event("startup")
    async def startup_db_client():
        """ MongoDB Connection on Startup"""
        try:
            app.mongodb_client = client
            app.mongodb = app.mongodb_client.get_database(settings.MONGO_DB_NAME)
            logger.info("  MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"  Failed to connect to MongoDB: {str(e)}")

    @app.on_event("shutdown")
    async def shutdown_db_client():
        """ MongoDB Connection on Shutdown"""
        logger.info(" 📴 Shutting down MongoDB client...")
        app.mongodb_client.close()
        logger.info(" MongoDB client shutdown complete")

    @app.middleware("http")
    async def performance_monitoring_middleware(request: Request, call_next):
        """Middleware to log API response times."""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(f" ⏱️ {request.method} {request.url} - Processed in {process_time:.3f}s")
        return response

app = create_application()

# Add Rate-Limit Exception Handler
app.add_exception_handler(429, _rate_limit_exceeded_handler)



@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")
