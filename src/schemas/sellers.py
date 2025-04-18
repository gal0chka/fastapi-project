from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["SellerBase", "SellerCreate", "Seller", "SellerWithBooks"]


# Базовый класс "Продавец", содержащий поля, которые есть во всех классах-наследниках.
class SellerBase(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr  # Используем EmailStr для валидации email


# Класс для валидации входящих данных. Не содержит id, так как его присваивает БД.
class SellerCreate(SellerBase):
    password: str = Field(min_length=6, max_length=100)  # Пример настройки длины пароля

    @field_validator("password")  # Валидатор для проверки сложности пароля
    @staticmethod
    def validate_password(val: str):
        if len(val) < 6:
            raise PydanticCustomError("Validation error", "Password is too short!")
        return val

# Класс, валидирующий исходящие данные. Он уже содержит id
class Seller(SellerBase):
    id: int


# Класс для возврата данных о продавце с его книгами
class SellerWithBooks(Seller):
    books: list["ReturnedBook"]  # Используем схему ReturnedBook из src/schemas/books.py

    class Config:
        from_attributes = True  # Для совместимости с ORM (ранее known as `orm_mode`)
# Импорт схемы книги после определения SellerWithBooks
from src.schemas.books import ReturnedBook

# Перестраиваем модель для корректной обработки forward-ссылок
SellerWithBooks.model_rebuild()