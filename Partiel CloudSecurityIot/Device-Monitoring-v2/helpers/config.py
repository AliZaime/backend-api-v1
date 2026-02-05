import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")

# MQTT Configuration
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "rabbitmq")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["device_monitoring"]
metrics_col = db["metrics"]
