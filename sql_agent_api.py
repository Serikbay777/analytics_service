#!/usr/bin/env python3
"""
SQL Agent API - преобразует естественные запросы в SQL
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv('.env.db')

app = Flask(__name__)
CORS(app)

# Настройки БД
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'music_analytics'),
    'user': os.getenv('DB_USER', 'nuraliserikbay'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Alem AI API
ALEM_API_KEY = os.getenv('ALEM_API_KEY')
ALEM_API_URL = os.getenv('ALEM_API_URL', 'https://llm.alem.ai/v1/chat/completions')
ALEM_MODEL = os.getenv('ALEM_MODEL', 'qwen3')

# Схема БД для контекста
DB_SCHEMA = """
СХЕМА БАЗЫ ДАННЫХ:

Основные таблицы:
- labels (label_id, label_name)
- artists (artist_id, artist_name, label_id)
- tracks (track_id, track_name, artist_id, label_id)
- platforms (platform_id, platform_name) - Spotify, Apple Music, YouTube, etc.
- countries (country_id, country_name)

Агрегаты:
- track_aggregates (track_id, total_revenue, total_streams, avg_rate)
- artist_aggregates (artist_id, total_revenue, total_streams, tracks_count, avg_revenue_per_track)
- platform_aggregates (platform_id, total_revenue, total_streams, tracks_count, artists_count)

Детальная статистика:
- track_platform_stats (track_id, platform_id, streams, revenue)
- track_country_stats (track_id, country_id, streams, revenue)
- track_monthly_stats (track_id, month_date, streams, revenue)
- artist_monthly_stats (artist_id, month_date, streams, revenue)

Представления (views):
- v_top_tracks_by_revenue - топ треков по выручке
- v_top_artists_by_revenue - топ артистов по выручке
- v_top_platforms_by_revenue - топ платформ по выручке

Примеры запросов:
1. "Сколько заработал Yenlik?" -> SELECT SUM(total_revenue) FROM artist_aggregates JOIN artists ON...
2. "Топ 10 треков" -> SELECT * FROM v_top_tracks_by_revenue LIMIT 10
3. "Yenlik на Spotify в Казахстане" -> JOIN artists, tracks, track_platform_stats, platforms, track_country_stats, countries
"""


def get_db_connection():
    """Получить подключение к БД"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def generate_sql_query(user_query: str) -> dict:
    """
    Генерирует SQL запрос из естественного языка используя Alem AI
    """
    prompt = f"""Ты SQL эксперт. Преобразуй запрос пользователя в SQL запрос для PostgreSQL.

{DB_SCHEMA}

ПРАВИЛА:
1. Используй только таблицы из схемы выше
2. Всегда используй JOIN для связи таблиц
3. Для поиска по имени используй ILIKE для регистронезависимого поиска
4. Возвращай только SQL запрос без объяснений
5. Используй агрегатные функции (SUM, COUNT, AVG) где нужно
6. Добавляй LIMIT если не указано иное (по умолчанию 100)
7. Форматируй числа с помощью ROUND для денег (2 знака)

ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_query}

Верни JSON в формате:
{{
    "sql": "SELECT ...",
    "explanation": "Краткое объяснение что делает запрос"
}}"""

    try:
        headers = {
            'Authorization': f'Bearer {ALEM_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': ALEM_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.1,
            'max_tokens': 2000
        }
        
        response = requests.post(ALEM_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result_data = response.json()
        result_text = result_data['choices'][0]['message']['content']
        
        # Извлекаем JSON из ответа
        if '```json' in result_text:
            json_str = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            json_str = result_text.split('```')[1].split('```')[0].strip()
        else:
            json_str = result_text.strip()
        
        result = json.loads(json_str)
        return result
        
    except Exception as e:
        return {
            "sql": None,
            "explanation": f"Ошибка генерации SQL: {str(e)}"
        }


def execute_sql_query(sql: str) -> dict:
    """
    Выполняет SQL запрос и возвращает результаты
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql)
        
        # Получаем результаты
        results = cursor.fetchall()
        
        # Преобразуем в список словарей
        data = [dict(row) for row in results]
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }


@app.route('/health', methods=['GET'])
def health():
    """Проверка работоспособности"""
    return jsonify({"status": "ok", "service": "SQL Agent API"})


@app.route('/api/query', methods=['POST'])
def query():
    """
    Основная ручка для запросов
    
    POST /api/query
    {
        "query": "Сколько заработал Yenlik на Spotify в Казахстане?"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Требуется поле 'query'"
            }), 400
        
        user_query = data['query']
        
        # 1. Генерируем SQL
        sql_result = generate_sql_query(user_query)
        
        if not sql_result.get('sql'):
            return jsonify({
                "error": "Не удалось сгенерировать SQL",
                "details": sql_result.get('explanation')
            }), 400
        
        sql_query = sql_result['sql']
        explanation = sql_result.get('explanation', '')
        
        # 2. Выполняем SQL
        query_result = execute_sql_query(sql_query)
        
        # 3. Формируем ответ
        response = {
            "query": user_query,
            "sql": sql_query,
            "explanation": explanation,
            "success": query_result['success'],
            "data": query_result.get('data', []),
            "count": query_result.get('count', 0)
        }
        
        if not query_result['success']:
            response['error'] = query_result.get('error')
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "error": f"Ошибка сервера: {str(e)}"
        }), 500


@app.route('/api/direct-sql', methods=['POST'])
def direct_sql():
    """
    Прямое выполнение SQL запроса (для отладки)
    
    POST /api/direct-sql
    {
        "sql": "SELECT * FROM artists LIMIT 10"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'sql' not in data:
            return jsonify({
                "error": "Требуется поле 'sql'"
            }), 400
        
        sql_query = data['sql']
        
        # Выполняем SQL
        result = execute_sql_query(sql_query)
        
        return jsonify({
            "sql": sql_query,
            "success": result['success'],
            "data": result.get('data', []),
            "count": result.get('count', 0),
            "error": result.get('error')
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Ошибка сервера: {str(e)}"
        }), 500


@app.route('/api/schema', methods=['GET'])
def schema():
    """
    Получить схему БД
    
    GET /api/schema
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' AND table_type='BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row['table_name'] for row in cursor.fetchall()]
        
        # Получаем список представлений
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema='public'
            ORDER BY table_name
        """)
        views = [row['table_name'] for row in cursor.fetchall()]
        
        # Статистика
        stats = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            stats[table] = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "tables": tables,
            "views": views,
            "statistics": stats,
            "schema_description": DB_SCHEMA
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Ошибка получения схемы: {str(e)}"
        }), 500


@app.route('/api/examples', methods=['GET'])
def examples():
    """
    Примеры запросов
    
    GET /api/examples
    """
    return jsonify({
        "examples": [
            {
                "query": "Сколько заработал Yenlik?",
                "description": "Общая выручка артиста"
            },
            {
                "query": "Топ 10 треков по выручке",
                "description": "Самые прибыльные треки"
            },
            {
                "query": "Yenlik на Spotify в Казахстане",
                "description": "Выручка артиста на конкретной платформе в стране"
            },
            {
                "query": "Сколько стримов у трека Meili?",
                "description": "Статистика конкретного трека"
            },
            {
                "query": "Топ 5 платформ по выручке",
                "description": "Самые прибыльные платформы"
            },
            {
                "query": "Какие треки у Ernar Amandyq?",
                "description": "Список треков артиста"
            },
            {
                "query": "Топ 10 стран по выручке",
                "description": "География выручки"
            },
            {
                "query": "Динамика Yenlik по месяцам",
                "description": "Помесячная статистика артиста"
            },
            {
                "query": "Средняя ставка на Apple Music",
                "description": "Средняя выручка за стрим на платформе"
            },
            {
                "query": "Сколько артистов у лейбла õzen?",
                "description": "Количество артистов лейбла"
            }
        ]
    })


if __name__ == '__main__':
    print("🚀 Запуск SQL Agent API...")
    print("📊 База данных:", DB_CONFIG['database'])
    print("🤖 LLM: Alem AI (qwen3)")
    print("🌐 API доступен на: http://localhost:8006")
    print("\nПримеры запросов:")
    print("  POST http://localhost:8006/api/query")
    print('  {"query": "Сколько заработал Yenlik?"}')
    print("\n  GET http://localhost:8006/api/examples")
    print("  GET http://localhost:8006/api/schema")
    
    app.run(host='0.0.0.0', port=8006, debug=True)
