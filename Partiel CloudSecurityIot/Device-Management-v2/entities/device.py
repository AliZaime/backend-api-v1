from helpers.config import Base
from sqlalchemy import Column, String, Integer, DateTime, func, Enum
import enum


class DeviceTypeEnum(str, enum.Enum):
    """Types de devices IoT supportés"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    LIGHT = "light"
    SYSTEM = "system"


class DeviceStatusEnum(str, enum.Enum):
    """Statuts possibles d'un device"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class Device(Base):
    """
    Modèle de données pour un device (capteur IoT ou hôte système)
    Gère la configuration uniquement - les métriques sont stockées dans ms_monitoring
    """
    __tablename__ = 't_devices'
    
    # Identifiants
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    device_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Informations du device
    name = Column(String(100), nullable=False)
    type = Column(
        Enum(
            DeviceTypeEnum,
            values_callable=lambda obj: [e.value for e in obj],
            name="devicetypeenum",
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    location = Column(String(200), nullable=True)
    status = Column(
        Enum(
            DeviceStatusEnum,
            values_callable=lambda obj: [e.value for e in obj],
            name="devicestatusenum",
            native_enum=True,
            validate_strings=True,
        ),
        default=DeviceStatusEnum.ACTIVE,
        nullable=False,
    )
    
    # Propriétaire (référence à l'utilisateur du backend-api-v1)
    owner_id = Column(Integer, nullable=False, index=True)
    
    # Configuration MQTT
    mqtt_topic = Column(String(200), nullable=False)
    
    # Métadonnées temporelles
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    last_seen = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convertir l'objet Device en dictionnaire"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'type': self.type.value if self.type else None,
            'location': self.location,
            'status': self.status.value if self.status else None,
            'owner_id': self.owner_id,
            'mqtt_topic': self.mqtt_topic,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
        }
