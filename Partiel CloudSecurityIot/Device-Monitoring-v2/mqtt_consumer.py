"""
Service de consommation MQTT
Désormais architecturé via helpers/mqtt_consumer_helper.py
"""
import sys
import os

# Ajout du dossier courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from helpers.mqtt_consumer_helper import MQTTConsumer

if __name__ == "__main__":
    print("=== MQTT Consumer Service Starting ===", flush=True)
    consumer = MQTTConsumer()
    consumer.start()
