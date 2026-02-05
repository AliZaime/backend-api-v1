from sqlalchemy.orm import Session
from sqlalchemy import func
from entities.device import Device, DeviceStatusEnum
from typing import Optional, List
from datetime import datetime
import uuid


class DeviceDAO:
    """Data Access Object pour les devices"""
    
    @staticmethod
    def generate_mqtt_topic(device_type: str, device_id: str) -> str:
        """Générer le topic MQTT en fonction du type et de l'ID du device"""
        if device_type == "system":
            return f"cloud-security-iot/system/metrics/{device_id}"
        else:
            return f"cloud-security-iot/iot/{device_type}/{device_id}"
    
    @staticmethod
    def create(db: Session, device_data: dict) -> Device:
        """Créer un nouveau device"""
        # Générer le topic MQTT automatiquement
        mqtt_topic = DeviceDAO.generate_mqtt_topic(
            device_data['type'],
            device_data['device_id']
        )
        device = Device(
            device_id=device_data['device_id'],
            name=device_data['name'],
            type=device_data['type'],
            location=device_data.get('location'),
            status=device_data.get('status', DeviceStatusEnum.ACTIVE),
            owner_id=device_data['owner_id'],
            mqtt_topic=mqtt_topic,
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    def get_by_id(db: Session, device_id: int) -> Optional[Device]:
        """Récupérer un device par son ID"""
        return db.query(Device).filter(Device.id == device_id).first()
    
    @staticmethod
    def get_by_device_id(db: Session, device_id: str) -> Optional[Device]:
        """Récupérer un device par son device_id"""
        return db.query(Device).filter(Device.device_id == device_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 10, device_type: Optional[str] = None) -> List[Device]:
        """Récupérer tous les devices avec pagination (optionnellement par type)"""
        query = db.query(Device)
        if device_type:
            query = query.filter(Device.type == device_type)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 10, device_type: Optional[str] = None) -> List[Device]:
        """Récupérer tous les devices d'un propriétaire (optionnellement par type)"""
        query = db.query(Device).filter(Device.owner_id == owner_id)
        if device_type:
            query = query.filter(Device.type == device_type)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_type(db: Session, device_type: str, skip: int = 0, limit: int = 10) -> List[Device]:
        """Récupérer tous les devices d'un certain type"""
        return db.query(Device).filter(
            Device.type == device_type
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_all(db: Session) -> int:
        """Compter le nombre total de devices"""
        return db.query(func.count(Device.id)).scalar()
    
    @staticmethod
    def count_by_owner(db: Session, owner_id: int) -> int:
        """Compter le nombre de devices d'un propriétaire"""
        return db.query(func.count(Device.id)).filter(
            Device.owner_id == owner_id
        ).scalar()
    
    @staticmethod
    def update(db: Session, device_id: int, **kwargs) -> Optional[Device]:
        """Mettre à jour un device (utilise kwargs pour flexibilité)"""
        device = DeviceDAO.get_by_id(db, device_id)
        if not device:
            return None
        
        # Mettre à jour uniquement les champs fournis
        for key, value in kwargs.items():
            if hasattr(device, key) and key not in ['id', 'device_id', 'mqtt_topic', 'created_at']:
                setattr(device, key, value)
        
        device.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    def update_last_seen(db: Session, device_id: int) -> Optional[Device]:
        """Mettre à jour le timestamp last_seen"""
        device = DeviceDAO.get_by_id(db, device_id)
        if not device:
            return None
        
        device.last_seen = datetime.utcnow()
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    def delete(db: Session, device_id: int) -> bool:
        """Supprimer un device"""
        device = DeviceDAO.get_by_id(db, device_id)
        if not device:
            return False
        
        db.delete(device)
        db.commit()
        return True
    
    @staticmethod
    def device_exists(db: Session, device_id: str) -> bool:
        """Vérifier si un device existe"""
        return db.query(Device).filter(Device.device_id == device_id).first() is not None
