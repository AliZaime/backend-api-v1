from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from dal.metric_dal import MetricDAL
import os
from jose import jwt
from helpers.logger import logger
from dto.metric_dto import MetricDTO
from entities.metric import Metric

router = APIRouter(prefix="/metrics", tags=["metrics"])
http_bearer = HTTPBearer()

MONGO_URI = os.getenv("MONGODB_URL", os.getenv("MONGO_URI", "mongodb://monitoring-mongo:27017"))
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["device_monitoring"]
metrics_col = db["metrics"]
metric_dal = MetricDAL(metrics_col)

import requests

def check_token(token: HTTPAuthorizationCredentials = Depends(http_bearer)):
    """Vérifier le token via le microservice d'Auth (qui consulte Redis)"""
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/users/verify-token",
            json={"token": token.credentials},
            timeout=5
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Session expirée ou banni")
        
        return response.json()["payload"]
    except Exception as e:
        logger.error(f"Erreur vérification token: {e}")
        raise HTTPException(status_code=401, detail="Service d'authentification injoignable")

@router.get("/device/{device_id}")
def get_metrics_by_device(request: Request, device_id: str, skip: int = 0, limit: int = 50, token=Depends(check_token)):
    """Seul l'admin ou le propriétaire du device peut voir ces métriques"""
    is_admin = token.get("is_admin", False)
    user_id = token.get("id")

    logger.info('Get Metrics - Device - ID: %s - User: %s - IP: %s', device_id, token.get('sub'), request.client.host)
    try:
        # Récupération de la première métrique pour trouver l'owner (ou via management si on veut être strict)
        # Approche simple : On filtre directement par owner_id si on n'est pas admin
        query = {"device_id": device_id}
        if not is_admin:
            query["owner_id"] = user_id
            
        # Utilisation de la méthode spécifique DAL avec pagination
        if is_admin:
            # Si admin, on veut tout pour ce device
            metrics = metric_dal.get_by_device(device_id, skip, limit)
        else:
            # Si user, on filtre aussi par owner (implémenté dans le DAL ?)
            # Le DAL actuel get_by_device ne filtre pas par owner, donc on doit faire attention
            # Soit on modifie le DAL, soit on filtre ici. 
            # Comme on a ajouté le filtrage dans le code original avec query["owner_id"] = user_id
            # On va adapter l'appel direct à mongo ici pour la pagination custom sécurisée
            # OU MIEUX: on utilise le DAL si on lui fait confiance, mais ici le DAL get_by_device est simple.
            # Pour rester cohérent avec le DAL modifié:
            metrics = metric_dal.get_by_device(device_id, skip, limit)
            # MAIS ATTENTION: get_by_device ne vérifie pas l'owner_id dans le DAL modifié ci-dessus.
            # Sécurité: Si on est pas admin, on doit vérifier que le device appartient au user.
            # On va récupérer le latest pour vérifier l'owner, ou faire une query custom.
            
            # Approche sure: Ré-implémenter la query avec pagination ici pour respecter la logique de sécurité précédente
            # ou ajouter check_owner au DAL.
            # Vu le code précédent, il faisait metric_dal.collection.find(query)
            
            cursor = metric_dal.collection.find(query, {"_id": 0}).sort("timestamp_dt", -1).skip(skip).limit(limit)
            metrics = list(cursor)
        
        if not metrics and not is_admin:
             return []
            
        return metrics
    except Exception as e:
        logger.error('Get Metrics - Device - Failed - Device: %s - IP: %s - Error: %s', device_id, request.client.host, str(e))
        raise HTTPException(status_code=500, detail="Erreur récupération métriques")

@router.get("/owner/{owner_id}")
def get_metrics_by_owner(request: Request, owner_id: int, skip: int = 0, limit: int = 50, token=Depends(check_token)):
    """Seul l'admin ou le propriétaire peut voir ces métriques"""
    is_admin = token.get("is_admin", False)
    user_id = token.get("id")

    if not is_admin and owner_id != user_id:
        logger.warning('Get Metrics - Owner - Access Denied - Target: %s - User: %s - IP: %s', owner_id, token.get('sub'), request.client.host)
        raise HTTPException(status_code=403, detail="Accès non autorisé aux données d'un tiers")
    
    logger.info('Get Metrics - Owner - Success - Target: %s - User: %s - IP: %s', owner_id, token.get('sub'), request.client.host)
    try:
        metrics = metric_dal.get_by_owner(owner_id, skip, limit)
        return metrics
    except Exception as e:
        logger.error('Get Metrics - Owner - Failed - Target: %s - IP: %s - Error: %s', owner_id, request.client.host, str(e))
        raise HTTPException(status_code=500, detail="Erreur récupération métriques")

@router.get("/type/{metric_type}")
def get_metrics_by_type(request: Request, metric_type: str, skip: int = 0, limit: int = 50, token=Depends(check_token)):
    logger.info('Get Metrics - Type - Request - Type: %s - User: %s - IP: %s', metric_type, token.get('sub'), request.client.host)
    try:
        metrics = metric_dal.get_by_type(metric_type, skip, limit)
        logger.info('Get Metrics - Type - Success - Type: %s - Count: %d - IP: %s', metric_type, len(metrics), request.client.host)
        return metrics
    except Exception as e:
        logger.error('Get Metrics - Type - Failed - Type: %s - IP: %s - Error: %s', metric_type, request.client.host, str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des métriques")

@router.get("/latest/{device_id}")
def get_latest_metric(request: Request, device_id: str, token=Depends(check_token)):
    """Dernière valeur d'un device (avec vérification owner)"""
    is_admin = token.get("is_admin", False)
    user_id = token.get("id")

    try:
        metric = metric_dal.get_latest(device_id)
        if not metric:
            raise HTTPException(status_code=404, detail="Pas de données pour ce device")
            
        # Vérification RBAC
        if not is_admin and metric.get("owner_id") != user_id:
             logger.warning('Get Latest Metric - Access Denied - Device: %s - User: %s - IP: %s', device_id, token.get('sub'), request.client.host)
             raise HTTPException(status_code=403, detail="Accès non autorisé à ce device")
             
        return metric
    except HTTPException:
        raise
    except Exception as e:
        logger.error('Get Latest Metric - Failed - Device: %s - IP: %s - Error: %s', device_id, request.client.host, str(e))
        raise HTTPException(status_code=500, detail="Erreur récupération")
