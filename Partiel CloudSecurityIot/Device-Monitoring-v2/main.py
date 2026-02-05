import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from controllers.metric_controller import router as metric_router
import uvicorn
import os

# 1. Configuration du serveur Socket.io
# Utilisation de Redis pour synchroniser les événements entre les réplicas (Scale-Out)
mgr = socketio.AsyncRedisManager('redis://redis:6379/1')

# On augmente la robustesse avec des timeouts explicites
sio = socketio.AsyncServer(
    client_manager=mgr,
    async_mode='asgi', 
    cors_allowed_origins='*',
    ping_timeout=60,
    ping_interval=25
)

# 2. Définition des événements
@sio.event
async def connect(sid, environ):
    print(f"DEBUG_v2: Client connecté (sid={sid})")

@sio.event
async def disconnect(sid):
    print(f"DEBUG_v2: Client déconnecté (sid={sid})")

@sio.on("new_metric")
async def handle_new_metric(sid, data):
    # Diffusion vers tous les clients (Dashboard)
    await sio.emit("metrics_live", data)

# 3. Microservice FastAPI
fastapi_app = FastAPI(title="Device Monitoring v2 - RealTime")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(metric_router)

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Mount static files to serve the dashboard assets
if os.path.exists("test"):
    fastapi_app.mount("/test", StaticFiles(directory="test", html=True), name="test")

@fastapi_app.get("/")
async def root():
    return FileResponse('test/index.html')

# Prometheus instrumentation
Instrumentator().instrument(fastapi_app).expose(fastapi_app)

# 4. Exportation de l'application combinée pour Uvicorn
# On utilise la méthode de wrapping la plus propre
# Le socketio_path doit correspondre au défaut du client (socket.io)
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path='socket.io')

if __name__ == "__main__":
    print("=== Lancement de l'API avec Socket.io Wrapper (v2) ===")
    uvicorn.run(app, host="0.0.0.0", port=8003)
