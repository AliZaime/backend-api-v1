import sys

# Configuration par défaut
MQTT_HOST = "localhost"
MQTT_PORT = 1883
DEFAULT_TOPIC = "cloud-security-iot/#"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        topic = userdata.get("topic", DEFAULT_TOPIC)
        print(f"✅ Connecté au Broker MQTT ({MQTT_HOST})")
        print(f"📡 Écoute sur le topic : {topic}")
        print("-" * 50)
        client.subscribe(topic)
    else:
        print(f"❌ Échec de connexion, code : {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_id = payload.get("device_id", "N/A")
        device_type = payload.get("type", "N/A")
        value = payload.get("value", "N/A")
        unit = payload.get("unit", "")
        
        print(f"🕒 [{payload.get('timestamp', 'no-time')}]")
        print(f"🔹 Topic : {msg.topic}")
        print(f"🔹 Device: {device_id} ({device_type})")
        print(f"📈 Valeur: {value} {unit}")
        print("-" * 30)
    except Exception as e:
        print(f"⚠️ Message brut sur {msg.topic} : {msg.payload.decode()}")

if __name__ == "__main__":
    # Récupération du topic via paramètre
    target_topic = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TOPIC
    
    client = mqtt.Client(userdata={"topic": target_topic})
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n👋 Arrêt du script.")
    except Exception as e:
        print(f"🚨 Erreur: {e}")
