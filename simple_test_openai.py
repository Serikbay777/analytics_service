#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест OpenAI агента
"""

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from analytics_tools import get_top_tracks_tool

load_dotenv()

print('=' * 80)
print('🧪 ПРОСТОЙ ТЕСТ OPENAI С ИНСТРУМЕНТАМИ')
print('=' * 80)

api_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('OPENAI_MODEL', 'gpt-4o')

print(f'\n📡 API ключ: {api_key[:20]}...')
print(f'🤖 Модель: {model}')

# Создаем LLM
llm = ChatOpenAI(
    model=model,
    api_key=api_key,
    temperature=0
)

# Тест 1: Простой запрос без инструментов
print('\n' + '-' * 80)
print('ТЕСТ 1: Простой запрос без инструментов')
print('-' * 80)

try:
    response = llm.invoke([HumanMessage(content="Привет! Как дела?")])
    print(f'✅ Ответ: {response.content}')
except Exception as e:
    print(f'❌ Ошибка: {e}')

# Тест 2: Прямой вызов инструмента
print('\n' + '-' * 80)
print('ТЕСТ 2: Прямой вызов инструмента get_top_tracks')
print('-' * 80)

try:
    result = get_top_tracks_tool(5, "revenue")
    print(f'✅ Результат получен (первые 500 символов):')
    print(result[:500] + '...')
except Exception as e:
    print(f'❌ Ошибка: {e}')

# Тест 3: LLM с инструментами (function calling)
print('\n' + '-' * 80)
print('ТЕСТ 3: LLM с function calling')
print('-' * 80)

from langchain_core.tools import tool

@tool
def get_top_tracks(limit: int = 5) -> str:
    """Получить топ треков по доходу"""
    return get_top_tracks_tool(limit, "revenue")

llm_with_tools = llm.bind_tools([get_top_tracks])

try:
    response = llm_with_tools.invoke([
        HumanMessage(content="Покажи топ-5 треков по доходу")
    ])
    
    print(f'✅ Ответ получен!')
    print(f'Есть tool_calls: {hasattr(response, "tool_calls") and len(response.tool_calls) > 0}')
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f'\n🔧 Агент хочет вызвать инструмент:')
        for call in response.tool_calls:
            print(f'   • {call["name"]} с параметрами: {call["args"]}')
        
        print('\n✅ FUNCTION CALLING РАБОТАЕТ!')
    else:
        print(f'\n⚠️  Агент ответил без вызова инструментов:')
        print(f'   {response.content[:200]}...')
        
except Exception as e:
    print(f'❌ Ошибка: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 80)
print('ИТОГИ ТЕСТИРОВАНИЯ')
print('=' * 80)
