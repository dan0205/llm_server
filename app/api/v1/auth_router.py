""" from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas
from app.core.database import get_db
from app.services import auth_service

router = APIRouter()

@router.post("/auth/google", response_model=schemas.Token)
async def login_with_google(
    token_data: schemas.GoogleToken,
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.login_or_register_user(
        db=db, google_token=token_data.token
    )
 """