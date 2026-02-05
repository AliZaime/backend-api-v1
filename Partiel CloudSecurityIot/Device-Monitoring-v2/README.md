# Device-Monitoring-v2

Microservice FastAPI + MongoDB pour la collecte, le stockage et l'exposition des métriques IoT et systèmes.

## Fonctionnalités principales
- Consommation des messages MQTT (cloud-security-iot/#) et insertion en base MongoDB
- Endpoints REST pour requêter les métriques par device_id, owner_id, type, etc.
- Authentification JWT
- Docker Compose pour orchestration (API, MongoDB, consommateur)

## Schéma MongoDB (collection metrics)
- device_id (str, UUID)
- owner_id (int)
- metric_type (str)
- value (float)
- unit (str)
- timestamp (datetime)

## Endpoints REST
- GET /metrics/device/{device_id}
- GET /metrics/owner/{owner_id}
- GET /metrics/type/{metric_type}
- GET /metrics/latest/{device_id}

## Démarrage
```sh
docker-compose up -d
```

## Exemple de document
```json
{
  "device_id": "c2a1e2b6-...-4f8b",
  "owner_id": 1,
  "metric_type": "cpu",
  "value": 42.1,
  "unit": "%",
  "timestamp": "2026-01-28T14:10:11.225486"
}
```
