from sqlalchemy import select
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.schemas.user import UserCreate, UserLogin, TokenWithUser, UserResponse
from app.services.auth_service import authenticate_user, create_user, create_tokens
from app.infra.database import get_db
from app.core.security import decode_token
from app.infra.redis import is_refresh_token_valid
from app.domain.schemas.user import TokenPayload
from app.infra import User
from app.api.v1.deps import CurrentUser

router = APIRouter(tags=["auth"])

DBSession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenWithUser)
async def register(user_in: Annotated[UserCreate, Body(...)], db: DBSession):
    existing = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(db, user_in)
    return await create_tokens(user.id, db)

@router.post("/login", response_model=TokenWithUser)
async def login(user_in: Annotated[UserLogin, Body(...)], db: DBSession):
    user = await authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return await create_tokens(user.id, db)

@router.post("/refresh", response_model=TokenWithUser)
async def refresh_token(refresh_token: Annotated[str, Body(embed=True)], db: DBSession):
    try:
        payload = decode_token(refresh_token)
        token_data = TokenPayload(**payload)
        if token_data.type != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = int(token_data.sub)
    jti = payload.get("jti")
    if not jti or not await is_refresh_token_valid(user_id, jti):
        raise HTTPException(status_code=401, detail="Refresh token revoked or expired")

    # Optional: invalidate old refresh token here for single-session
    return await create_tokens(user_id, db)

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: CurrentUser):
    """Get current authenticated user information"""
    return UserResponse(id=current_user.id, email=current_user.email)