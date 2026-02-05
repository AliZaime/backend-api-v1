from pydantic import BaseModel, Field
from typing import Optional

class MetricDTO(BaseModel):
    device_id: str = Field(..., description="Identifiant du device")
    owner_id: int = Field(..., description="ID du propriétaire")
    metric_type: str = Field(..., description="Type de métrique (cpu, temperature, etc.)")
    value: float = Field(..., description="Valeur mesurée")
    unit: str = Field(..., description="Unité de la mesure")
    timestamp: Optional[str] = Field(None, description="Horodatage ISO8601")

    class Config:
        schema_extra = {
            "example": {
                "device_id": "c2a1e2b6-...-4f8b",
                "owner_id": 1,
                "metric_type": "cpu",
                "value": 42.1,
                "unit": "%",
                "timestamp": "2026-01-28T14:10:11.225486"
            }
        }
