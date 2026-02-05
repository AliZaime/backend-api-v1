from pydantic import BaseModel, Field, validator
from typing import Optional
from entities.device import DeviceTypeEnum, DeviceStatusEnum


class DeviceCreateDTO(BaseModel):
    """DTO pour la création d'un device"""
    device_id: Optional[str] = Field(None, min_length=1, max_length=100, description="Identifiant unique du device (auto si absent)")
    name: str = Field(..., min_length=1, max_length=100, description="Nom du device")
    type: DeviceTypeEnum = Field(..., description="Type de device (temperature, humidity, pressure, light, system)")
    location: Optional[str] = Field(None, max_length=200, description="Localisation du device")
    owner_id: int = Field(..., description="ID du propriétaire (user id)")
    
    class Config:
        use_enum_values = True


class DeviceUpdateDTO(BaseModel):
    """DTO pour la mise à jour d'un device"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    status: Optional[DeviceStatusEnum] = Field(None)
    
    class Config:
        use_enum_values = True


class DeviceResponseDTO(BaseModel):
    """DTO pour la réponse d'un device"""
    id: int
    device_id: str
    name: str
    type: str
    location: Optional[str]
    status: str
    owner_id: int
    mqtt_topic: str
    created_at: Optional[str]
    updated_at: Optional[str]
    last_seen: Optional[str]
    
    class Config:
        from_attributes = True
