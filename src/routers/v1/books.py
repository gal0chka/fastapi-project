# Для импорта из корневого модуля
# import sys
# sys.path.append("..")
# from main import app

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from src.models.books import Book
from src.schemas import IncomingBook, ReturnedAllbooks, ReturnedBook, BookUpdate
from src.models.sellers import Seller as SellerModel
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session
from fastapi import HTTPException
# from src.core.security import verify_access_token

books_router = APIRouter(tags=["books"], prefix="/books")

# CRUD - Create, Read, Update, Delete

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
@books_router.post("/books/", status_code=status.HTTP_201_CREATED)
@books_router.post(
    "/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED
)  # Прописываем модель ответа
async def create_book(
    book: IncomingBook,
    session: DBSession,
):  # прописываем модель валидирующую входные данные
    # session = get_async_session() вместо этого мы используем иньекцию зависимостей DBSession
    
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    seller = await session.get(SellerModel, book.seller_id)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found"
        )
    new_book = Book(
        **{
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "pages": book.pages,
            "seller_id": book.seller_id,
        }
    )

    session.add(new_book)
    await session.flush()

    return new_book

# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
# @books_router.post(
#     "/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED
# )  # Прописываем модель ответа
# async def create_book(
#     book: IncomingBook,
#     session: DBSession,
#     token: str = Depends(verify_access_token)  # Добавляем проверку токена
# ):  
#     # Получаем продавца по seller_id
#     seller = await session.get(SellerModel, book.seller_id)
#     if not seller:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Seller not found"
#         )
    
#     # Создаем книгу
#     new_book = Book(
#         **{
#             "title": book.title,
#             "author": book.author,
#             "year": book.year,
#             "pages": book.pages,
#             "seller_id": book.seller_id,
#         }
#     )

#     session.add(new_book)
#     await session.flush()

#     return new_book


# Ручка, возвращающая все книги
@books_router.get("/", response_model=ReturnedAllbooks)
async def get_all_books(session: DBSession):
    # Хотим видеть формат
    # books: [{"id": 1, "title": "blabla", ...., "year": 2023},{...}]
    query = select(Book)  # SELECT * FROM book
    result = await session.execute(query)
    books = result.scalars().all()
    return {"books": books}


# Ручка для получения книги по ее ИД
@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    if result := await session.get(Book, book_id):
        return result

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления книги
@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await session.get(Book, book_id)
    ic(deleted_book)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_book:
        await session.delete(deleted_book)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о книге
@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book_data: BookUpdate, session: AsyncSession = Depends(get_async_session)):
    # Получаем книгу по id
    if updated_book := await session.get(Book, book_id):
        # Проверяем, существует ли продавец с указанным seller_id
        seller = await session.get(SellerModel, new_book_data.seller_id)
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller not found"
            )
        # Обновляем поля книги
        updated_book.author = new_book_data.author
        updated_book.title = new_book_data.title
        updated_book.year = new_book_data.year
        updated_book.pages = new_book_data.pages
        updated_book.seller_id = new_book_data.seller_id

        await session.flush()

        return updated_book

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о книге
# @books_router.put("/{book_id}", response_model=ReturnedBook)
# async def update_book(
#     book_id: int, 
#     new_book_data: BookUpdate, 
#     session: AsyncSession = Depends(get_async_session),
#     token: str = Depends(verify_access_token)  # Добавляем проверку токена
# ):
#     # Получаем книгу по id
#     if updated_book := await session.get(Book, book_id):
#         # Проверяем, существует ли продавец с указанным seller_id
#         seller = await session.get(SellerModel, new_book_data.seller_id)
#         if not seller:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Seller not found"
#             )
        
#         # Обновляем поля книги
#         updated_book.author = new_book_data.author
#         updated_book.title = new_book_data.title
#         updated_book.year = new_book_data.year
#         updated_book.pages = new_book_data.pages
#         updated_book.seller_id = new_book_data.seller_id

#         await session.flush()

#         return updated_book

#     return Response(status_code=status.HTTP_404_NOT_FOUND)