import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(str(settings.REDIS_URL), decode_responses=True)

async def store_refresh_token(user_id: int, token_jti: str, expires_in_days: int = 7) -> None:
    key = f"refresh_token:{user_id}:{token_jti}"
    await redis_client.setex(key, expires_in_days * 24 * 3600, "valid")

async def invalidate_refresh_token(user_id: int, token_jti: str) -> None:
    key = f"refresh_token:{user_id}:{token_jti}"
    await redis_client.delete(key)

async def is_refresh_token_valid(user_id: int, token_jti: str) -> bool:
    key = f"refresh_token:{user_id}:{token_jti}"
    return await redis_client.exists(key) == 1