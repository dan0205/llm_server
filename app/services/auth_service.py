""" from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app import schemas, models
from sqlalchemy.future import select

async def login_or_register_user(db: AsyncSession, google_token: str):
    try:
        idinfo = id_token.verify_oauth2_token(
            google_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        google_sub = idinfo['sub']
        email = idinfo['email']
        full_name = idinfo.get('name')

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google Token",
        )

    # DB에서 사용자 확인
    result = await db.execute(select(models.User).filter(models.User.google_sub == google_sub))
    user = result.scalar_one_or_none()

    # 없으면 새로 생성
    if not user:
        new_user = models.User(
            google_sub=google_sub,
            email=email,
            full_name=full_name,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        user = new_user

    # JWT 생성
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
 """