import os
import json
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime
import time
import socketio
from helpers.config import MONGO_URI, MQTT_BROKER_HOST, MQTT_BROKER_PORT
from entities.metric import Metric
from dal.metric_dal import MetricDAL
from helpers.logger import logger

class MQTTConsumer:
    """Helper class to handle MQTT consumption and storage in MongoDB + Socket.io emission"""
    
    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client["device_monitoring"]
        self.metrics_col = self.db["metrics"]
        self.metric_dal = MetricDAL(self.metrics_col)
        
        # MQTT Client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        
        # Socket.io Client (to talk to our own Monitoring API)
        self.sio = socketio.Client()
        self.api_url = os.getenv("MONITORING_API_URL", "http://monitoring_api:8000")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connecté au broker avec succès (code={rc})")
            client.subscribe("cloud-security-iot/#")
        else:
            logger.error(f"Échec de connexion au broker (code={rc})")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"Message reçu sur topic '{msg.topic}': {payload}")
            
            # 1. Préparation de la métrique
            owner_id = payload.get("owner_id")
            if owner_id is not None:
                try: owner_id = int(owner_id)
                except Exception: owner_id = None
            
            timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()
            
            metric = Metric(
                device_id=payload.get("device_id"),
                owner_id=owner_id,
                metric_type=payload.get("type") or payload.get("metric_type"),
                value=payload.get("value"),
                unit=payload.get("unit"),
                timestamp=timestamp
            )
            
            # 2. Stockage MongoDB
            if metric.device_id and metric.metric_type:
                self.metric_dal.insert_metric(metric)
                logger.debug(f"[MongoDB] Métrique insérée: {metric.device_id}")
                
                # 3. Émission Temps Réel via Socket.io
                if self.sio.connected:
                    self.sio.emit('new_metric', payload)
                    logger.info(f"[Socket.io] Métrique diffusée en temps réel")
            else:
                logger.warning(f"Payload de métrique invalide: {payload}")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message: {e}")

    def connect_sio(self):
        """Connect to the Socket.io server (API)"""
        max_retries = 10
        for i in range(max_retries):
            try:
                logger.info(f"Tentative de connexion Socket.io à {self.api_url}")
                self.sio.connect(self.api_url)
                logger.info("✓ Connecté au serveur Socket.io (API)")
                return True
            except Exception as e:
                logger.warning(f"⚠ Échec connexion Socket.io ({i+1}/{max_retries}): {e}")
                time.sleep(3)
        return False

    def start(self):
        """Start both MQTT and Socket.io clients"""
        # Connexion Socket.io en premier (optionnel mais utile pour le debug)
        self.connect_sio()
        
        # Connexion MQTT
        while True:
            try:
                logger.info(f"Tentative de connexion MQTT à {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
                self.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
                break
            except Exception as e:
                logger.error(f"Connexion MQTT échouée: {e}. Nouvelle tentative dans 5s...")
                time.sleep(5)
        
        self.mqtt_client.loop_forever()
