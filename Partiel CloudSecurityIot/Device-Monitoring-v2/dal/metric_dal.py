from pymongo.collection import Collection
from typing import List, Optional
from entities.metric import Metric

class MetricDAL:
    def __init__(self, collection: Collection):
        self.collection = collection
        # Création d'un index TTL (Time To Live) de 7 jours
        self.collection.create_index("timestamp_dt", expireAfterSeconds=604800)
        # Index composé pour la recherche rapide par device et tri par date
        self.collection.create_index([("device_id", 1), ("timestamp_dt", -1)])
        # Index pour la recherche par owner
        self.collection.create_index("owner_id")

    def insert_metric(self, metric: Metric):
        data = metric.to_dict()
        # On ajoute une version "Date" du timestamp pour l'index TTL de MongoDB
        from datetime import datetime
        try:
            if isinstance(metric.timestamp, str):
                data["timestamp_dt"] = datetime.fromisoformat(metric.timestamp.replace("Z", ""))
            else:
                data["timestamp_dt"] = metric.timestamp
        except Exception:
            data["timestamp_dt"] = datetime.utcnow()
            
        self.collection.insert_one(data)

    def get_by_device(self, device_id: str, skip: int = 0, limit: int = 50) -> List[dict]:
        return list(self.collection.find({"device_id": device_id}, {"_id": 0}).sort("timestamp_dt", -1).skip(skip).limit(limit))

    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 50) -> List[dict]:
        return list(self.collection.find({"owner_id": owner_id}, {"_id": 0}).sort("timestamp_dt", -1).skip(skip).limit(limit))

    def get_by_type(self, metric_type: str, skip: int = 0, limit: int = 50) -> List[dict]:
        return list(self.collection.find({"metric_type": metric_type}, {"_id": 0}).sort("timestamp_dt", -1).skip(skip).limit(limit))

    def get_latest(self, device_id: str) -> Optional[dict]:
        return self.collection.find_one({"device_id": device_id}, sort=[("timestamp_dt", -1)], projection={"_id": 0})
