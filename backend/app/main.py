from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.models import models  # noqa: F401 - registers SQLAlchemy models
from app.api import projects, analysis, questions

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(questions.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "codelens-ai-backend"}
