from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException,Security,Request,Response
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

from helpers.config import session_factory
from dal.user_dao import get_all_users,create_user,authenticate
from dto.users_dto import UserResponse,UserRequest,TokenResponse,TokenRequest
from entities.user import User
from helpers.utils import create_token,decode_token
from helpers.utils import create_token,decode_token,hash_pwd
from helpers.config import logger
from dal.black_listed_dao import add_token_to_blacklist,is_blacklist_token
router=APIRouter(prefix="/users",tags=["users"])  
http_bearer=HTTPBearer()

def check_token(session=Depends(session_factory),token:HTTPAuthorizationCredentials=Security(http_bearer)):
    credentials=token.credentials
    payload=decode_token(credentials)
    if not payload :
        raise HTTPException(status_code=401,detail='Invalid token')
    if is_blacklist_token(session,credentials):
        raise HTTPException(status_code=401,detail='Token is blacklisted')
    return payload

@router.get("/",response_model=list[UserResponse])
def get_all(session=Depends(session_factory),
            payload=Depends(check_token)
            ):
    
    # Seuls les admins peuvent lister tous les utilisateurs
    if not payload.get("is_admin"):
         raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    users:list[User]=get_all_users(session)
    results:list[UserResponse]=[]
    for user in users:
        results.append(UserResponse(
            email=str(user.email),
            is_admin=bool(user.is_admin),
            created_at=str(user.created_at),
            updated_at=str(user.updated_at)
        ))
    logger.info('GET /users - Admin access verified')
    return results

@router.post("/add",response_model=UserResponse)
def register_user(request: Request, userRequest:UserRequest,session=Depends(session_factory)):
    # VERSION SECURISEE (avec hachage Argon2)
    user_entity=User(
        email=userRequest.email,
        password=hash_pwd(userRequest.password)  # ← Hash sécurisé Argon2
    )
    add_ok=create_user(session,user_entity)
    if add_ok :
        logger.info('Register - Success - User: %s - IP: %s', userRequest.email, request.client.host)
        return UserResponse(
            email=str(user_entity.email),
            is_admin=bool(user_entity.is_admin),
            created_at=str(user_entity.created_at),
            updated_at=str(user_entity.updated_at)
        )
        
    logger.error('Register - Failed - User: %s - IP: %s - Reason: Database Error', userRequest.email, request.client.host)
    raise HTTPException(status_code=401,detail="Registration failed")

@router.post("/auth",response_model=TokenResponse)
def authenticate_user(request: Request, userRequest:UserRequest,
                        session=Depends(session_factory),
                        ):
    user_entity=User(
        email=userRequest.email,
        password=userRequest.password
    )
    auth_user=authenticate(session,user_entity)
    if auth_user != False :
        claims:dict={
                "id": auth_user.id,
                "sub":auth_user.email,
                "is_admin":bool(auth_user.is_admin)
        }
        token=create_token(claims)
        logger.info('Login - Success - User: %s - IP: %s', userRequest.email, request.client.host)
        return TokenResponse(token=token,
                             payload=claims)
    logger.warning('Login - Failed - User: %s - IP: %s - Reason: Invalid Credentials', userRequest.email, request.client.host)
    raise HTTPException(status_code=401,detail="Authentication failed")
@router.post("/verify-token",response_model=TokenResponse)
def verify_token(request: Request, tokenRequest:TokenRequest, session=Depends(session_factory)):
    payload=decode_token(token=tokenRequest.token)
    if not payload :
        logger.warning('Verify Token - Invalid - IP: %s', request.client.host)
        raise HTTPException(status_code=404,detail="Invalid token")
    
    # Vérification dans la blacklist Redis via le DAO
    if is_blacklist_token(session, tokenRequest.token):
        logger.warning('Verify Token - Blacklisted - User: %s - IP: %s', payload.get('sub'), request.client.host)
        raise HTTPException(status_code=401, detail="Token is blacklisted")
        
    return TokenResponse(token=tokenRequest.token,payload=payload)

@router.post("/logout")
def logout_user(request: Request, token:HTTPAuthorizationCredentials=Security(http_bearer),
                session=Depends(session_factory)
                ):
    credentials=token.credentials
    
    add_ok=add_token_to_blacklist(session,credentials)
    if add_ok :
        logger.info('Logout - Success - IP: %s', request.client.host)
        return Response(status_code=200,content="logout successful")
    logger.error('Logout - Failed - IP: %s - Reason: Redis Error', request.client.host)
    raise HTTPException(status_code=500,detail="Logout failed")
