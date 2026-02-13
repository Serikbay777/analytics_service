#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация работы AI агента с OpenAI
"""

from analytics_agent_openai_simple import run_agent
from dotenv import load_dotenv
import os

load_dotenv()

print('=' * 80)
print('🎉 ДЕМОНСТРАЦИЯ AI АГЕНТА С OPENAI GPT-4O')
print('=' * 80)

api_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('OPENAI_MODEL', 'gpt-4o')

print(f'\n📡 Модель: {model}')
print(f'🌐 Endpoint: https://api.openai.com/v1')
print(f'✅ Function Calling: Поддерживается')

# Список демо-запросов
demo_queries = [
    "Покажи топ-3 трека по доходу",
    "Кто такой Yenlik?",
    "Сравни Yenlik и Shiza"
]

for i, query in enumerate(demo_queries, 1):
    print('\n' + '=' * 80)
    print(f'ЗАПРОС {i}: {query}')
    print('=' * 80)
    print('\n⏳ Обрабатываю...\n')
    
    try:
        response = run_agent(query, api_key, model)
        print('✅ ОТВЕТ:')
        print('-' * 80)
        # Ограничиваем вывод для читаемости
        if len(response) > 800:
            print(response[:800] + '\n\n... (ответ обрезан для демо) ...')
        else:
            print(response)
        print('-' * 80)
    except Exception as e:
        print(f'❌ ОШИБКА: {e}')

print('\n' + '=' * 80)
print('🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!')
print('=' * 80)
print('\n💡 Для интерактивного режима запустите:')
print('   python analytics_agent_openai_simple.py')
print('\n📚 Документация: OPENAI_SETUP.md')
