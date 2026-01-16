"""
Main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import tickets, emails
from app.database import initialize_database

# Create FastAPI app
app = FastAPI(
    title="Customer Quote Request System",
    description="Automated email processing and quote request management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tickets.router)
app.include_router(emails.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        initialize_database()
        print(f"[SUCCESS] Application started in {settings.environment.upper()} mode")
        print(f"[INFO] Email mode: {'Resend (Production)' if settings.is_production else 'Mock (Development)'}")
    except Exception as e:
        print(f"[ERROR] Error during startup: {e}")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Customer Quote Request API",
        "version": "1.0.0",
        "environment": settings.environment,
        "email_mode": "production" if settings.is_production else "development"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True
    )
