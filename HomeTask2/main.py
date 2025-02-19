from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime
import json
from pathlib import Path
import re

app = FastAPI()

DATA_FILE = Path("requests.json")

# Функция для проверки, что строка состоит только из кириллицы и начинается с заглавной буквы
def validate_cyrillic(value: str):
    if not re.fullmatch(r"[А-ЯЁ][а-яё]+", value):
        raise ValueError("Поле должно содержать только кириллические символы и начинаться с заглавной буквы")
    return value

# Модель для валидации входных данных
class RequestModel(BaseModel):
    фамилия: str = Field(..., description="Фамилия", example="Иванов")
    имя: str = Field(..., description="Имя", example="Петр")
    дата_рождения: str = Field(..., description="Дата рождения", example="1990-05-15")
    номер_телефона: str = Field(..., description="Телефон", example="+79001234567")
    email: EmailStr = Field(..., description="Электронная почта", example="example@email.com")
    причины: List[str] = Field(..., description="Список причин обращения", example=["Нет доступа к сети", "Не работает телефон"])
    дата_обнаружения: datetime = Field(..., description="Дата и время обнаружения", example="2025-02-19T14:30:00")

    # Дополнительная валидация полей
    @classmethod
    def validate_familiya(cls, value: str) -> str:
        return validate_cyrillic(value)

    @classmethod
    def validate_imya(cls, value: str) -> str:
        return validate_cyrillic(value)

@app.post("/submit_request/")
async def submit_request(request: RequestModel):
    """Сохраняем данные запроса в JSON-файл."""
    data = request.dict()

    # Загружаем существующие данные если есть
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Добавляем новый запрос
    existing_data.append(data)

    # Сохраняем в файл с UTF-8
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

    # Возвращаем JSON с правильной кодировкой UTF-8 чтоб кракозябры не было
    return JSONResponse(
        content={"message": "Обращение сохранено", "data": data}, 
        media_type="application/json; charset=utf-8"
    )

# Добавим корневой эндпойнт, чтобы при открытии не было ошибки
@app.get("/")
def root():
    return {"message": "Сервис сбора обращений работает! Перейдите на /docs для тестирования API."}
