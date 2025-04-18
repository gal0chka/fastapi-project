from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.token import Token, UserLogin
from src.core.security import create_access_token, verify_password
from src.models.sellers import Seller as SellerModel
from src.configurations import get_async_session

auth_router = APIRouter(tags=["auth"], prefix="/auth")


# Эндпоинт для получения токена
@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_async_session)):
    # Ищем пользователя по email
    user = db.query(SellerModel).filter(SellerModel.e_mail == form_data.email).first()
    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Создаем токен
    access_token = create_access_token(data={"sub": user.e_mail})
    return {"access_token": access_token, "token_type": "bearer"}
