import pytest
from sqlalchemy import select
from src.models.sellers import Seller as SellerModel
from src.models.books import Book
from fastapi import status
from icecream import ic


# Тест на ручку для создания продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/seller/", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    seller_id = result_data.pop("id", None)
    assert seller_id, "Seller id not returned from endpoint"
    
    # В ответе не должно быть поля password
    assert "password" not in result_data, "Password should not be returned in response"
    
    assert result_data == {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com"
    }


@pytest.mark.asyncio
async def test_create_seller_with_short_password(async_client):
    data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "e_mail": "alice.smith@example.com",
        "password": "123"  # слишком короткий пароль
    }
    response = await async_client.post("/api/v1/seller/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем продавцов напрямую через ORM-модель, чтобы не зависеть от POST ручки
    seller1 = SellerModel(
        first_name="John",
        last_name="Doe",
        e_mail="john.doe@example.com",
        password="password123"
    )
    seller2 = SellerModel(
        first_name="Alice",
        last_name="Smith",
        e_mail="alice.smith@example.com",
        password="password456"
    )
    
    db_session.add_all([seller1, seller2])
    await db_session.flush()  # Выполняем flush, чтобы получить присвоенные id

    # Запрашиваем список продавцов
    response = await async_client.get("/api/v1/seller/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    # Ожидаем, что будет возвращен список продавцов
    assert len(response_data) == 2, "Ожидается, что будет возвращено 2 продавца"

    expected_response = [
        {
            "id": seller1.id,
            "first_name": "John",
            "last_name": "Doe",
            "e_mail": "john.doe@example.com"
        },
        {
            "id": seller2.id,
            "first_name": "Alice",
            "last_name": "Smith",
            "e_mail": "alice.smith@example.com"
        }
    ]

    # Порядок может быть не детерминирован, поэтому сортируем по id
    response_data_sorted = sorted(response_data, key=lambda x: x["id"])
    expected_response_sorted = sorted(expected_response, key=lambda x: x["id"])
    assert response_data_sorted == expected_response_sorted



@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем продавца напрямую через ORM
    seller = SellerModel(
        first_name="John",
        last_name="Doe",
        e_mail="john.doe@example.com",
        password="password123"
    )
    db_session.add(seller)
    await db_session.flush()  # flush для получения seller.id

    # Создаем книги для этого продавца
    book1 = Book(
        title="Clean Architecture",
        author="Robert Martin",
        year=2025,
        pages=300,
        seller_id=seller.id
    )
    book2 = Book(
        title="Eugeny Onegin",
        author="Pushkin",
        year=2001,
        pages=104,
        seller_id=seller.id
    )
    db_session.add_all([book1, book2])
    await db_session.flush()

    # Запрашиваем данные о продавце по его id
    response = await async_client.get(f"/api/v1/seller/{seller.id}")
    assert response.status_code == status.HTTP_200_OK

    # Формируем ожидаемый ответ. Обратите внимание: поле password не должно возвращаться.
    expected_response = {
        "id": seller.id,
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com",
        "books": [
            {
                "id": book1.id,
                "title": "Clean Architecture",
                "author": "Robert Martin",
                "year": 2025,
                "pages": 300,
            },
            {
                "id": book2.id,
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2001,
                "pages": 104,
            },
        ]
    }

    # Если порядок книг в ответе может быть произвольным, сортируем списки по id
    response_data = response.json()
    response_data["books"] = sorted(response_data["books"], key=lambda x: x["id"])
    expected_response["books"] = sorted(expected_response["books"], key=lambda x: x["id"])

    assert response_data == expected_response


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем продавца вручную через ORM
    seller = SellerModel(
        first_name="John",
        last_name="Doe",
        e_mail="john.doe@example.com",
        password="password123"
    )
    db_session.add(seller)
    await db_session.flush()  # Получаем присвоенный seller.id

    # Отправляем PUT-запрос для обновления продавца.
    # Обратите внимание: для обновления используется схема SellerCreate, поэтому необходимо передать password.
    response = await async_client.put(
        f"/api/v1/seller/{seller.id}",
        json={
            "first_name": "Alice",
            "last_name": "Smith",
            "e_mail": "alice.smith@example.com",
            "password": "newpassword123"
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Получаем обновленного продавца из базы данных
    updated_seller = await db_session.get(SellerModel, seller.id)
    assert updated_seller.first_name == "Alice"
    assert updated_seller.last_name == "Smith"
    assert updated_seller.e_mail == "alice.smith@example.com"
    assert updated_seller.id == seller.id

import pytest
from fastapi import status
from sqlalchemy import select
from src.models.sellers import Seller as SellerModel

@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем продавца напрямую через ORM
    seller = SellerModel(
        first_name="John",
        last_name="Doe",
        e_mail="john.doe@example.com",
        password="password123"
    )
    db_session.add(seller)
    await db_session.flush()
    
    seller_id = seller.id

    # Отправляем запрос на удаление продавца
    response = await async_client.delete(f"/api/v1/seller/{seller_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    
    # Проверяем, что в базе данных больше нет продавцов
    result = await db_session.execute(select(SellerModel))
    remaining_sellers = result.scalars().all()
    assert len(remaining_sellers) == 0


@pytest.mark.asyncio
async def test_delete_seller_with_invalid_seller_id(db_session, async_client):
    # Создаем продавца напрямую через ORM
    seller = SellerModel(
        first_name="John",
        last_name="Doe",
        e_mail="john.doe@example.com",
        password="password123"
    )
    db_session.add(seller)
    await db_session.flush()

    # Отправляем запрос на удаление продавца с несуществующим id (seller.id + 1)
    response = await async_client.delete(f"/api/v1/seller/{seller.id + 1}")
    assert response.status_code == status.HTTP_404_NOT_FOUND