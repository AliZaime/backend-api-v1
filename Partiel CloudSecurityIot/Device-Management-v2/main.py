from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from helpers.config import Base, engine, API_TITLE, API_VERSION, API_DESCRIPTION
from controllers.device_controller import router as device_router

# Créer les tables
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(device_router)

# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)


@app.get("/health", tags=["health"])
def health_check():
    """Vérifier que le service est actif"""
    return {"status": "healthy", "service": "Device-Management-v2"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
