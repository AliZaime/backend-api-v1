from datetime import datetime
from typing import Optional

class Metric:
    def __init__(self, device_id: str, owner_id: int, metric_type: str, value: float, unit: str, timestamp: Optional[str] = None):
        self.device_id = device_id
        self.owner_id = owner_id
        self.metric_type = metric_type
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "owner_id": self.owner_id,
            "metric_type": self.metric_type,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp
        }
