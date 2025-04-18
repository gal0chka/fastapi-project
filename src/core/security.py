# from datetime import datetime, timedelta
# from typing import Union
# import jwt
# from passlib.context import CryptContext

# # Конфигурация для JWT
# SECRET_KEY = "your-secret-key"  # Замените на более безопасный секретный ключ
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время действия токена в минутах

# # Контекст для хэширования паролей
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# # Хэширование пароля
# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)


# # Проверка пароля
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


# # Создание JWT токена
# def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + expires_delta
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# # Верификация JWT токена
# def verify_access_token(token: str) -> Union[dict, None]:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload if payload["exp"] >= datetime.utcnow().timestamp() else None
#     except jwt.PyJWTError:
#         return None
