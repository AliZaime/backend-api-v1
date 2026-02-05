# 📊 RAPPORT D'ANALYSE COMPLÈTE - BACKEND AUTHENTICATION API v1

**Date d'analyse:** 25 Janvier 2026  
**Projet:** Micro-service d'authentification  
**Type:** API REST avec FastAPI  
**Base de données:** PostgreSQL

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble générale](#vue-densemble)
2. [Architecture du projet](#architecture)
3. [Stack technologique](#stack-technologique)
4. [Structure des dossiers](#structure-des-dossiers)
5. [Composants clés](#composants-clés)
6. [Flux de données](#flux-de-données)
7. [Endpoints API](#endpoints-api)
8. [Gestion de la sécurité](#gestion-de-la-sécurité)
9. [Base de données](#base-de-données)
10. [Configuration et déploiement](#configuration-et-déploiement)
11. [Points forts](#points-forts)
12. [Points d'amélioration](#points-damélioration)
13. [Recommandations](#recommandations)

---

## 🎯 Vue d'ensemble

### Objectif principal
Ce backend est un **micro-service d'authentification** conçu pour gérer les opérations liées aux utilisateurs et à l'authentification dans une architecture Cloud/IoT. C'est un service autonome qui peut être intégré dans une plateforme plus grande.

### Fonctionnalités principales
- ✅ **Inscription des utilisateurs** - Création de nouveaux comptes
- ✅ **Authentification** - Vérification des identifiants et génération de tokens JWT
- ✅ **Vérification de tokens** - Validation des JWT sans dépendre de sessions
- ✅ **Gestion des rôles** - Support des utilisateurs normaux et administrateurs
- ✅ **Logout** - Blacklist des tokens pour éviter leur réutilisation
- ✅ **Gestion des logs** - Traçabilité des actions importantes

---

## 🏗️ Architecture du projet

### Modèle architectural : **Layered Architecture** (Architecture en couches)

```
┌─────────────────────────────────────────┐
│     CONTROLLERS (Couche présentation)   │  ← Gestion des requêtes HTTP
├─────────────────────────────────────────┤
│     HELPERS (Utilitaires & Config)      │  ← Outils partagés
├─────────────────────────────────────────┤
│        DTO (Data Transfer Objects)      │  ← Sérialisation/Validation
├─────────────────────────────────────────┤
│     DAL (Data Access Layer)             │  ← Requêtes base de données
├─────────────────────────────────────────┤
│     ENTITIES (Modèles de données)       │  ← Schémas SQL/ORM
├─────────────────────────────────────────┤
│     DATABASE (PostgreSQL)               │  ← Stockage persistant
└─────────────────────────────────────────┘
```

### Avantages de cette architecture
- **Séparation des responsabilités** : Chaque couche a un rôle spécifique
- **Testabilité** : Les couches peuvent être testées indépendamment
- **Maintenabilité** : Modifications faciles sans impact en cascade
- **Réutilisabilité** : Les composants peuvent être réutilisés

---

## 💻 Stack technologique

### Framework web
| Technologie | Version | Rôle |
|------------|---------|------|
| **FastAPI** | 0.123.7 | Framework web asynchrone, création d'API REST |
| **Uvicorn** | 0.38.0 | Serveur ASGI pour exécuter FastAPI |
| **Starlette** | 0.50.0 | Base de FastAPI pour le routage HTTP |

### Base de données
| Technologie | Version | Rôle |
|------------|---------|------|
| **PostgreSQL** | Alpine | SGBD relationnel principal |
| **SQLAlchemy** | 2.0.44 | ORM pour interaction avec la DB |
| **psycopg2-binary** | 2.9.11 | Driver PostgreSQL pour Python |

### Authentification & Sécurité
| Technologie | Version | Rôle |
|------------|---------|------|
| **python-jose** | 3.5.0 | Création et validation de JWT |
| **argon2-cffi** | 25.1.0 | Hachage sécurisé des mots de passe |
| **python-dotenv** | 1.2.1 | Gestion des variables d'environnement |

### Validation des données
| Technologie | Version | Rôle |
|------------|---------|------|
| **Pydantic** | 2.12.5 | Validation et sérialisation des données |
| **email-validator** | 2.3.0 | Validation des adresses email |

### Infrastructure & Logging
| Technologie | Version | Rôle |
|------------|---------|------|
| **Docker** | - | Conteneurisation de l'application |
| **docker-compose** | - | Orchestration multi-conteneurs |
| **Logging** | Built-in | Enregistrement des événements |

### Autres dépendances
- **sentry-sdk** 2.47.0 : Monitoring et gestion des erreurs
- **cryptography** 46.0.3 : Opérations cryptographiques
- **PyYAML** 6.0.3 : Parsing de fichiers YAML

---

## 📁 Structure des dossiers

```
backend-api-v1/
│
├── 📄 main.py                          ← Point d'entrée de l'application
├── 📄 requirements.txt                 ← Dépendances Python
├── 📄 Dockerfile                       ← Configuration Docker
├── 📄 docker-compose.yml               ← Orchestration des services
├── 📄 init.sql                         ← Script d'initialisation DB
├── 📄 README.md                        ← Documentation basique
│
├── 📦 controllers/                     ← Couche présentation (Endpoints)
│   ├── __init__.py
│   └── auth_controller.py              ← Tous les endpoints d'authentification
│
├── 📦 dal/                             ← Couche d'accès aux données
│   ├── __init__.py
│   ├── user_dao.py                     ← Opérations utilisateurs en DB
│   └── black_listed_dao.py             ← Gestion des tokens blacklistés
│
├── 📦 dto/                             ← Data Transfer Objects
│   ├── __init__.py
│   └── users_dto.py                    ← Schémas de requête/réponse
│
├── 📦 entities/                        ← Modèles de données (ORM)
│   ├── __init__.py
│   └── user.py                         ← Entités User et BlacklistToken
│
├── 📦 helpers/                         ← Utilitaires et configuration
│   ├── __init__.py
│   ├── config.py                       ← Configuration DB et logging
│   └── utils.py                        ← Fonctions de sécurité (JWT, hash)
│
├── 📦 test/                            ← Tests
│   └── api_test.http                   ← Tests manuels des endpoints
│
├── 🐳 Fichiers Kubernetes
│   ├── backend-deployment.yaml         ← Déploiement K8s du backend
│   ├── backend-service.yaml            ← Service K8s interne
│   ├── backend-service-nodeport.yaml   ← Service K8s exposé
│   ├── backend-cm0-configmap.yaml      ← ConfigMap pour la config
│   └── ...fichiers DB similaires

└── 📄 LICENSE
```

---

## 🔧 Composants clés

### 1. **main.py** - Point d'entrée

```python
# Initialisation FastAPI
app = FastAPI(
    title="Authentication app",
    description="Micro service signing app"
)

# Création des tables au démarrage
Base.metadata.create_all(bind=engine)

# Enregistrement du routeur d'authentification
app.include_router(router)

# Lancement du serveur
uvicorn.run("main:app", host="0.0.0.0", reload=True)
```

**Responsabilités:**
- Crée l'instance FastAPI
- Configure la base de données
- Enregistre les routes
- Lance le serveur ASGI sur le port 8000

---

### 2. **helpers/config.py** - Configuration centralisée

**Variables d'environnement gérées:**

| Variable | Défaut | Description |
|----------|--------|-------------|
| `EXPIRE_TIME` | 30 | Durée d'expiration du JWT (minutes) |
| `SECRET_KEY` | Valeur Argon2 | Clé secrète pour signer les JWT |
| `USER_DB` | admin | Utilisateur PostgreSQL |
| `PASSWORD_DB` | 1234 | Mot de passe PostgreSQL |
| `NAME_DB` | db_auth | Nom de la base de données |
| `SERVER_DB` | localhost | Adresse du serveur PostgreSQL |

**Configuration de la base de données:**

```python
# URL de connexion PostgreSQL
URL_DB = 'postgresql+psycopg2://admin:1234@localhost:5432/db_auth'

# Pool de connexions
engine = create_engine(URL_DB, pool_size=10)

# Gestion des sessions
LocalSession = sessionmaker(bind=engine)
```

**Système de logging:**
- Fichier de log : `./logs/auth.log`
- Format : `%(asctime)s-%(levelname)s-%(message)s`
- Niveau : INFO

---

### 3. **helpers/utils.py** - Fonctions de sécurité

#### Hachage des mots de passe (Argon2)

```python
def hash_pwd(password: str) -> str
  # Utilise Argon2id pour hacher de manière sécurisée
  # Argon2 : algorithme primé résistant aux attaques par GPU/ASIC
```

**Paramètres Argon2:**
- m=65536 (mémoire : 64 MB)
- t=3 (itérations)
- p=4 (parallélisme)

#### Vérification des mots de passe

```python
def verify_pwd(hash_password: str, password: str) -> bool
  # Vérification timing-safe contre le brute-force
```

#### Création de tokens JWT

```python
def create_token(data: dict) -> str
  # Crée un JWT avec :
  # - Données personnalisées (claims)
  # - Expiration (exp) : par défaut 30 minutes
  # - Date d'émission (iat)
  # - Algorithme : HS256 (HMAC-SHA256)
```

**Exemple de payload JWT:**
```json
{
  "sub": "utilisateur@email.com",
  "role": false,
  "exp": 1706163456,
  "iat": 1706161656
}
```

#### Décodage de tokens JWT

```python
def decode_token(token: str) -> dict | bool
  # Valide la signature et l'expiration
  # Retourne les données ou False si invalide
```

---

### 4. **controllers/auth_controller.py** - Endpoints API

Définit tous les points d'accès HTTP du service.

#### Middleware de sécurité

```python
def check_token(session, token):
  # Décode le token JWT
  # Vérifie qu'il n'est pas blacklisté
  # Retourne le payload ou lève une exception 401
```

Utilisé comme dépendance sur les routes protégées.

#### Endpoints disponibles

Prefix : `/users`

---

### 5. **entities/user.py** - Modèles de données

#### Table `t_users`

```python
class User:
  id: Integer         ← Clé primaire, auto-incrémentée
  email: String       ← Unique, indexée
  password: String    ← Stockée hachée (128 caractères)
  is_admin: Boolean   ← Défaut : False
  created_at: DateTime← Timestamp de création
  updated_at: DateTime← Timestamp de mise à jour
```

#### Table `t_blacklist_tokens`

```python
class BlacklistToken:
  id: Integer         ← Clé primaire
  token: String       ← Unique, le JWT complet
  blacklisted_on: DateTime← Timestamp du logout
```

---

### 6. **dal/user_dao.py** - Opérations utilisateurs

#### `create_user(session, user)` 
- Vérifie l'unicité de l'email
- Insère le nouvel utilisateur
- Retourne True/False

**Flux:**
```
Requête avec email
    ↓
Vérification email unique
    ↓ Unique → Insertion
    ↓ Doublon → Erreur
Commit / Rollback
```

#### `get_all_users(session)`
- Retourne tous les utilisateurs

#### `authenticate(session, user)`
- Cherche l'utilisateur par email ET mot de passe
- Retourne l'entité ou False

**Note:** Le mot de passe est comparé en clair (voir améliorations)

---

### 7. **dal/black_listed_dao.py** - Gestion de la blacklist

#### `is_blacklist_token(session, token)`
- Vérifie si un token est blacklisté
- Retourne True/False

#### `add_token_to_blacklist(session, token)`
- Ajoute un token à la blacklist
- Appelé au logout

---

### 8. **dto/users_dto.py** - Schémas de validation

Utilise Pydantic pour validation automatique.

#### `UserRequest`
```python
{
  "email": "user@example.com",  ← EmailStr (format email)
  "password": "secret123"        ← min_length=6
}
```

#### `UserResponse`
```python
{
  "email": "user@example.com",
  "is_admin": false,
  "created_at": "2024-01-25 10:30:45.123456",
  "updated_at": "2024-01-25 10:30:45.123456"
}
```

#### `TokenResponse`
```python
{
  "token": "eyJhbGc...",
  "payload": {
    "sub": "user@example.com",
    "role": false
  }
}
```

#### `TokenRequest`
```python
{
  "token": "eyJhbGc..."
}
```

---

## 🔄 Flux de données

### 1. **Flux d'inscription (POST /users/add)**

```
Client
  │
  ├─ Envoie : UserRequest {email, password}
  │
  ↓ [FastAPI valide avec Pydantic]
  │
Controller (auth_controller.py)
  │
  ├─ Crée entité User
  │
  ↓ [DAL]
  │
DAL (user_dao.py)
  │
  ├─ Vérifie email unique
  ├─ Insère en DB
  ├─ Commite la transaction
  │
  ↓ [ORM SQLAlchemy]
  │
PostgreSQL
  │
  ├─ Insère dans t_users
  │
  ↓ [Réponse]
  │
Controller
  │
  ├─ Retourne UserResponse
  │
  ↓
Client
  │
  └─ Reçoit : UserResponse {email, is_admin, created_at, updated_at}
```

### 2. **Flux d'authentification (POST /users/auth)**

```
Client
  │
  ├─ Envoie : UserRequest {email, password}
  │
  ↓
Controller
  │
  ├─ Crée entité User avec email et password
  │
  ↓
DAL (authenticate)
  │
  ├─ Query : SELECT * FROM t_users WHERE email = ? AND password = ?
  │
PostgreSQL
  │
  ├─ Retourne l'utilisateur ou None
  │
  ↓ [Controller vérifie le résultat]
  │
  ├─ Si trouvé : Crée JWT avec claims
  ├─ Si non trouvé : Lève HTTPException 401
  │
  ├─ JWT = encode({"sub": email, "role": is_admin}, SECRET_KEY, "HS256")
  │
  ↓
Client
  │
  └─ Reçoit : TokenResponse {token, payload}
```

**⚠️ PROBLÈME IDENTIFIÉ:** Le mot de passe est stocké et comparé en clair !
(Voir section "Points d'amélioration")

### 3. **Flux de vérification de token (POST /users/verify-token)**

```
Client
  │
  ├─ Envoie : TokenRequest {token}
  │
  ↓
Controller
  │
  ├─ Appelle decode_token(token)
  │
  ↓ [helpers/utils.py]
  │
  ├─ Valide la signature avec SECRET_KEY
  ├─ Vérifie l'expiration (exp)
  ├─ Retourne le payload ou False
  │
  ↓ [Controller vérifie]
  │
  ├─ Si valide : Retourne TokenResponse
  ├─ Si invalide : Lève HTTPException 404
  │
  ↓
Client
  │
  └─ Reçoit : TokenResponse {token, payload}
```

### 4. **Flux de logout (POST /users/logout)**

```
Client
  │
  ├─ Envoie : Authorization: Bearer eyJhbGc...
  │
  ↓ [Middleware check_token]
  │
  ├─ Décode le token
  ├─ Vérifie pas déjà blacklisté
  ├─ Retourne payload
  │
  ↓
Controller (logout_user)
  │
  ├─ Extrait le token du header
  │
  ↓ [DAL]
  │
DAL (black_listed_dao.py)
  │
  ├─ Insère dans t_blacklist_tokens
  │
PostgreSQL
  │
  ├─ Insère le token
  │
  ↓
Client
  │
  └─ Reçoit : 200 OK "logout successful"
```

### 5. **Flux d'accès ressource protégée (GET /users/)**

```
Client
  │
  ├─ Envoie : Authorization: Bearer eyJhbGc...
  │
  ↓ [Middleware check_token]
  │
  ├─ Décode le token
  ├─ Vérifie pas blacklisté
  ├─ Vérifie signature valide
  │
  ├─ ✓ Token valide → Retourne payload
  ├─ ✗ Token expiré/invalide → Lève 401
  ├─ ✗ Token blacklisté → Lève 401
  │
  ↓
Controller
  │
  ├─ Reçoit payload (claims)
  ├─ Récupère tous les utilisateurs
  ├─ Formate la réponse
  │
  ↓
Client
  │
  └─ Reçoit : List[UserResponse]
```

---

## 🔌 Endpoints API

### 1. **Inscription - POST `/users/add`**

**Requête:**
```http
POST /users/add HTTP/1.1
Content-Type: application/json

{
  "email": "nouveau@example.com",
  "password": "motdepasse123"
}
```

**Réponse réussie (200):**
```json
{
  "email": "nouveau@example.com",
  "is_admin": false,
  "created_at": "2024-01-25 10:30:45.123456",
  "updated_at": "2024-01-25 10:30:45.123456"
}
```

**Réponses d'erreur:**
- **400** : Email invalide ou mot de passe < 6 caractères (Pydantic)
- **401** : Email déjà utilisé

**Logs:** `user register ok {email}`

---

### 2. **Authentification - POST `/users/auth`**

**Requête:**
```http
POST /users/auth HTTP/1.1
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "motdepasse123"
}
```

**Réponse réussie (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwicm9sZSI6ZmFsc2UsImV4cCI6MTcwNjE2MzQ1NiwiaWF0IjoxNzA2MTYxNjU2fQ.abc123...",
  "payload": {
    "sub": "user@example.com",
    "role": false,
    "exp": 1706163456,
    "iat": 1706161656
  }
}
```

**Réponses d'erreur:**
- **400** : Format email/password invalide
- **401** : Identifiants incorrects

**Logs:** `Authetication for user ; {email}`

**Durée de validité du token:** 30 minutes (configurable)

---

### 3. **Vérification de token - POST `/users/verify-token`**

**Requête:**
```http
POST /users/verify-token HTTP/1.1
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Réponse réussie (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "payload": {
    "sub": "user@example.com",
    "role": false,
    "exp": 1706163456,
    "iat": 1706161656
  }
}
```

**Réponses d'erreur:**
- **404** : Token invalide ou expiré

**Cas d'usage:** Validation côté client du token sans appel à une ressource protégée

---

### 4. **Récupération d'utilisateurs - GET `/users/`**

**Requête:**
```http
GET /users/ HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Réponse réussie (200):**
```json
[
  {
    "email": "user1@example.com",
    "is_admin": false,
    "created_at": "2024-01-20 08:15:30.123456",
    "updated_at": "2024-01-20 08:15:30.123456"
  },
  {
    "email": "admin@example.com",
    "is_admin": true,
    "created_at": "2024-01-15 09:00:00.123456",
    "updated_at": "2024-01-15 09:00:00.123456"
  }
]
```

**Réponses d'erreur:**
- **401** : Token invalide/expiré/blacklisté
- **404** : Token format invalide

**Protection:** Nécessite un JWT valide

**Logs:** `get all users from ip :`

---

### 5. **Logout - POST `/users/logout`**

**Requête:**
```http
POST /users/logout HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Réponse réussie (200):**
```
logout successful
```

**Réponses d'erreur:**
- **401** : Token invalide/expiré/déjà blacklisté
- **500** : Erreur lors de l'insertion en DB

**Effet:** Le token est ajouté à la table `t_blacklist_tokens` et ne pourra plus être utilisé

**Logs:** `user logged out` ou `logout faild`

---

## 🔐 Gestion de la sécurité

### 1. **Hachage des mots de passe**

**Algorithme:** Argon2id (primé OWASP 2018)

**Paramètres:**
```
m=65536  → 64 MB de mémoire
t=3      → 3 itérations
p=4      → 4 threads parallèles
```

**Avantages:**
- ✅ Résistant aux attaques par GPU et ASIC
- ✅ Paramètres ajustables avec la puissance des CPU
- ✅ Hachage probabiliste (chaque hash est différent)

**Exemple:**
```
Mot de passe : "Password123"
Hash généré : $argon2id$v=19$m=65536,t=3,p=4$hT18aCPZ5AFxQ2ncYkRkWg$5UvBttA1brZmn6Bmf1T0NgKaYaqUzMV1pvWNxDp5pFc
```

### 2. **Tokens JWT (JSON Web Tokens)**

**Structure du JWT:**
```
Header.Payload.Signature

Header: {"alg": "HS256", "typ": "JWT"}
Payload: {"sub": "email@example.com", "role": false, "exp": 1706163456}
Signature: HMAC_SHA256(Header.Payload, SECRET_KEY)
```

**Durée de validité:** 30 minutes (paramètrable)

**Cas d'utilisation stateless:** Pas besoin de session côté serveur

**Algorithme de signature:** HS256 (HMAC-SHA256)

### 3. **Blacklist des tokens**

**Problème résolu:** Un JWT valide jusqu'à l'expiration peut continuer à être utilisé après le logout

**Solution:** Table `t_blacklist_tokens` contenant les tokens révoqués

**Vérification:** À chaque requête protégée, le token est vérifié contre la blacklist

### 4. **Protection des endpoints**

**Middleware HTTP Bearer:**
```python
@Security(http_bearer)
def check_token(token: HTTPAuthorizationCredentials):
    # Vérifie le format Authorization: Bearer <token>
    # Décode et valide
    # Vérifie la blacklist
```

**Endpoints protégés:**
- GET `/users/` 
- POST `/users/logout`

**Endpoints non protégés:**
- POST `/users/add` (inscription sans token)
- POST `/users/auth` (authentification sans token)
- POST `/users/verify-token` (vérification sans authentification)

### 5. **Validation des données (Pydantic)**

**Email validation:**
```python
email: EmailStr  # Validation RFC 5322
```

**Mot de passe:**
```python
password: str = Field(min_length=6)  # Longueur minimale
```

### 6. **Secret Key Management**

**Variable d'environnement:** `SECRET_KEY`

**Valeur par défaut:** Hash Argon2 fourni (⚠️ NE PAS utiliser en production)

**Recommandation:** Générer une clé aléatoire sécurisée et la passer via `.env`

---

## 💾 Base de données

### 1. **Configuration de connexion**

**Type:** PostgreSQL

**URL de connexion construite:**
```
postgresql+psycopg2://admin:1234@localhost:5432/db_auth
```

**Composants:**
- **Driver:** psycopg2 (PostgreSQL)
- **Utilisateur:** admin
- **Mot de passe:** 1234
- **Serveur:** localhost (ou variable SERVER_DB)
- **Port:** 5432
- **Base:** db_auth

**Pool de connexions:** 10 connexions max

### 2. **Schéma des tables**

#### Table `t_users`

```sql
CREATE TABLE t_users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email VARCHAR UNIQUE NOT NULL,
  password VARCHAR(128) NOT NULL,
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_id ON t_users(id);
CREATE INDEX idx_users_email ON t_users(email);
```

**Champs:**
- `id` : Identifiant unique auto-incrémenté
- `email` : Unique, indexé pour recherche rapide
- `password` : Stocké hachée (128 caractères)
- `is_admin` : Boolean, défaut FALSE
- `created_at` : Timestamp de création, défaut NOW()
- `updated_at` : Timestamp de mise à jour, mise à jour auto

#### Table `t_blacklist_tokens`

```sql
CREATE TABLE t_blacklist_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token VARCHAR(500) UNIQUE NOT NULL,
  blacklisted_on TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_blacklist_id ON t_blacklist_tokens(id);
```

**Champs:**
- `id` : Identifiant unique
- `token` : Le JWT complet, unique et indexé
- `blacklisted_on` : Timestamp du logout

### 3. **Initialisation de la DB**

**Fichier:** `init.sql`

```sql
CREATE DATABASE db_auth
```

**Automatismes:**
- Le `docker-entrypoint-initdb.d` exécute ce script au démarrage du conteneur PostgreSQL
- SQLAlchemy crée automatiquement les tables à partir des entités (première exécution)

### 4. **Gestion des transactions**

**Commit automatique:**
```python
session.add(user)
session.commit()  # Valide la transaction
```

**Rollback en cas d'erreur:**
```python
except Exception:
    session.rollback()  # Annule la transaction
    return False
```

**Fermeture des sessions:**
```python
finally:
    session.close()  # Libère la connexion du pool
```

---

## 🚀 Configuration et déploiement

### 1. **Variables d'environnement (.env)**

**Fichier à créer:** `.env` (à la racine du projet)

```env
# Base de données
USER_DB=admin
PASSWORD_DB=secure_password_here
NAME_DB=db_auth
SERVER_DB=db  # ou localhost en local

# Authentification
EXPIRE_TIME=30
SECRET_KEY=your_secret_key_here

# Optional : Sentry
SENTRY_DSN=https://...
```

### 2. **Docker & Docker-Compose**

#### Fichier Dockerfile

**Image de base:** `python:3.14-slim`

```dockerfile
FROM python:3.14-slim
WORKDIR /app
RUN useradd -m userapp              # Utilisateur non-root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/logs && chown -R userapp:userapp /app
ENV PYTHONUNBUFFERED=1              # Pas de buffering
ENV PYTHONDONTWRITEBYTECODE=1       # Pas de .pyc
USER userapp
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
```

**Avantages:**
- ✅ Image allégée (slim)
- ✅ Utilisateur non-root (sécurité)
- ✅ Variables d'environnement optimisées

#### Fichier docker-compose.yml

**Services:**

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: auth-ms
    environment:
      - SERVER_DB=db
      - NAME_DB=${NAME_DB-db_auth}
    ports:
      - 8000:8000
    volumes:
      - ./logs:/app/logs
    networks:
      - net-auth
    depends_on:
      - db

  db:
    image: postgres:alpine
    container_name: postgresql
    environment:
      - POSTGRES_USER=${USER_DB-admin}
      - POSTGRES_PASSWORD=${PASSWORD_DB-1234}
    ports:
      - 5432:5432
    networks:
      - net-auth
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro

networks:
  net-auth:
    driver: bridge
```

**Architecture réseau:**
```
┌─────────────────────────────────┐
│   docker network (net-auth)     │
│   ┌───────────┐   ┌───────────┐ │
│   │ auth-ms   │   │ postgresql│ │
│   │ Port 8000 │   │ Port 5432 │ │
│   └─────┬─────┘   └─────┬─────┘ │
│         │               │       │
│         └───────────────┘       │
└─────────────────────────────────┘
         ↑                    ↑
       Host              Host 5432
     Port 8000        (pour debug)
```

**Variables d'environnement:**
- `USER_DB` : Utilisateur PostgreSQL (défaut: admin)
- `PASSWORD_DB` : Mot de passe (défaut: 1234)
- `NAME_DB` : Nom de la DB (défaut: db_auth)
- `SERVER_DB` : Host PostgreSQL (dans compose: "db")

### 3. **Déploiement Kubernetes**

**Fichiers fournis:**

#### `backend-deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
spec:
  # Configuration du déploiement
```

#### `backend-service.yaml`
Service interne pour communication inter-pods

#### `backend-service-nodeport.yaml`
Service exposé sur les nœuds (accès externe)

#### `backend-cm0-configmap.yaml`
Configuration centralisée (fichier de config)

#### `db-deployment.yaml` / `db-service.yaml`
Déploiement de PostgreSQL dans K8s

### 4. **Lancement local**

**Avec docker-compose:**
```bash
docker-compose up -d
```

**Avec Python direct:**
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python main.py
```

**Accès:**
- API : http://localhost:8000
- Documentation Swagger : http://localhost:8000/docs
- PostgreSQL : localhost:5432

---

## ✅ Points forts

### 1. **Architecture bien organisée**
- Séparation claire des responsabilités
- Couches indépendantes et testables
- Code modulaire et maintenable

### 2. **Sécurité robuste**
- ✅ Hachage Argon2 pour les mots de passe
- ✅ JWT pour l'authentification stateless
- ✅ Blacklist des tokens pour le logout
- ✅ Validation Pydantic des données
- ✅ Conteneurisation avec utilisateur non-root

### 3. **Infrastructure moderne**
- Docker et docker-compose pour isolation et reproductibilité
- Support Kubernetes avec fichiers YAML
- Logging structuré

### 4. **Framework puissant**
- FastAPI : performance, documentation auto, validation intégrée
- SQLAlchemy : ORM flexible et sûr
- Pydantic : validation et sérialisation robustes

### 5. **Bonnes pratiques**
- Variables d'environnement externalisées
- Pool de connexions DB configuré
- Gestion appropriée des exceptions
- Sessions fermées correctement

---

## ⚠️ Points d'amélioration

### 1. **CRITIQUE : Mots de passe comparés en clair**

**Problème:**
```python
# DAL user_dao.py
def authenticate(session:Session,user:User):
    filtred_user=session.query(User).filter(
        User.email==user.email,
        User.password==user.password  # ← COMPARAISON EN CLAIR !
    ).one_or_none()
```

**Risque:** Si la base de données est compromise, tous les mots de passe sont visibles en clair.

**Solution:**
```python
def authenticate(session:Session, user:User):
    filtered_user = session.query(User).filter(
        User.email == user.email
    ).one_or_none()
    
    if filtered_user and verify_pwd(filtered_user.password, user.password):
        return filtered_user
    return False
```

**Impact:** 🔴 CRITIQUE - À corriger avant la production

---

### 2. **Mot de passe non haché lors de l'inscription**

**Problème:**
```python
# controller auth_controller.py
@router.post("/add")
def register_user(userRequest:UserRequest,session=Depends(session_factory)):
    user_entity=User(
        email=userRequest.email,
        password=userRequest.password  # ← PAS HACHÉE !
    )
```

**Solution:**
```python
from helpers.utils import hash_pwd

@router.post("/add")
def register_user(userRequest:UserRequest, session=Depends(session_factory)):
    user_entity = User(
        email=userRequest.email,
        password=hash_pwd(userRequest.password)  # Hacher ici
    )
```

**Impact:** 🔴 CRITIQUE

---

### 3. **SECRET_KEY hardcodée par défaut**

**Problème:**
```python
SECRET_KEY = os.getenv("SECRET_KEY", "$argon2id$v=19$m=65536,t=3,p=4$...")
```

**Risque:** Si le `.env` n'est pas configuré, une clé par défaut est utilisée (connue publiquement).

**Solution:**
```python
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not configured in environment variables")
```

**Impact:** 🔴 CRITIQUE pour la production

---

### 4. **Pas de rate-limiting**

**Problème:** Un attaquant peut faire des brute-force sur `/users/auth`

**Solution:** Ajouter `slowapi` ou `limits` pour rate-limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth")
@limiter.limit("5/minute")
def authenticate_user(...):
    ...
```

**Impact:** 🟠 MOYEN

---

### 5. **Pas de validation de la force du mot de passe**

**Problème:** `password: str = Field(min_length=6)` ne valide que la longueur

**Solution:** Valider la complexité
```python
import re

def validate_password_strength(password: str):
    if not re.search(r'[A-Z]', password):
        raise ValueError("Majuscule requise")
    if not re.search(r'[0-9]', password):
        raise ValueError("Chiffre requis")
    if not re.search(r'[!@#$%^&*]', password):
        raise ValueError("Caractère spécial requis")
    return True
```

**Impact:** 🟡 MOYEN

---

### 6. **Logs insuffisants**

**Problème:** Les logs ne contiennent pas l'adresse IP du client

```python
logger.info('get all users from ip :')  # IP non loggée
```

**Solution:**
```python
@router.get("/")
def get_all(request: Request, ...):
    client_ip = request.client.host
    logger.info(f'get all users from ip: {client_ip}')
```

**Impact:** 🟡 MOYEN (sécurité et debugging)

---

### 7. **Pas de validation CORS**

**Problème:** Aucune restriction CORS, accessible de n'importe quelle origine

**Solution:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://exemple.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Impact:** 🟠 MOYEN

---

### 8. **Pas de tests unitaires**

**Problème:** Aucun test automatisé visible

**Fichier `test/api_test.http`** contient seulement des tests manuels

**Solution:** Ajouter des tests pytest
```python
# tests/test_auth_controller.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/users/add", json={
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 200
```

**Impact:** 🟡 MOYEN

---

### 9. **Pas de migration de DB (Alembic)**

**Problème:** Pas de versioning des schémas

**Solution:** Utiliser Alembic pour gérer les migrations

**Impact:** 🟡 MOYEN (important en production)

---

### 10. **Commentaires et documentation manquants**

**Problème:** Code peu documenté

**Solution:** Ajouter des docstrings
```python
def create_user(session: Session, user: User) -> bool:
    """
    Crée un nouvel utilisateur en base de données.
    
    Args:
        session: Session SQLAlchemy
        user: Entité User à créer
        
    Returns:
        True si création réussie, False sinon
        
    Raises:
        Validation email unique effectuée
    """
```

**Impact:** 🟡 MOYEN

---

### 11. **Type hints incomplets**

**Problème:** Certaines fonctions manquent de type hints

```python
def hash_pwd(password:str):  # Pas de return type
    return pwd_hash.hash(password)
```

**Solution:**
```python
def hash_pwd(password: str) -> str:
    return pwd_hash.hash(password)
```

**Impact:** 🟢 FAIBLE (mais bonne pratique)

---

### 12. **Pas de pagination pour GET /users/**

**Problème:** Retourne TOUS les utilisateurs, peut surcharger le serveur

**Solution:**
```python
@router.get("/")
def get_all(skip: int = 0, limit: int = 10, ...):
    users = session.query(User).offset(skip).limit(limit).all()
```

**Impact:** 🟡 MOYEN

---

### 13. **Encodage UTF-8 non garantit**

**Problème:** Les fichiers n'ont pas de déclaration d'encodage

**Solution:** Ajouter au début des fichiers Python
```python
# -*- coding: utf-8 -*-
```

**Impact:** 🟢 FAIBLE

---

## 📋 Recommandations

### Phase 1 : Corrections critiques (URGENT)

**Priorité absolue avant production :**

1. ✅ **Hacher le mot de passe en inscription**
   - Implémenter `hash_pwd()` dans `/users/add`
   - Temps: 10 min

2. ✅ **Utiliser `verify_pwd()` en authentification**
   - Corriger `/users/auth` pour comparer les hashes
   - Temps: 10 min

3. ✅ **Générer SECRET_KEY aléatoire**
   - Forcer la configuration via `.env`
   - Generer une clé sécurisée au déploiement
   - Temps: 15 min

### Phase 2 : Améliorations importantes (RECOMMANDÉ)

4. **Ajouter rate-limiting**
   - Dépendance : `slowapi`
   - Protéger `/users/auth` et `/users/add`
   - Temps: 1 heure

5. **Améliorer les logs**
   - Ajouter IP client
   - Ajouter stack traces aux erreurs
   - Temps: 1 heure

6. **Implémenter CORS restrictif**
   - Configurer origins autorisées
   - Temps: 30 min

7. **Ajouter validation force du mot de passe**
   - Longueur ≥ 8
   - Au moins 1 majuscule
   - Au moins 1 chiffre
   - Au moins 1 caractère spécial
   - Temps: 45 min

### Phase 3 : Bonnes pratiques (À FAIRE)

8. **Ajouter des tests unitaires**
   - Dépendance : `pytest`, `httpx`
   - Tests pour chaque endpoint
   - Temps: 4 heures

9. **Ajouter migrations Alembic**
   - Dépendance : `alembic`
   - Créer version initiale
   - Temps: 2 heures

10. **Implémenter pagination**
    - Ajouter `skip` et `limit` à GET `/users/`
    - Temps: 45 min

11. **Ajouter docstrings**
    - Documenter chaque fonction
    - Temps: 2 heures

12. **Ajouter type hints complets**
    - Type hints sur toutes les fonctions
    - Temps: 1 heure

### Commandes de correction rapide

**Pour la base de données (dev uniquement) :**
```bash
# Réinitialiser la DB
docker-compose down -v
docker-compose up -d

# Vérifier les logs
docker-compose logs -f backend
```

---

## 🎓 Résumé pour assimilation

### Ce qu'il faut retenir

1. **Type de service:** Micro-service d'authentification REST

2. **Stack:** FastAPI + PostgreSQL + JWT + Argon2

3. **Architecture:** Layered (Controller → DTO → DAL → Entity)

4. **Sécurité:** 
   - ✅ Argon2 pour les mots de passe
   - ✅ JWT pour tokens
   - ✅ Blacklist pour logout
   - ⚠️ Mots de passe NON hachés (BUG)

5. **Endpoints:** 5 routes pour auth complet

6. **Déploiement:** Docker-Compose ou Kubernetes

7. **Améliorations urgentes:**
   - Hacher les mots de passe
   - Corriger l'authentification
   - Générer SECRET_KEY unique

### Flux mental simplifié

```
1. User Sign Up
   email/password → POST /users/add → DB

2. User Login
   email/password → POST /users/auth → JWT Token

3. User Access Protected Resource
   JWT → GET /users/ → List of users (if token valid)

4. User Logout
   JWT → POST /users/logout → Blacklist JWT

5. Token Verification
   JWT → POST /users/verify-token → payload info
```

---

## 📞 Points de contact du code

**Fichiers critiques à connaître:**

| Fichier | Raison | Action fréquente |
|---------|--------|-----------------|
| `controllers/auth_controller.py` | Endpoints | Ajouter routes |
| `dal/user_dao.py` | Requêtes DB | Corriger authentification |
| `helpers/utils.py` | Sécurité | Améliorer hachage |
| `helpers/config.py` | Configuration | Ajouter variables d'env |
| `entities/user.py` | Modèles | Ajouter champs |
| `docker-compose.yml` | Déploiement | Changer ports/variables |

---

**Ce rapport couvre l'ensemble de votre backend. Pour des questions spécifiques sur un point, n'hésitez pas à demander des détails supplémentaires !**
