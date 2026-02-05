import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from controllers.auth_controller import router
from helpers.config import Base, engine, LocalSession
from dal.user_dao import create_user
from entities.user import User
from helpers.utils import hash_pwd

app = FastAPI(
    title="Authentication app",
    description="Micro service signing app"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create one time
Base.metadata.create_all(bind=engine)

def bootstrap_admin():
    session = LocalSession()
    try:
        # Configuration via variables d'environnement (plus sûr)
        admin_email = os.getenv("INITIAL_ADMIN_EMAIL", "admin@admin.com")
        admin_pwd = os.getenv("INITIAL_ADMIN_PASSWORD", "admin123!")

        # On vérifie si un admin existe déjà
        admin_exists = session.query(User).filter(User.is_admin == True).first()
        if not admin_exists:
            print(f"=== Seeding Protected Admin: {admin_email} ===")
            admin = User(
                email=admin_email,
                password=hash_pwd(admin_pwd), # Hachage Argon2 obligatoire
                is_admin=True
            )
            session.add(admin)
            session.commit()
            print("Admin created securely.")
    except Exception as e:
        print(f"Error bootstrapping admin: {e}")
    finally:
        session.close()

bootstrap_admin()
app.include_router(router)

# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)