import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import psutil
import os
from .config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_PUBLISH_INTERVAL, SessionLocal, logger
from dal.device_dao import DeviceDAO
from entities.device import DeviceStatusEnum

# Configurable system metric: cpu, ram, both (default: both)
SYSTEM_METRIC = os.getenv("SYSTEM_METRIC", "both").lower()

class MQTTPublisher:
    """Helper class to handle MQTT publication for devices"""
    
    def __init__(self):
        self.running = False
        self.MQTT_BROKER_HOST = MQTT_BROKER_HOST
        self.MQTT_BROKER_PORT = MQTT_BROKER_PORT
        self.MQTT_PUBLISH_INTERVAL = int(MQTT_PUBLISH_INTERVAL)
        self.client = mqtt.Client(client_id=f"publisher_{random.randint(1000, 9999)}")
        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT Broker!")
            print("✓ Connected to MQTT Broker")
        else:
            logger.error(f"Failed to connect, return code {rc}")
            print(f"✗ Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning(f"Disconnected from MQTT Broker with code {rc}")
        print(f"⚠ Disconnected from MQTT Broker")

    def start(self):
        """Start the publication loop"""
        self.running = True
        logger.info(f"MQTT Publisher starting - Broker: {self.MQTT_BROKER_HOST}:{self.MQTT_BROKER_PORT}")
        print(f"✓ MQTT Publisher service started - Interval: {self.MQTT_PUBLISH_INTERVAL}s", flush=True)
        
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        try:
            self.client.loop_start()
            logger.info(f"Connecting to {self.MQTT_BROKER_HOST}...")
            
            # Retry logic for initial connection
            max_retries = 30
            retry_count = 0
            connected = False
            
            while not connected and self.running and retry_count < max_retries:
                try:
                    self.client.connect(self.MQTT_BROKER_HOST, self.MQTT_BROKER_PORT, keepalive=60)
                    connected = True
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Connection failed ({retry_count}/{max_retries}), retrying in 2s: {e}")
                    print(f"⚠ Connection failed ({retry_count}/{max_retries}), retrying in 2s: {e}")
                    time.sleep(2)
            
            if not connected:
                raise Exception("Could not connect to MQTT Broker after multiple retries")
            self._publish_loop()
        except KeyboardInterrupt:
            logger.info("MQTT Publisher stopped by user")
            print("\n✗ MQTT Publisher stopped")
        except Exception as e:
            logger.error(f"MQTT Publisher error: {e}")
            print(f"✗ MQTT Publisher error: {e}")
        finally:
            self.running = False
            self.client.loop_stop()
            self.client.disconnect()
    
    def _publish_loop(self):
        while self.running:
            try:
                # Synchronisation : on sample les métriques système une seule fois pour tout le cycle
                system_metrics = {
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "ram_percent": psutil.virtual_memory().percent
                }
                logger.info(f"[BATCH_SYNC] New metrics sampled: {system_metrics}")
                print(f"DEBUG: [BATCH_SYNC] System metrics sampled: {system_metrics}", flush=True)
                
                self._publish_all_devices(system_metrics)
                time.sleep(self.MQTT_PUBLISH_INTERVAL)
            except Exception as e:
                logger.error(f"Error in publish loop: {e}")
                time.sleep(1)
    
    def _publish_all_devices(self, system_metrics=None):
        db = SessionLocal()
        try:
            devices = DeviceDAO.get_all(db, skip=0, limit=1000)
            if not devices:
                return
            for device in devices:
                if device.status == DeviceStatusEnum.ACTIVE or device.status == 'active':
                    self._publish_device_data(device, system_metrics)
        except Exception as e:
            logger.error(f"Error fetching devices: {e}")
        finally:
            db.close()
    
    def _publish_device_data(self, device, system_metrics=None):
        try:
            if not self.connected:
                return

            if device.type == 'temperature':
                value = round(random.uniform(15, 30), 2)
                unit = "°C"
            elif device.type == 'humidity':
                value = round(random.uniform(30, 80), 2)
                unit = "%"
            elif device.type == 'pressure':
                value = round(random.uniform(1000, 1050), 2)
                unit = "hPa"
            elif device.type == 'light':
                value = round(random.uniform(0, 100), 2)
                unit = "%"
            elif device.type == 'system':
                # Utilisation des métriques synchronisées s'il y en a
                if system_metrics:
                    value = system_metrics
                else:
                    # Fallback si pas de metrics passées
                    metrics = {}
                    if SYSTEM_METRIC in ("cpu", "both"):
                        metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)
                    if SYSTEM_METRIC in ("ram", "both"):
                        metrics["ram_percent"] = psutil.virtual_memory().percent
                    value = metrics if len(metrics) > 1 else list(metrics.values())[0]
                unit = "%"
            else:
                value = 0
                unit = ""
            
            message = {
                "device_id": device.device_id,
                "owner_id": getattr(device, "owner_id", None),
                "name": device.name,
                "type": device.type,
                "value": value,
                "unit": unit,
                "status": device.status,
                "location": device.location,
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.client.publish(device.mqtt_topic, json.dumps(message), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published to {device.mqtt_topic}: {value}{unit}")
            else:
                logger.error(f"Failed to publish to {device.mqtt_topic}, rc: {result.rc}")
        except Exception as e:
            logger.error(f"Error publishing device {device.device_id}: {e}")
