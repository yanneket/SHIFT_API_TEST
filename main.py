from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt

app = FastAPI(title='SHIFT')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Секретный ключ для подписи и верификации токенов JWT
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"


# Пример информации из БД
USERS_DATA = [
    {"username": "admin", "password": "adminpass", 'salary': 10000, "date_of_promotion": '12.04.23'},
    {"username": "user", "password": "userpass", 'salary': 20000, "date_of_promotion": '20.04.23'},
    {"username": "user1", "password": "user1pass", 'salary': 13000, "date_of_promotion": '12.08.24'}
]


class User(BaseModel):
    username: str
    password: str


# Функция для создания JWT токена
def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


# Функция получения User'а по токену
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # декодируем токен
        return payload.get("sub")
    except:
        return


# Функция для получения пользовательских данных на основе имени пользователя
def get_user(username: str):
    for user in USERS_DATA:
        if user.get("username") == username:
            return user
    return None


# аутентификация
@app.post("/login")
async def login(user_in: User):
    for user in USERS_DATA:
        if user.get("username") == user_in.username and user.get("password") == user_in.password:
            return {"access_token": create_jwt_token(
                {"sub": user_in.username, "exp": datetime.utcnow() + timedelta(seconds=30)}), "token_type": "bearer"}
        else:
            raise HTTPException(status_code=400, detail="User not found")


# получение информации о пользователе
@app.get("/about_me")
async def about_me(current_user: str = Depends(get_user_from_token)):
    user = get_user(current_user)
    if user:
        return user
    else:
        raise HTTPException(status_code=400, detail="The token is invalid")
