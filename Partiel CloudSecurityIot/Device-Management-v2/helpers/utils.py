from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from helpers.config import SECRET_KEY, EXPIRE_TIME, MQTT_BROKER_HOST, MQTT_BROKER_PORT
import paho.mqtt.client as mqtt
import json
import threading

def create_token(data: dict):
    """Créer un JWT token"""
    payload = data.copy()
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=int(EXPIRE_TIME))
    payload.update({
        "exp": expire_time,
        "iat": datetime.now(timezone.utc)
    })
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token: str):
    """Décoder et vérifier un JWT token"""
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload:
            return payload
    except JWTError as e:
        print(f"Erreur décodage token: {e}")
        return False
    return False

def publish_mqtt_message(topic: str, message: dict):
    """Publier un message MQTT de manière asynchrone"""
    def _publish():
        try:
            client = mqtt.Client()
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
            client.publish(topic, json.dumps(message), qos=1)
            client.disconnect()
            print(f"✓ MQTT message published to {topic}")
        except Exception as e:
            print(f"✗ MQTT publish error: {e}")
    
    # Publier en arrière-plan pour ne pas bloquer la réponse HTTP
    thread = threading.Thread(target=_publish, daemon=True)
    thread.start()
