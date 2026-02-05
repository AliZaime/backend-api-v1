from helpers.config import redis_client, EXPIRE_TIME

def is_blacklist_token(session, token: str):
    # On vérifie dans Redis si le token existe
    return redis_client.exists(token) == 1

def add_token_to_blacklist(session, token: str):
    try:
        # On ajoute le token dans Redis avec un TTL (en secondes)
        # On utilise EXPIRE_TIME du config (qui est en minutes) converti en secondes
        ttl_seconds = int(EXPIRE_TIME) * 60
        redis_client.setex(token, ttl_seconds, "true")
        return True
    except Exception as e:
        print(f"Error adding to Redis blacklist: {e}")
        return False
