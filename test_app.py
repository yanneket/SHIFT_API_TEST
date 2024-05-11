import time
from datetime import datetime, timedelta
import jwt
import pytest
import httpx
from httpx import ASGITransport
from main import User, app, SECRET_KEY, ALGORITHM


# Тест выдачи токена по верным данным
@pytest.mark.asyncio
async def test_login_with_valid_data():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Создаем тестового пользователя
        test_user = User(username="admin", password="adminpass")

        # Отправляем POST-запрос на /login
        response = await client.post("/login", json=test_user.model_dump())

        # Проверяем статус-код ответа
        assert response.status_code == 200

        # Проверяем структуру JSON-ответа
        response_data = response.json()
        if "access_token" in response_data:
            # В случае успешной аутентификации проверяем токен
            assert "token_type" in response_data
            assert response_data["token_type"] == "bearer"


# Тест на проверку неверных учетных данных
@pytest.mark.asyncio
async def test_login_with_invalid_data():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Создаем тестового пользователя с неверными учетными данными
        test_user = User(username="invalid_user", password="invalid_password")

        # Отправляем POST-запрос на /login с неправильными данными
        response = await client.post("/login", json=test_user.model_dump())

        # Проверяем статус-код ответа
        assert response.status_code == 400

        # Проверяем структуру JSON-ответа
        assert {"detail": "User not found"} == response.json()


# Тест на истечение срока действия токена
@pytest.mark.asyncio
async def test_timeout():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Создаем тестового пользователя
        test_user = User(username="admin", password="adminpass")

        # Отправляем POST-запрос на /login
        response = await client.post("/login", json=test_user.model_dump())

        # Проверяем статус-код ответа
        assert response.status_code == 200

        # Добавляем в headers токен и ждем 40 секунд
        jwt_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {jwt_token}"}
        time.sleep(40)

        # Получаем ответ 400, так как токен истек
        response = await client.get("/about_me", headers=headers)
        assert response.status_code == 400
        assert {"detail": "The token is invalid"} == response.json()


# Тест на успешную аутентификацию по токену
@pytest.mark.asyncio
async def test_authenticate_successfully():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Создаем тестового пользователя
        test_user = User(username="admin", password="adminpass")

        # Отправляем POST-запрос на /login
        response = await client.post("/login", json=test_user.model_dump())

        # Проверяем статус-код ответа
        assert response.status_code == 200

        # Добавляем в headers токен и ждем 40 секунд
        jwt_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {jwt_token}"}

        # Получаем ответ 200, аутентификация успешна
        response = await client.get("/about_me", headers=headers)
        assert response.status_code == 200
        assert {"username": "admin", "password": "adminpass", 'salary': 10000, "date_of_promotion": '12.04.23'} == response.json()
