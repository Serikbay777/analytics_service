#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Агент для аналитики музыкальных данных на LangGraph
"""

import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

# Загружаем переменные из .env
load_dotenv()
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from analytics_tools import (
    get_top_tracks_tool,
    get_top_artists_tool,
    search_track_tool,
    search_artist_tool,
    get_track_details_tool,
    get_artist_tracks_tool,
    get_platform_stats_tool,
    get_country_stats_tool,
    get_artist_timeline_tool,
    compare_artists_tool,
    get_viral_tracks_tool,
    get_summary_stats_tool,
    analyze_monetization_tool
)


# Определяем инструменты как LangChain tools
@tool
def get_top_tracks(limit: int = 10, sort_by: str = "revenue") -> str:
    """
    Получить топ треков по доходу или стримам.
    
    Args:
        limit: количество треков (по умолчанию 10)
        sort_by: поле для сортировки - 'revenue' (доход), 'streams' (стримы), 'avg_rate' (ставка)
    
    Returns:
        JSON с топ треками
    """
    return get_top_tracks_tool(limit, sort_by)

@tool
def get_top_artists(limit: int = 10, sort_by: str = "revenue") -> str:
    """
    Получить топ артистов по доходу, стримам или количеству треков.
    
    Args:
        limit: количество артистов (по умолчанию 10)
        sort_by: поле для сортировки - 'revenue', 'streams', 'tracks_count', 'avg_rate'
    
    Returns:
        JSON с топ артистами
    """
    return get_top_artists_tool(limit, sort_by)

@tool
def search_track(query: str) -> str:
    """
    Поиск трека по названию (частичное совпадение).
    
    Args:
        query: поисковый запрос (название трека или его часть)
    
    Returns:
        JSON со списком найденных треков
    """
    return search_track_tool(query)

@tool
def search_artist(query: str) -> str:
    """
    Поиск артиста по имени (частичное совпадение).
    
    Args:
        query: поисковый запрос (имя артиста или его часть)
    
    Returns:
        JSON со списком найденных артистов
    """
    return search_artist_tool(query)

@tool
def get_track_details(track_name: str, artist_name: str = "") -> str:
    """
    Получить детальную информацию о треке: платформы, страны, типы подписок, динамика по месяцам.
    
    Args:
        track_name: название трека
        artist_name: имя артиста (опционально, для уточнения)
    
    Returns:
        JSON с детальной информацией о треке
    """
    return get_track_details_tool(track_name, artist_name)

@tool
def get_artist_tracks(artist_name: str) -> str:
    """
    Получить все треки артиста, отсортированные по доходу.
    
    Args:
        artist_name: имя артиста
    
    Returns:
        JSON со списком всех треков артиста
    """
    return get_artist_tracks_tool(artist_name)

@tool
def get_platform_stats(platform_name: str = "") -> str:
    """
    Получить статистику по платформе (Spotify, Apple Music, YouTube и т.д.).
    Если platform_name не указан, вернет статистику по всем платформам.
    
    Args:
        platform_name: название платформы (опционально)
    
    Returns:
        JSON со статистикой по платформе(ам)
    """
    return get_platform_stats_tool(platform_name)

@tool
def get_country_stats(country_name: str = "") -> str:
    """
    Получить статистику по стране.
    Если country_name не указан, вернет топ-20 стран.
    
    Args:
        country_name: название страны (опционально)
    
    Returns:
        JSON со статистикой по стране(ам)
    """
    return get_country_stats_tool(country_name)

@tool
def get_artist_timeline(artist_name: str) -> str:
    """
    Получить временную динамику артиста по месяцам (июль-декабрь 2025).
    
    Args:
        artist_name: имя артиста
    
    Returns:
        JSON с данными по месяцам
    """
    return get_artist_timeline_tool(artist_name)

@tool
def compare_artists(artist1: str, artist2: str) -> str:
    """
    Сравнить двух артистов по всем метрикам.
    
    Args:
        artist1: имя первого артиста
        artist2: имя второго артиста
    
    Returns:
        JSON со сравнительной статистикой
    """
    return compare_artists_tool(artist1, artist2)

@tool
def get_viral_tracks(threshold: float = 10.0) -> str:
    """
    Найти вирусные треки с большими колебаниями стримов.
    Коэффициент вирусности = максимальные стримы за месяц / средние стримы.
    
    Args:
        threshold: минимальный коэффициент вирусности (по умолчанию 10.0)
    
    Returns:
        JSON со списком вирусных треков
    """
    return get_viral_tracks_tool(threshold)

@tool
def get_summary_stats() -> str:
    """
    Получить общую статистику: топ треки, артисты, платформы, страны.
    Используй это для общего обзора данных.
    
    Returns:
        JSON с общей статистикой
    """
    return get_summary_stats_tool()

@tool
def analyze_monetization(artist_name: str = "") -> str:
    """
    Анализ монетизации: средняя ставка за стрим, доход на трек и т.д.
    Если artist_name не указан, вернет общую статистику монетизации.
    
    Args:
        artist_name: имя артиста (опционально)
    
    Returns:
        JSON с анализом монетизации
    """
    return analyze_monetization_tool(artist_name)


# Список всех инструментов
tools = [
    get_top_tracks,
    get_top_artists,
    search_track,
    search_artist,
    get_track_details,
    get_artist_tracks,
    get_platform_stats,
    get_country_stats,
    get_artist_timeline,
    compare_artists,
    get_viral_tracks,
    get_summary_stats,
    analyze_monetization
]


# Состояние агента
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]


# Создаем LLM с инструментами
def create_agent(api_key: str, model: str = "claude-3-5-sonnet-20241022"):
    """Создает агента с LLM и инструментами"""
    
    llm = ChatAnthropic(
        model=model,
        api_key=api_key,
        temperature=0
    )
    
    llm_with_tools = llm.bind_tools(tools)
    
    return llm_with_tools


# Узел для вызова агента
def call_agent(state: AgentState, llm_with_tools):
    """Вызывает LLM агента"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# Определяем, продолжать ли работу или завершить
def should_continue(state: AgentState):
    """Определяет, нужно ли продолжать или завершить"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Если есть вызовы инструментов, продолжаем
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Иначе завершаем
    return END


# Создаем граф
def create_graph(api_key: str):
    """Создает LangGraph граф агента"""
    
    llm_with_tools = create_agent(api_key)
    
    # Создаем узел инструментов
    tool_node = ToolNode(tools)
    
    # Создаем граф
    workflow = StateGraph(AgentState)
    
    # Добавляем узлы
    workflow.add_node("agent", lambda state: call_agent(state, llm_with_tools))
    workflow.add_node("tools", tool_node)
    
    # Устанавливаем точку входа
    workflow.set_entry_point("agent")
    
    # Добавляем условное ребро
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # Добавляем ребро от инструментов обратно к агенту
    workflow.add_edge("tools", "agent")
    
    # Компилируем граф с памятью
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


# Функция для запуска агента
def run_agent(query: str, api_key: str, thread_id: str = "default"):
    """
    Запускает агента с запросом
    
    Args:
        query: запрос пользователя
        api_key: API ключ Anthropic
        thread_id: ID треда для сохранения истории
    
    Returns:
        Ответ агента
    """
    app = create_graph(api_key)
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Запускаем агента
    result = app.invoke(
        {"messages": [HumanMessage(content=query)]},
        config=config
    )
    
    # Возвращаем последнее сообщение
    return result["messages"][-1].content


# Интерактивный режим
def interactive_mode(api_key: str):
    """Интерактивный режим общения с агентом"""
    
    print("=" * 80)
    print("🤖 AI АГЕНТ АНАЛИТИКИ МУЗЫКАЛЬНЫХ ДАННЫХ")
    print("=" * 80)
    print("\nДоступные команды:")
    print("  - Введите ваш вопрос на русском или английском")
    print("  - 'exit' или 'quit' для выхода")
    print("  - 'clear' для очистки истории")
    print("\nПримеры запросов:")
    print("  • Покажи топ-10 треков по доходу")
    print("  • Найди информацию о треке Meili")
    print("  • Сравни артистов Yenlik и Shiza")
    print("  • Какие треки стали вирусными?")
    print("  • Анализ монетизации для артиста Ernar Amandyq")
    print("\n" + "=" * 80 + "\n")
    
    app = create_graph(api_key)
    thread_id = "interactive_session"
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        try:
            user_input = input("Вы: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'выход']:
                print("\n👋 До свидания!")
                break
            
            if user_input.lower() == 'clear':
                thread_id = f"session_{os.urandom(4).hex()}"
                config = {"configurable": {"thread_id": thread_id}}
                print("\n✓ История очищена\n")
                continue
            
            print("\n🤔 Думаю...\n")
            
            # Запускаем агента
            result = app.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            # Выводим ответ
            response = result["messages"][-1].content
            print(f"Агент: {response}\n")
            print("-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}\n")


if __name__ == "__main__":
    # Получаем API ключ из переменной окружения
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ Ошибка: установите переменную окружения ANTHROPIC_API_KEY")
        print("   export ANTHROPIC_API_KEY='your-api-key'")
        exit(1)
    
    # Запускаем интерактивный режим
    interactive_mode(api_key)
