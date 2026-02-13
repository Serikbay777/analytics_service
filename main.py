"""
FastAPI приложение для AI агента аналитики музыкальных данных
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api.routes import router

# Создаем приложение
app = FastAPI(
    title="🎵 AI Analytics Agent API",
    description="""
    AI агент для аналитики музыкальных данных на базе OpenAI GPT-4o.
    
    ## Возможности
    
    - 🔍 Поиск треков и артистов
    - 📊 Топы по доходу и стримам
    - 📈 Детальная аналитика
    - 🌍 География и платформы
    - 🔬 Специальная аналитика
    
    ## Инструменты (13 шт.)
    
    1. **get_top_tracks** - Топ треков
    2. **get_top_artists** - Топ артистов
    3. **search_track** - Поиск трека
    4. **search_artist** - Поиск артиста
    5. **get_track_details** - Детали трека
    6. **get_artist_tracks** - Треки артиста
    7. **get_platform_stats** - Статистика платформ
    8. **get_country_stats** - Статистика стран
    9. **get_artist_timeline** - Динамика артиста
    10. **compare_artists** - Сравнение артистов
    11. **get_viral_tracks** - Вирусные треки
    12. **get_summary_stats** - Общая статистика
    13. **analyze_monetization** - Анализ монетизации
    
    ## Примеры запросов
    
    - "Покажи топ-10 треков по доходу"
    - "Найди информацию о треке Meili"
    - "Кто такой Yenlik?"
    - "Сравни артистов Yenlik и Shiza"
    - "Какие треки стали вирусными?"
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(router, prefix="/api/v1", tags=["Agent"])


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Analytics Agent</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            h1 {
                font-size: 3em;
                margin: 0 0 20px 0;
                text-align: center;
            }
            .subtitle {
                text-align: center;
                font-size: 1.2em;
                opacity: 0.9;
                margin-bottom: 40px;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }
            .feature {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
            .links {
                display: flex;
                gap: 20px;
                justify-content: center;
                margin-top: 40px;
            }
            .btn {
                padding: 15px 30px;
                background: white;
                color: #667eea;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                transition: transform 0.2s;
            }
            .btn:hover {
                transform: translateY(-2px);
            }
            .stats {
                display: flex;
                justify-content: space-around;
                margin: 40px 0;
                text-align: center;
            }
            .stat-value {
                font-size: 2.5em;
                font-weight: bold;
            }
            .stat-label {
                opacity: 0.8;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 AI Analytics Agent</h1>
            <div class="subtitle">
                Интеллектуальный агент для аналитики музыкальных данных
            </div>
            
            <div class="stats">
                <div>
                    <div class="stat-value">13</div>
                    <div class="stat-label">Инструментов</div>
                </div>
                <div>
                    <div class="stat-value">3</div>
                    <div class="stat-label">Модели GPT</div>
                </div>
                <div>
                    <div class="stat-value">∞</div>
                    <div class="stat-label">Возможностей</div>
                </div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🔍</div>
                    <h3>Поиск</h3>
                    <p>Найди любой трек или артиста</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <h3>Топы</h3>
                    <p>Рейтинги по доходу и стримам</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📈</div>
                    <h3>Аналитика</h3>
                    <p>Детальная статистика</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🌍</div>
                    <h3>География</h3>
                    <p>Данные по странам</p>
                </div>
            </div>
            
            <div class="links">
                <a href="/docs" class="btn">📚 API Документация</a>
                <a href="/redoc" class="btn">📖 ReDoc</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/ping")
async def ping():
    """Простая проверка доступности"""
    return {"status": "ok", "message": "pong"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
