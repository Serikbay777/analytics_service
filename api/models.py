"""
Pydantic модели для API
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    """Запрос к агенту"""
    query: str = Field(..., description="Вопрос на естественном языке", min_length=1)
    model: Optional[str] = Field(default="gpt-4o", description="Модель LLM")


class QueryResponse(BaseModel):
    """Ответ агента"""
    query: str = Field(..., description="Исходный запрос")
    answer: str = Field(..., description="Ответ агента")
    model: str = Field(..., description="Использованная модель")
    execution_time: float = Field(..., description="Время выполнения в секундах")


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    error: str = Field(..., description="Описание ошибки")
    detail: Optional[str] = Field(None, description="Детали ошибки")


class HealthResponse(BaseModel):
    """Статус здоровья сервиса"""
    status: str = Field(..., description="Статус сервиса")
    version: str = Field(..., description="Версия API")
    models_available: List[str] = Field(..., description="Доступные модели")
    tools_count: int = Field(..., description="Количество инструментов")


class ToolInfo(BaseModel):
    """Информация об инструменте"""
    name: str = Field(..., description="Название инструмента")
    description: str = Field(..., description="Описание инструмента")


class ToolsResponse(BaseModel):
    """Список доступных инструментов"""
    tools: List[ToolInfo] = Field(..., description="Список инструментов")
    count: int = Field(..., description="Количество инструментов")
