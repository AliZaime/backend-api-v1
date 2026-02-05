
from typing import Final
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
import logging
import os
#environement variables
EXPIRE_TIME:Final[str]=os.getenv("EXPIRE_TIME","30")
SECRET_KEY:Final[str]=os.getenv("SECRET_KEY","$argon2id$v=19$m=65536,t=3,p=4$hT18aCPZ5AFxQ2ncYkRkWg$5UvBttA1brZmn6Bmf1T0NgKaYaqUzMV1pvWNxDp5pFc")
REDIS_HOST: Final[str] = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT: Final[int] = int(os.getenv('REDIS_PORT', 6379))

# Base de données
# On privilégie DATABASE_URL si elle est définie (Docker Compose / K8S)
DEFAULT_DB_URL = f'postgresql+psycopg2://admin:1234@auth-db:5432/db_auth'
URL_DB: Final[str] = os.getenv('DATABASE_URL', DEFAULT_DB_URL)
# Compatibilité avec anciens noms si besoin, bien que DATABASE_URL soit standard
if not URL_DB.startswith("postgresql+psycopg2://") and URL_DB.startswith("postgresql://"):
    URL_DB = URL_DB.replace("postgresql://", "postgresql+psycopg2://", 1)
#sqlalchemy
engine=create_engine(URL_DB,pool_size=10)
LocalSession=sessionmaker(bind=engine)
Base=declarative_base()
def session_factory():
    session=LocalSession()
    try:
        yield session
    finally:
        session.close()
#logs
formater=logging.Formatter(fmt='%(asctime)s-%(levelname)s-%(message)s')
handler=logging.FileHandler('./logs/auth.log')
handler.setFormatter(formater)
logger=logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Redis config
import redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
