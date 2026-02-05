# Device-Management-v2

Service de gestion de la configuration des devices IoT et systèmes pour Cloud Security IoT.

## Architecture

- **Responsabilité**: Gérer la configuration des devices uniquement
- **Devices**: Agents autonomes qui publient leurs résultats au broker MQTT
- **ms_monitoring**: Récupère et stocke les résultats depuis le broker MQTT

## Structure

```
Device-Management-v2/
├── entities/          - Modèles de données (Device)
├── dto/              - Validation des données (Pydantic)
├── dal/              - Accès aux données (CRUD)
├── controllers/      - Endpoints REST
├── helpers/          - Configuration et dépendances
├── sql/              - Schéma PostgreSQL
├── test/             - Tests HTTP
├── main.py           - Point d'entrée FastAPI
├── requirements.txt  - Dépendances Python
└── docker-compose.yml - Orchestration des services
```

## Endpoints

### Devices
- `POST /devices` - Créer un device
- `GET /devices` - Lister tous les devices (paginated)
- `GET /devices/count` - Compter le total
- `GET /devices/{id}` - Récupérer un device
- `GET /devices/owner/{email}` - Devices d'un propriétaire
- `GET /devices/type/{type}` - Devices d'un type
- `PUT /devices/{id}` - Mettre à jour
- `DELETE /devices/{id}` - Supprimer
- `POST /devices/{id}/heartbeat` - Mettre à jour last_seen

### Health
- `GET /health` - Vérifier le statut du service

## Types de devices

- `temperature` - Capteur de température
- `humidity` - Capteur d'humidité
- `pressure` - Capteur de pression
- `light` - Capteur de lumière
- `system` - Machine/serveur (CPU/RAM/disk)

## Statuts

- `active` - Device actif
- `inactive` - Device inactif

## MQTT Topics (auto-générés)

- IoT: `cloud-security-iot/iot/{type}/{device_id}`
- System: `cloud-security-iot/system/metrics/{device_id}`

## Configuration

Variables d'environnement:
- `DATABASE_URL` - URL PostgreSQL
- `MQTT_BROKER_HOST` - Host du broker MQTT (défaut: mosquitto)
- `MQTT_BROKER_PORT` - Port du broker MQTT (défaut: 1883)
- `MQTT_PUBLISH_INTERVAL` - Délai de publication en secondes (défaut: 30)

## Démarrage

```bash
# Avec Docker Compose
docker-compose up -d

# En développement local
pip install -r requirements.txt
uvicorn main:app --reload
```

## Base de données

PostgreSQL avec une table unique `t_devices` contenant la configuration de tous les devices.

Les résultats et métriques sont stockés dans `ms_monitoring`.
