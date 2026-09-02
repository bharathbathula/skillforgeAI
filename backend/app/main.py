from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.api.endpoints import auth, resumes, jobdescription, analysis, ats

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include endpoints under /api/v1
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(resumes.router, prefix=f"{settings.API_V1_STR}/resumes", tags=["resumes"])
app.include_router(jobdescription.router, prefix=f"{settings.API_V1_STR}/jobdescription", tags=["jobdescription"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["analysis"])
app.include_router(ats.router, prefix=f"{settings.API_V1_STR}/ats", tags=["ats"])

@app.get("/")
def root():
    db_type = "PostgreSQL" if "postgresql" in settings.SQLALCHEMY_DATABASE_URI else "SQLite"
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "database_type": db_type,
        "db_uri": settings.SQLALCHEMY_DATABASE_URI.split("@")[-1] if "@" in settings.SQLALCHEMY_DATABASE_URI else settings.SQLALCHEMY_DATABASE_URI
    }
