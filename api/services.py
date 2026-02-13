"""
Сервисы для работы с агентом
"""
import os
import time
from typing import Dict, Any
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

from analytics_agent_openai_simple import run_agent, tools


class AgentService:
    """Сервис для работы с AI агентом"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY не найден в .env")
        
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.available_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
        self.tools = tools
    
    def query(self, query: str, model: str = None) -> Dict[str, Any]:
        """
        Отправить запрос агенту
        
        Args:
            query: Вопрос на естественном языке
            model: Модель LLM (опционально)
        
        Returns:
            Словарь с ответом и метаданными
        """
        if not model:
            model = self.default_model
        
        if model not in self.available_models:
            raise ValueError(f"Модель {model} не поддерживается. Доступные: {self.available_models}")
        
        start_time = time.time()
        
        try:
            answer = run_agent(query, self.api_key, model)
            execution_time = time.time() - start_time
            
            return {
                "query": query,
                "answer": answer,
                "model": model,
                "execution_time": round(execution_time, 2)
            }
        except Exception as e:
            execution_time = time.time() - start_time
            raise Exception(f"Ошибка при выполнении запроса: {str(e)}")
    
    def get_tools_info(self) -> list:
        """Получить информацию о доступных инструментах"""
        tools_info = []
        for tool in self.tools:
            tools_info.append({
                "name": tool.name,
                "description": tool.description
            })
        return tools_info
    
    def get_health(self) -> Dict[str, Any]:
        """Получить статус здоровья сервиса"""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "models_available": self.available_models,
            "tools_count": len(self.tools)
        }


# Глобальный экземпляр сервиса
agent_service = AgentService()
