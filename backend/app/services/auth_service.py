import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infra import User
from app.domain.schemas.user import UserCreate
from app.core.security import verify_password, hash_password, create_access_token, create_refresh_token
from app.infra.redis import store_refresh_token
from app.core.config import settings

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed_pw = hash_password(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_pw)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

async def create_tokens(user_id: int, db: AsyncSession) -> dict[str, any]:
    jti = str(uuid.uuid4())
    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user_id), "jti": jti})
    
    # Store refresh token JTI in Redis for validation/revocation
    await store_refresh_token(
        user_id=user_id,
        token_jti=jti,
        expires_in_days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    # Get user info
    user = await db.get(User, user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }