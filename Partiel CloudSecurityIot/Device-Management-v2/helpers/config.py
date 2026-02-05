import os
from typing import Final
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging

# ==================== VARIABLES D'ENVIRONNEMENT ====================
# MQTT
MQTT_BROKER_HOST: Final[str] = os.getenv("MQTT_BROKER_HOST", "rabbitmq")
MQTT_BROKER_PORT: Final[int] = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_PUBLISH_INTERVAL: Final[int] = int(os.getenv("MQTT_PUBLISH_INTERVAL", "30"))

# JWT & Authentification
SECRET_KEY: Final[str] = os.getenv("SECRET_KEY", "$argon2id$v=19$m=65536,t=3,p=4$hT18aCPZ5AFxQ2ncYkRkWg$5UvBttA1brZmn6Bmf1T0NgKaYaqUzMV1pvWNxDp5pFc")
EXPIRE_TIME: Final[str] = os.getenv("EXPIRE_TIME", "30")

# Base de données
# On privilégie DATABASE_URL si elle est définie (Docker Compose / K8S)
DEFAULT_DB_URL = f'postgresql+psycopg2://admin:1234@management-db:5432/db_devices'
DATABASE_URL: Final[str] = os.getenv('DATABASE_URL', DEFAULT_DB_URL)
# Compatibilité avec anciens noms si besoin, bien que DATABASE_URL soit standard
if not DATABASE_URL.startswith("postgresql+psycopg2://") and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# FastAPI
API_TITLE: Final[str] = "Device-Management-v2"
API_VERSION: Final[str] = "1.0.0"
API_DESCRIPTION: Final[str] = "Microservice de gestion des devices IoT et système pour Cloud Security IoT"

# Services externes
AUTH_SERVICE_URL: Final[str] = os.getenv("AUTH_SERVICE_URL", "http://auth-ms:8000")

# ==================== SQLALCHEMY ====================
engine = create_engine(DATABASE_URL, echo=False, pool_size=10)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ==================== DEPENDENCY ====================
def get_db():
    """Dépendance FastAPI pour la session PostgreSQL"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== LOGS ====================
import os
os.makedirs('./logs', exist_ok=True)
formatter = logging.Formatter(fmt='%(asctime)s-%(levelname)s-%(message)s')
handler = logging.FileHandler('./logs/device_management.log')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)
