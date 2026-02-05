# Guide : Interroger RabbitMQ pour les métriques

Pour voir les métriques envoyées dans vos topics MQTT via le terminal, vous avez plusieurs options.

## 1. Utiliser le client MQTT en ligne de commande (Mosquitto)

Si vous avez `mosquitto-clients` installé sur votre machine :

```bash
# Écouter tous les topics de votre projet
mosquitto_sub -h localhost -p 1883 -t "cloud-security-iot/#" -v
```

## 2. Via Docker (si RabbitMQ est dans un conteneur)

Vous pouvez utiliser `rabbitmqadmin` à l'intérieur du conteneur pour lister les files d'attente ou les échanges, mais pour voir les _messages MQTT_, il est plus simple d'utiliser l'interface de gestion ou un script.

Pour voir les échanges (exchanges) créés par le plugin MQTT :

```bash
docker exec iot-rabbitmq rabbitmqctl list_exchanges
```

## 3. Script Python "Peek" (Recommandé)

J'ai créé un script utilitaire dans `test/peek_metrics.py` qui formate joliment les données en temps réel.

**Pour le lancer :**

```bash
python test/peek_metrics.py
```

## 4. Interface de Gestion RabbitMQ (Web)

Pour une vue visuelle, ouvrez votre navigateur :

- **URL** : [http://localhost:15672](http://localhost:15672)
- **Login** : `guest` (ou vos credentials dans `.env`)
- **Password** : `guest`
- Allez dans l'onglet **Exchanges** et cherchez `amq.topic`.
