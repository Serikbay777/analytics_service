"""
API роуты
"""
from fastapi import APIRouter, HTTPException, status
from api.models import (
    QueryRequest, 
    QueryResponse, 
    ErrorResponse,
    HealthResponse,
    ToolsResponse,
    ToolInfo
)
from api.services import agent_service

router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Отправить запрос агенту",
    description="Отправляет вопрос на естественном языке AI агенту и получает ответ"
)
async def query_agent(request: QueryRequest):
    """
    Отправить запрос AI агенту
    
    - **query**: Вопрос на естественном языке (русский или английский)
    - **model**: Модель LLM (gpt-4o, gpt-4o-mini, gpt-4-turbo)
    
    Примеры запросов:
    - "Покажи топ-10 треков по доходу"
    - "Найди информацию о треке Meili"
    - "Сравни артистов Yenlik и Shiza"
    """
    try:
        result = agent_service.query(request.query, request.model)
        return QueryResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Проверка здоровья сервиса",
    description="Возвращает статус сервиса и доступные возможности"
)
async def health_check():
    """
    Проверка здоровья сервиса
    
    Возвращает:
    - Статус сервиса
    - Версию API
    - Доступные модели
    - Количество инструментов
    """
    health = agent_service.get_health()
    return HealthResponse(**health)


@router.get(
    "/tools",
    response_model=ToolsResponse,
    summary="Список доступных инструментов",
    description="Возвращает список всех аналитических инструментов агента"
)
async def get_tools():
    """
    Получить список доступных инструментов
    
    Возвращает информацию о всех 13 аналитических инструментах:
    - Название инструмента
    - Описание функциональности
    """
    tools_info = agent_service.get_tools_info()
    return ToolsResponse(
        tools=[ToolInfo(**tool) for tool in tools_info],
        count=len(tools_info)
    )


@router.get(
    "/models",
    summary="Список доступных моделей",
    description="Возвращает список поддерживаемых LLM моделей"
)
async def get_models():
    """
    Получить список доступных моделей
    
    Возвращает список всех поддерживаемых LLM моделей
    """
    return {
        "models": agent_service.available_models,
        "default": agent_service.default_model,
        "count": len(agent_service.available_models)
    }
