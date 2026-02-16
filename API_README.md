# 🚀 AI Analytics Agent - FastAPI

REST API для AI агента аналитики музыкальных данных.

## 📦 Структура проекта

```
analytics_scripts/
├── main.py                    # FastAPI приложение
├── api/
│   ├── __init__.py
│   ├── models.py             # Pydantic модели
│   ├── routes.py             # API роуты
│   └── services.py           # Бизнес-логика
├── analytics_agent_openai_simple.py  # AI агент
├── analytics_tools.py        # Инструменты
├── precalc_data/            # Данные
└── run_api.sh               # Скрипт запуска
```

## 🚀 Быстрый старт

### 1. Запуск сервера

```bash
# Способ 1: Через скрипт
./run_api.sh

# Способ 2: Напрямую
source venv/bin/activate
python main.py

# Способ 3: Через uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервер запустится на `http://localhost:8000`

### 2. Открыть документацию

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Главная:** http://localhost:8000

## 📡 API Endpoints

### 🏥 Health Check

**GET** `/api/v1/health`

Проверка здоровья сервиса.

```bash
curl http://localhost:8000/api/v1/health
```

Ответ:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_available": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
  "tools_count": 13
}
```

### 💬 Query Agent

**POST** `/api/v1/query`

Отправить запрос агенту.

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Покажи топ-5 треков по доходу",
    "model": "gpt-4o"
  }'
```

Ответ:
```json
{
  "query": "Покажи топ-5 треков по доходу",
  "answer": "Вот топ-5 треков по доходу:\n\n1. \"Meili\" - Yenlik...",
  "model": "gpt-4o",
  "execution_time": 3.45
}
```

### 🛠️ Get Tools

**GET** `/api/v1/tools`

Получить список инструментов.

```bash
curl http://localhost:8000/api/v1/tools
```

Ответ:
```json
{
  "tools": [
    {
      "name": "get_top_tracks",
      "description": "Получить топ треков по доходу или стримам..."
    },
    ...
  ],
  "count": 13
}
```

### 🤖 Get Models

**GET** `/api/v1/models`

Получить список моделей.

```bash
curl http://localhost:8000/api/v1/models
```

Ответ:
```json
{
  "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
  "default": "gpt-4o",
  "count": 3
}
```

## 💡 Примеры использования

### Python

```python
import requests

# Отправить запрос
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "Покажи топ-10 треков по доходу",
        "model": "gpt-4o"
    }
)

result = response.json()
print(result["answer"])
```

### JavaScript

```javascript
// Отправить запрос
const response = await fetch('http://localhost:8000/api/v1/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'Покажи топ-10 треков по доходу',
    model: 'gpt-4o'
  })
});

const result = await response.json();
console.log(result.answer);
```

### cURL

```bash
# Топ треков
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Покажи топ-10 треков по доходу"}'

# Поиск трека
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Найди информацию о треке Meili"}'

# Сравнение артистов
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Сравни артистов Yenlik и Shiza"}'
```

## 📊 Примеры запросов

### Топы и рейтинги

```json
{"query": "Покажи топ-10 треков по доходу"}
{"query": "Топ-5 артистов по стримам"}
{"query": "Самые популярные треки"}
```

### Поиск

```json
{"query": "Найди информацию о треке Meili"}
{"query": "Кто такой Yenlik?"}
{"query": "Найди артиста Shiza"}
```

### Аналитика

```json
{"query": "Сравни артистов Yenlik и Shiza"}
{"query": "Какие треки стали вирусными?"}
{"query": "Анализ монетизации для артиста Ernar Amandyq"}
```

### География и платформы

```json
{"query": "Статистика по платформе Spotify"}
{"query": "Топ-5 стран по доходу"}
{"query": "Динамика артиста Yenlik по месяцам"}
```

## 🔧 Конфигурация

### Переменные окружения (.env)

```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
```

### Доступные модели

- `gpt-4o` - Самая мощная (по умолчанию)
- `gpt-4o-mini` - Быстрая и дешевая
- `gpt-4-turbo` - Баланс скорости и качества

## 🎨 Swagger UI

Интерактивная документация доступна по адресу:

**http://localhost:8000/docs**

Там можно:
- 📖 Посмотреть все endpoints
- 🧪 Протестировать API
- 📝 Увидеть схемы данных
- 💡 Изучить примеры

## 🔒 CORS

По умолчанию разрешены запросы с любых доменов (`allow_origins=["*"]`).

Для продакшена измените в `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📈 Производительность

- **Простой запрос:** ~2-4 секунды
- **Сложный запрос:** ~5-10 секунд
- **Concurrent requests:** Поддерживается (async)

## 🐛 Решение проблем

### Ошибка: "Address already in use"

Порт 8000 занят. Используйте другой:

```bash
uvicorn main:app --port 8001
```

### Ошибка: "OPENAI_API_KEY не найден"

Проверьте `.env` файл и убедитесь, что ключ указан.

### Ошибка: "No such file or directory: 'precalc_data/metadata.json'"

Запустите прекалькуляцию:

```bash
python precalc_data.py
```

## 🚀 Деплой

### Docker (будущее)

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Render / Railway / Fly.io

1. Создайте `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Добавьте переменные окружения в панели управления

3. Deploy!

## 📚 Дополнительная документация

- [README.md](README.md) - Главная документация
- [OPENAI_SETUP.md](OPENAI_SETUP.md) - Настройка OpenAI
- [FINAL_REPORT.md](FINAL_REPORT.md) - Финальный отчет

---

**Сделано с ❤️ для õzen label**
