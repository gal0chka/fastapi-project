from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
# from src.core.security import verify_access_token
# Импортируем ORM-модель с переименованием, чтобы не путать с Pydantic-схемой
from src.models.sellers import Seller as SellerModel
from src.schemas.sellers import SellerCreate, Seller as SellerSchema, SellerWithBooks
from src.configurations import get_async_session

sellers_router = APIRouter(tags=["sellers"], prefix="/seller")


# Регистрация продавца
@sellers_router.post("/", response_model=SellerSchema, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: SellerCreate, session: AsyncSession = Depends(get_async_session)):
    new_seller = SellerModel(
        first_name=seller.first_name,
        last_name=seller.last_name,
        e_mail=seller.e_mail,
        password=seller.password,
    )
    session.add(new_seller)
    await session.flush()  # Производим flush для получения присвоенного id
    return new_seller


# Получение списка всех продавцов
@sellers_router.get("/", response_model=list[SellerSchema])
async def get_all_sellers(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(SellerModel))
    sellers = result.scalars().all()
    return sellers


# Получение данных о конкретном продавце
@sellers_router.get("/{seller_id}", response_model=SellerWithBooks)
async def get_seller(seller_id: int, session: AsyncSession = Depends(get_async_session)):
    query = (
        select(SellerModel)
        .options(selectinload(SellerModel.books))
        .filter(SellerModel.id == seller_id)
    )
    result = await session.execute(query)
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )
    return seller

# @sellers_router.get("/{seller_id}", response_model=SellerWithBooks)
# async def get_seller(
#     seller_id: int, 
#     token: str = Depends(verify_access_token),  # Добавляем проверку токена
#     session: AsyncSession = Depends(get_async_session)
# ):
#     # Проверка пользователя с токеном
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token",
#             headers={"WWW-Authenticate": "Bearer"}
#         )
    
#     # Получаем продавца из базы данных
#     seller = await session.get(SellerModel, seller_id)
#     if not seller:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Seller not found"
#         )

#     return seller

# Обновление данных о продавце
@sellers_router.put("/{seller_id}", response_model=SellerSchema)
async def update_seller(seller_id: int, seller_data: SellerCreate, session: AsyncSession = Depends(get_async_session)):
    seller = await session.get(SellerModel, seller_id)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )

    seller.first_name = seller_data.first_name
    seller.last_name = seller_data.last_name
    seller.e_mail = seller_data.e_mail

    await session.flush()
    return seller


# Удаление продавца
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: AsyncSession = Depends(get_async_session)):
    seller = await session.get(SellerModel, seller_id)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )

    await session.delete(seller)
    await session.flush()
