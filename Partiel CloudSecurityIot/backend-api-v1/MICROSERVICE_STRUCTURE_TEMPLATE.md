# Microservice Backend Template

Cette fiche décrit la structure et les conventions à suivre pour tout nouveau microservice backend (FastAPI + SQLAlchemy + PostgreSQL + Docker/K8s). Adaptez le métier, gardez la forme.

## Arborescence de référence

```
project-root/
├── main.py                    # Point d'entrée FastAPI
├── requirements.txt           # Dépendances
├── Dockerfile                 # Image d'exécution
├── docker-compose.yml         # Orchestration locale
├── init.sql                   # Bootstrap base (optionnel)
├── README.md                  # Guide projet
│
├── controllers/               # Couche présentation (routes)
│   └── auth_controller.py     # Exemple : routes d'auth (à adapter)
│
├── dal/                       # Data Access Layer (requêtes DB)
│   └── user_dao.py            # Exemple : accès utilisateurs (à adapter)
│
├── dto/                       # Data Transfer Objects (Pydantic)
│   └── users_dto.py           # Exemple : schémas utilisateurs
│
├── entities/                  # Modèles ORM (SQLAlchemy)
│   └── user.py                # Exemple : entités User/Blacklist
│
├── helpers/                   # Utilitaires & config transverses
│   ├── config.py              # Connexion DB, logging, env
│   └── utils.py               # Sécurité (hash, JWT), helpers
│
├── test/                      # Tests (http ou pytest)
│   └── api_test.http
│
├── k8s/ (ou fichiers *.yaml)  # Manifests Kubernetes (deploy, svc, cm)
└── logs/                      # Sortie des logs applicatifs (montée en volume)
```

## Principes structurants
- **Layered** : Controller → DTO → DAL → Entity → DB
- **Stateless** : JWT pour l’auth, pas de sessions serveur
- **Sécurité** : Argon2 pour les mots de passe, tokens blacklistables
- **Config** : Tout via variables d’environnement (.env), jamais en dur
- **Logs** : Fichier dédié, format horodaté, niveau INFO minimum
- **Tests** : Fichier .http pour manuel, pytest pour auto

## Fichiers clés à reproduire
- `main.py` : crée l’app, enregistre les routers, lance uvicorn
- `helpers/config.py` : DB URL, engine, session factory, logging, secrets
- `helpers/utils.py` : hash/verify (Argon2), create/decode JWT, utilitaires
- `controllers/*.py` : routes FastAPI, dépendances de sécurité
- `dal/*.py` : requêtes SQLAlchemy, commits/rollback, no logique métier
- `entities/*.py` : Base declarative + tables
- `dto/*.py` : Schémas Pydantic (request/response)
- `docker-compose.yml` : service app + service DB, réseau bridge, volume logs
- `Dockerfile` : image slim, user non-root, install deps, cmd uvicorn

## Conventions sécurité (CRITICAL)

### 1️⃣ Hachage/Vérification des mots de passe (OBLIGATOIRE)
```python
# helpers/utils.py : fonctions prêtes à l'emploi
def hash_pwd(password: str) -> str:
    return pwd_hash.hash(password)  # Argon2id

def verify_pwd(hash_password: str, password: str) -> bool:
    return pwd_hash.verify(hash_password, password)  # Timing-safe
```
**À l'inscription** : appeler `hash_pwd()` avant de stocker le mot de passe  
**À l'authentification** : récupérer l'utilisateur par email, puis vérifier le hash avec `verify_pwd()`  
**Ne jamais** : comparer des mots de passe en clair en base  

### 2️⃣ Secret Key depuis l'environnement (OBLIGATOIRE)
```python
# helpers/config.py
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be provided in environment variables")
```
**Jamais** de valeur par défaut en production  
**Générer** une clé aléatoire sécurisée au déploiement (ex. `openssl rand -hex 32`)  
**Passer** via `.env` (dev), Docker Secrets ou K8s Secret (prod)  

### 3️⃣ Rate Limiting minimal (FORTEMENT RECOMMANDÉ)
Installer `slowapi` :
```bash
pip install slowapi
```
Ajouter en début de `main.py` :
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Dans controllers :
@router.post("/auth")
@limiter.limit("5/minute")
def authenticate_user(...):
    ...

@router.post("/add")
@limiter.limit("3/minute")
def register_user(...):
    ...
```
Protège contre les attaques par brute-force sur authentification et inscription.

### Autres sécurité
- JWT : HS256 avec `SECRET_KEY` fourni par l'env, exp court (ex: 30 min)
- Blacklist : table dédiée pour révoquer un token après logout
- CORS restreint si frontal distinct (accepter uniquement les origins connues)

## Conventions code
- Type hints obligatoires
- Docstrings sur fonctions publiques
- Exceptions HTTP via `HTTPException`
- Sessions SQLAlchemy fermées systématiquement (context ou dépendance)
- Pas de logique métier dans DAL, seulement accès données

## Conventions tests (OBLIGATOIRE pour 9/10)

Créer `tests/test_main.py` avec pytest + TestClient :

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Scénarios minimum

def test_register_success():
    """Inscription valide"""
    response = client.post("/users/add", json={
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_register_duplicate_email():
    """Email déjà utilisé"""
    client.post("/users/add", json={
        "email": "duplicate@example.com",
        "password": "Pass123"
    })
    response = client.post("/users/add", json={
        "email": "duplicate@example.com",
        "password": "OtherPass"
    })
    assert response.status_code == 401

def test_authenticate_success():
    """Authentification valide"""
    client.post("/users/add", json={
        "email": "auth@example.com",
        "password": "SecurePass123"
    })
    response = client.post("/users/auth", json={
        "email": "auth@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 200
    assert "token" in response.json()

def test_authenticate_invalid():
    """Identifiants invalides"""
    response = client.post("/users/auth", json={
        "email": "notfound@example.com",
        "password": "WrongPass"
    })
    assert response.status_code == 401

def test_protected_route_valid_token():
    """Accès route protégée avec JWT valide"""
    # S'authentifier pour obtenir token
    auth_response = client.post("/users/auth", json={
        "email": "auth@example.com",
        "password": "SecurePass123"
    })
    token = auth_response.json()["token"]
    
    # Accéder route protégée
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_protected_route_invalid_token():
    """Accès route protégée sans token"""
    response = client.get("/users/")
    assert response.status_code == 403

def test_token_expired():
    """Token expiré rejeté"""
    response = client.post("/users/verify-token", json={
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"
    })
    assert response.status_code == 404

def test_logout_blacklists_token():
    """Logout ajoute token à blacklist"""
    auth_response = client.post("/users/auth", json={
        "email": "auth@example.com",
        "password": "SecurePass123"
    })
    token = auth_response.json()["token"]
    
    # Logout
    response = client.post(
        "/users/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Token ne doit plus être accessible
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
```

**Exécuter les tests :**
```bash
pytest tests/ -v
```

Minimum requis : enregistrement, authentification, route protégée, logout/blacklist, tokens invalides.

## Déploiement
- Docker : monter `./logs` en volume, passer env (DB, SECRET_KEY, EXPIRE_TIME)
- Compose : dépendance DB, init.sql optionnel, ports exposés
- K8s : Deployment, Service (ClusterIP/NodePort), ConfigMap/Secret pour env, PVC si besoin

## Checklist démarrage (score 9/10)
- [ ] `.env` créé avec `USER_DB`, `PASSWORD_DB`, `NAME_DB`, `SERVER_DB`, `SECRET_KEY` (clé aléatoire, pas de default), `EXPIRE_TIME`
- [ ] `pip install -r requirements.txt` (inclut `slowapi` pour rate limiting)
- [ ] `docker-compose up -d` (ou uvicorn local)
- [ ] Vérifier Swagger `/docs`
- [ ] Tous les mots de passe **hachés en inscription** avec `hash_pwd()`
- [ ] Authentification compare via **`verify_pwd()`** (pas en clair)
- [ ] Rate limiting appliqué sur `/auth` et `/add`
- [ ] Tests exécutés : `pytest tests/ -v` (tous au vert)
- [ ] SECRET_KEY refusé de démarrer si absent en env (pas de valeur par défaut)

> **Objectif : 9/10 minimum**  
> Utilisez ce template comme squelette : remplacez les exemples (auth, users) par le domaine métier du nouveau microservice, en conservant la même organisation et les mêmes bonnes pratiques.  
> Les 4 correctifs critiques (hash pwd, secret key, rate limiting, tests) sont obligatoires pour atteindre 9/10.
