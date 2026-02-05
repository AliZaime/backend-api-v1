"""
Service MQTT pour publier les données des devices
Désormais architecturé via helpers/mqtt_publisher.py
"""
import sys
import os

# Ajout du dossier courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from helpers.mqtt_publisher import MQTTPublisher

if __name__ == "__main__":
    print("=== MQTT Publisher Service Starting ===", flush=True)
    publisher = MQTTPublisher()
    publisher.start()
