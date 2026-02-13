#!/usr/bin/env python3
"""
SQL Agent API на FastAPI - преобразует естественные запросы в SQL
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import requests
from typing import List, Dict, Any, Optional
import uvicorn

load_dotenv('.env.db')

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

# FastAPI app
app = FastAPI(
    title="SQL Agent API",
    description="Преобразует естественные запросы в SQL и выполняет их на БД музыкальной аналитики",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic модели
class QueryRequest(BaseModel):
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Сколько заработал Yenlik?"
            }
        }

class DirectSQLRequest(BaseModel):
    sql: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "sql": "SELECT * FROM artists LIMIT 10"
            }
        }

class QueryResponse(BaseModel):
    query: str
    sql: str
    explanation: str
    success: bool
    data: List[Dict[str, Any]]
    count: int
    error: Optional[str] = None

class DirectSQLResponse(BaseModel):
    sql: str
    success: bool
    data: List[Dict[str, Any]]
    count: int
    error: Optional[str] = None

class SchemaResponse(BaseModel):
    tables: List[str]
    views: List[str]
    statistics: Dict[str, int]
    schema_description: str

class ExampleItem(BaseModel):
    query: str
    description: str

class ExamplesResponse(BaseModel):
    examples: List[ExampleItem]

class TelegramRequest(BaseModel):
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Сколько заработал Yenlik?"
            }
        }

class TelegramResponse(BaseModel):
    query: str
    telegram_message: str
    success: bool
    error: Optional[str] = None


def format_for_telegram(query: str, sql: str, data: List[Dict], explanation: str) -> str:
    """
    Форматирует результаты запроса для Telegram с Markdown
    """
    message = f"🎵 *Результаты запроса*\n\n"
    message += f"❓ _{query}_\n\n"
    
    if not data:
        message += "❌ Нет данных\n"
        return message
    
    # Если один результат с одним полем (например, сумма)
    if len(data) == 1 and len(data[0]) == 1:
        key = list(data[0].keys())[0]
        value = data[0][key]
        
        # Форматирование в зависимости от типа
        if 'revenue' in key.lower() or 'выручка' in key.lower():
            message += f"💰 *Выручка:* `${value:,.2f}`\n"
        elif 'stream' in key.lower() or 'стрим' in key.lower():
            message += f"🎧 *Стримы:* `{value:,}`\n"
        elif 'count' in key.lower() or 'количество' in key.lower():
            message += f"📊 *Количество:* `{value:,}`\n"
        else:
            message += f"📊 *{key}:* `{value}`\n"
    
    # Если один результат с несколькими полями
    elif len(data) == 1:
        message += "📊 *Результат:*\n\n"
        for key, value in data[0].items():
            if value is None:
                continue
            
            # Форматирование значений
            if isinstance(value, (int, float)):
                if 'revenue' in key.lower():
                    formatted_value = f"${value:,.2f}"
                elif 'stream' in key.lower():
                    formatted_value = f"{value:,}"
                elif 'rate' in key.lower():
                    formatted_value = f"{value:.6f}"
                else:
                    formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
            
            # Эмодзи для полей
            emoji = "•"
            if 'revenue' in key.lower():
                emoji = "💰"
            elif 'stream' in key.lower():
                emoji = "🎧"
            elif 'track' in key.lower():
                emoji = "🎵"
            elif 'artist' in key.lower():
                emoji = "👤"
            elif 'platform' in key.lower():
                emoji = "📱"
            elif 'country' in key.lower():
                emoji = "🌍"
            
            message += f"{emoji} *{key}:* `{formatted_value}`\n"
    
    # Если несколько результатов (топ, список)
    else:
        message += f"📊 *Топ {len(data)} результатов:*\n\n"
        
        for i, row in enumerate(data[:10], 1):  # Максимум 10 для Telegram
            # Определяем основные поля
            name = row.get('track_name') or row.get('artist_name') or row.get('platform_name') or row.get('country_name') or row.get('label_name')
            revenue = row.get('total_revenue') or row.get('revenue')
            streams = row.get('total_streams') or row.get('streams')
            
            if name:
                message += f"*{i}. {name}*\n"
                
                if revenue:
                    try:
                        rev_float = float(revenue)
                        message += f"   💰 ${rev_float:,.2f}"
                    except:
                        message += f"   💰 ${revenue}"
                
                if streams:
                    try:
                        streams_int = int(streams)
                        message += f" | 🎧 {streams_int:,}"
                    except:
                        message += f" | 🎧 {streams}"
                
                message += "\n"
            else:
                # Если нет основного имени, выводим все поля
                message += f"*{i}.*\n"
                for key, value in row.items():
                    if value is not None:
                        message += f"   • {key}: `{value}`\n"
        
        if len(data) > 10:
            message += f"\n_...и еще {len(data) - 10} результатов_\n"
    
    # Добавляем объяснение
    if explanation:
        message += f"\n💡 _{explanation}_\n"
    
    return message


def get_db_connection():
    """Получить подключение к БД"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def generate_sql_query(user_query: str) -> dict:
    """Генерирует SQL запрос из естественного языка используя Alem AI"""
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
8. ВАЖНО: Для треков конкретного артиста используй таблицы tracks и artists с JOIN

ПРИМЕРЫ:

Запрос: "Сколько заработал Yenlik?"
SQL: SELECT ROUND(SUM(aa.total_revenue)::numeric, 2) AS total_revenue FROM artists a JOIN artist_aggregates aa ON a.artist_id = aa.artist_id WHERE a.artist_name ILIKE 'Yenlik';

Запрос: "Топ 10 треков"
SQL: SELECT * FROM v_top_tracks_by_revenue LIMIT 10;

Запрос: "Топ 5 треков Yenlik"
SQL: SELECT t.track_name, a.artist_name, ta.total_revenue, ta.total_streams FROM tracks t JOIN artists a ON t.artist_id = a.artist_id JOIN track_aggregates ta ON t.track_id = ta.track_id WHERE a.artist_name ILIKE 'Yenlik' ORDER BY ta.total_revenue DESC LIMIT 5;

Запрос: "Yenlik на Spotify"
SQL: SELECT a.artist_name, p.platform_name, SUM(tps.revenue) as total_revenue, SUM(tps.streams) as total_streams FROM artists a JOIN tracks t ON a.artist_id = t.artist_id JOIN track_platform_stats tps ON t.track_id = tps.track_id JOIN platforms p ON tps.platform_id = p.platform_id WHERE a.artist_name ILIKE 'Yenlik' AND p.platform_name ILIKE 'Spotify' GROUP BY a.artist_name, p.platform_name;

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
        import json
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
    """Выполняет SQL запрос и возвращает результаты"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql)
        results = cursor.fetchall()
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


# Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Корневой endpoint"""
    return {
        "service": "SQL Agent API",
        "version": "1.0.0",
        "status": "ok",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Проверка работоспособности"""
    return {"status": "ok", "service": "SQL Agent API"}


@app.post("/api/query", response_model=QueryResponse, tags=["Query"])
async def query(request: QueryRequest):
    """
    Основная ручка для запросов на естественном языке
    
    Преобразует запрос пользователя в SQL и выполняет его.
    
    **Примеры запросов:**
    - "Сколько заработал Yenlik?"
    - "Топ 10 треков по выручке"
    - "Yenlik на Spotify в Казахстане"
    """
    user_query = request.query
    
    # 1. Генерируем SQL
    sql_result = generate_sql_query(user_query)
    
    if not sql_result.get('sql'):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Не удалось сгенерировать SQL",
                "details": sql_result.get('explanation')
            }
        )
    
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
    
    return response


@app.post("/api/direct-sql", response_model=DirectSQLResponse, tags=["Query"])
async def direct_sql(request: DirectSQLRequest):
    """
    Прямое выполнение SQL запроса (для отладки)
    
    **Пример:**
    ```json
    {
        "sql": "SELECT * FROM artists LIMIT 10"
    }
    ```
    """
    sql_query = request.sql
    
    # Выполняем SQL
    result = execute_sql_query(sql_query)
    
    return {
        "sql": sql_query,
        "success": result['success'],
        "data": result.get('data', []),
        "count": result.get('count', 0),
        "error": result.get('error')
    }


@app.get("/api/schema", response_model=SchemaResponse, tags=["Schema"])
async def schema():
    """
    Получить схему БД
    
    Возвращает список таблиц, представлений и статистику по записям.
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
        
        return {
            "tables": tables,
            "views": views,
            "statistics": stats,
            "schema_description": DB_SCHEMA
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения схемы: {str(e)}")


@app.get("/api/examples", response_model=ExamplesResponse, tags=["Examples"])
async def examples():
    """
    Примеры запросов
    
    Возвращает список примеров запросов на естественном языке.
    """
    return {
        "examples": [
            {"query": "Сколько заработал Yenlik?", "description": "Общая выручка артиста"},
            {"query": "Топ 10 треков по выручке", "description": "Самые прибыльные треки"},
            {"query": "Yenlik на Spotify в Казахстане", "description": "Выручка артиста на конкретной платформе в стране"},
            {"query": "Сколько стримов у трека Meili?", "description": "Статистика конкретного трека"},
            {"query": "Топ 5 платформ по выручке", "description": "Самые прибыльные платформы"},
            {"query": "Какие треки у Ernar Amandyq?", "description": "Список треков артиста"},
            {"query": "Топ 10 стран по выручке", "description": "География выручки"},
            {"query": "Динамика Yenlik по месяцам", "description": "Помесячная статистика артиста"},
            {"query": "Средняя ставка на Apple Music", "description": "Средняя выручка за стрим на платформе"},
            {"query": "Сколько артистов у лейбла õzen?", "description": "Количество артистов лейбла"}
        ]
    }


@app.post("/api/telegram", response_model=TelegramResponse, tags=["Telegram"])
async def telegram_query(request: TelegramRequest):
    """
    Запрос для Telegram бота
    
    Преобразует запрос в SQL, выполняет его и форматирует результат
    для отправки в Telegram с красивым Markdown форматированием.
    
    **Примеры запросов:**
    - "Сколько заработал Yenlik?"
    - "Топ 5 треков"
    - "Yenlik на Spotify"
    
    **Возвращает:**
    - Готовое сообщение для Telegram с эмодзи и форматированием
    """
    user_query = request.query
    
    try:
        # 1. Генерируем SQL
        sql_result = generate_sql_query(user_query)
        
        if not sql_result.get('sql'):
            return {
                "query": user_query,
                "telegram_message": f"❌ *Ошибка*\n\nНе удалось обработать запрос: _{user_query}_",
                "success": False,
                "error": sql_result.get('explanation')
            }
        
        sql_query = sql_result['sql']
        explanation = sql_result.get('explanation', '')
        
        # 2. Выполняем SQL
        query_result = execute_sql_query(sql_query)
        
        if not query_result['success']:
            return {
                "query": user_query,
                "telegram_message": f"❌ *Ошибка выполнения*\n\n_{query_result.get('error')}_",
                "success": False,
                "error": query_result.get('error')
            }
        
        # 3. Форматируем для Telegram
        telegram_message = format_for_telegram(
            user_query,
            sql_query,
            query_result.get('data', []),
            explanation
        )
        
        return {
            "query": user_query,
            "telegram_message": telegram_message,
            "success": True
        }
        
    except Exception as e:
        return {
            "query": user_query,
            "telegram_message": f"❌ *Ошибка*\n\n_{str(e)}_",
            "success": False,
            "error": str(e)
        }


if __name__ == '__main__':
    print("🚀 Запуск SQL Agent API (FastAPI)...")
    print("📊 База данных:", DB_CONFIG['database'])
    print("🤖 LLM: Alem AI (qwen3)")
    print("🌐 API доступен на: http://localhost:8006")
    print("📚 Документация: http://localhost:8006/docs")
    print("📖 ReDoc: http://localhost:8006/redoc")
    
    uvicorn.run(app, host="0.0.0.0", port=8006)
