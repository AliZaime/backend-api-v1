from fastapi import APIRouter, Depends, HTTPException, Query, Security, Request
from typing import List, Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dto.device_dto import DeviceCreateDTO, DeviceUpdateDTO, DeviceResponseDTO
from dal.device_dao import DeviceDAO
from helpers.config import get_db, AUTH_SERVICE_URL
from helpers.utils import decode_token, publish_mqtt_message
import requests
from datetime import datetime
import logging

router = APIRouter(prefix="/devices", tags=["devices"])
http_bearer = HTTPBearer()

# Logger setup
logger = logging.getLogger("device_management")

def check_token(token: HTTPAuthorizationCredentials = Security(http_bearer)):
    """Vérifier le token via le microservice d'Auth (qui consulte Redis)"""
    credentials = token.credentials
    try:
        # Appel au microservice d'Auth pour validation centrale
        response = requests.post(
            f"{AUTH_SERVICE_URL}/users/verify-token",
            json={"token": credentials},
            timeout=5
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Session expirée ou bannie")
        
        return response.json()["payload"]
    except Exception as e:
        logger.error(f"Erreur vérification token: {e}")
        raise HTTPException(status_code=401, detail="Service d'authentification injoignable")

@router.post("", response_model=DeviceResponseDTO, status_code=201)
@router.post("/", response_model=DeviceResponseDTO, status_code=201)
def create_device(
    request: Request,
    device: DeviceCreateDTO,
    db: Session = Depends(get_db),
    payload = Depends(check_token)
):
    """
    Créer un nouveau device
    """
    import uuid
    device_data = device.dict()
    # Générer un device_id UUID si non fourni ou vide
    if not device_data.get('device_id'):
        device_data['device_id'] = str(uuid.uuid4())
    # Vérifier unicité
    if DeviceDAO.device_exists(db, device_data['device_id']):
        logger.warning('Create Device - Failed - ID %s exists - IP: %s', device_data['device_id'], request.client.host)
        raise HTTPException(status_code=400, detail="Device avec cet ID existe déjà")
    try:
        created_device = DeviceDAO.create(db, device_data)
        # Publier le message MQTT de création
        mqtt_message = {
            "event": "device_created",
            "device_id": created_device.device_id,
            "name": created_device.name,
            "type": created_device.type,
            "status": created_device.status,
            "timestamp": datetime.now().isoformat()
        }
        publish_mqtt_message(created_device.mqtt_topic, mqtt_message)
        logger.info('Create Device - Success - ID: %s - User: %s - IP: %s', created_device.device_id, payload.get('sub'), request.client.host)
        return created_device.to_dict()
    except Exception as e:
        logger.error('Create Device - Failed - Error: %s - IP: %s', str(e), request.client.host)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{device_id}", response_model=DeviceResponseDTO)
def update_device(
    request: Request,
    device_id: int,
    device_update: DeviceUpdateDTO,
    db: Session = Depends(get_db),
    payload = Depends(check_token)
):
    """
    Mettre à jour un device (vérifie la propriété si non-admin)
    """
    device = DeviceDAO.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device non trouvé")
    
    # Vérification RBAC
    is_admin = payload.get("is_admin", False)
    user_id = payload.get("id")
    if not is_admin and device.owner_id != user_id:
        logger.warning('Update Device - Access Denied - Device: %s - User: %s - IP: %s', device_id, payload.get('sub'), request.client.host)
        raise HTTPException(status_code=403, detail="Accès non autorisé pour la modification")
    
    update_data = device_update.dict(exclude_unset=True)
    updated_device = DeviceDAO.update(db, device_id, **update_data)
    
    logger.info('Update Device - Success - ID: %s - Updated Fields: %s - IP: %s', device_id, list(update_data.keys()), request.client.host)
    return updated_device.to_dict()


@router.delete("/{device_id}", status_code=204)
def delete_device(request: Request, device_id: int, db: Session = Depends(get_db), payload = Depends(check_token)):
    """
    Supprimer un device (vérifie la propriété si non-admin)
    """
    device = DeviceDAO.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device non trouvé")
    
    # Vérification RBAC
    is_admin = payload.get("is_admin", False)
    user_id = payload.get("id")
    if not is_admin and device.owner_id != user_id:
        logger.warning('Delete Device - Access Denied - Device: %s - User: %s - IP: %s', device_id, payload.get('sub'), request.client.host)
        raise HTTPException(status_code=403, detail="Accès non autorisé pour la suppression")
    
    DeviceDAO.delete(db, device_id)
    logger.info('Delete Device - Success - ID: %s - By User: %s - IP: %s', device_id, payload.get('sub'), request.client.host)
    return None


@router.get("", response_model=List[DeviceResponseDTO])
@router.get("/", response_model=List[DeviceResponseDTO])
def list_devices(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    type: Optional[str] = Query(None, description="Filtrer par type de device"),
    db: Session = Depends(get_db),
    payload = Depends(check_token)
):
    """
    Lister les devices (Admin: tous, User: les siennes) - Supporte le filtrage par type
    """
    is_admin = payload.get("is_admin", False)
    user_id = payload.get("id")
    
    if is_admin:
        devices = DeviceDAO.get_all(db, skip=skip, limit=limit, device_type=type)
        logger.info('List Devices - Admin - User: %s - Type: %s - IP: %s', payload.get('sub'), type, request.client.host)
    else:
        devices = DeviceDAO.get_by_owner(db, owner_id=user_id, skip=skip, limit=limit, device_type=type)
        logger.info('List Devices - User - ID: %s - Type: %s - IP: %s', user_id, type, request.client.host)
    
    return [device.to_dict() for device in devices]


@router.get("/{device_id}", response_model=DeviceResponseDTO)
def get_device(
    request: Request,
    device_id: int,
    db: Session = Depends(get_db),
    payload = Depends(check_token)
):
    """
    Récupérer les détails d'un device (vérifie la propriété si non-admin)
    """
    device = DeviceDAO.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device non trouvé")
    
    # Vérification RBAC
    is_admin = payload.get("is_admin", False)
    user_id = payload.get("id")
    if not is_admin and device.owner_id != user_id:
        logger.warning('Get Device - Access Denied - Device: %s - User: %s - IP: %s', device_id, payload.get('sub'), request.client.host)
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return device.to_dict()


@router.post("/{device_id}/heartbeat", response_model=DeviceResponseDTO)
def update_heartbeat(device_id: int, db: Session = Depends(get_db), payload = Depends(check_token)):
    """
    Mettre à jour le heartbeat (last_seen) d'un device
    Utilisé pour indiquer que le device est actif
    - **device_id**: ID du device
    """
    device = DeviceDAO.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device non trouvé")
    
    updated_device = DeviceDAO.update_last_seen(db, device_id)
    
    # Publier le message MQTT de heartbeat
    mqtt_message = {
        "event": "heartbeat",
        "device_id": updated_device.device_id,
        "status": updated_device.status,
        "last_seen": updated_device.last_seen.isoformat() if updated_device.last_seen else None,
        "timestamp": datetime.now().isoformat()
    }
    publish_mqtt_message(updated_device.mqtt_topic, mqtt_message)
    
    return updated_device.to_dict()
