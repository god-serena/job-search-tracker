from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import application_documents, applications, documents, resume, stats, tailoring

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Search Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(application_documents.router)
app.include_router(resume.router)
app.include_router(tailoring.router)
app.include_router(documents.router)
app.include_router(stats.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
