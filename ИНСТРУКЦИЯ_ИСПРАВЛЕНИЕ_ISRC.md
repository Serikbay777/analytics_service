# 🔧 Инструкция: Исправление дубликатов треков через ISRC

## 📋 Проблема
Трек "Meili" от Yenlik разбит на **2 записи** в БД:
- **Запись 1**: Лейбл `õzen` → $3,808.86 (2.7M стримов)
- **Запись 2**: Лейбл `ÕZEÑ` → $1,100.88 (13.7M стримов)

**Причина**: Группировка по `(track_name, artist, label)` вместо `ISRC`

**Решение**: Использовать ISRC код для группировки (у обеих записей ISRC = `DG-A05-25-01737`)

---

## 🚀 Шаги исправления

### ШАГ 1: Обновить скрипт precalc_data.py (✅ УЖЕ СДЕЛАНО)
Файл `precalc_data.py` уже обновлён для группировки по ISRC.

### ШАГ 2: Пересоздать прекалькулированные данные
```bash
cd /path/to/analytics_scripts
python3 precalc_data.py
```

Это создаст новые файлы в `precalc_data/` с правильной группировкой по ISRC.

### ШАГ 3: Обновить схему БД на сервере
```bash
# Подключитесь к серверу и выполните:
psql -h <host> -U <user> -d music_analytics -f fix_tracks_with_isrc.sql
```

Или вручную:
```sql
-- Добавить колонку ISRC
ALTER TABLE tracks ADD COLUMN IF NOT EXISTS isrc VARCHAR(50);

-- Создать индекс
CREATE INDEX IF NOT EXISTS idx_tracks_isrc ON tracks(isrc);
```

### ШАГ 4: Очистить старые данные в БД
```sql
-- ВНИМАНИЕ: Это удалит все данные!
TRUNCATE TABLE track_subscription_stats CASCADE;
TRUNCATE TABLE track_monthly_stats CASCADE;
TRUNCATE TABLE track_country_stats CASCADE;
TRUNCATE TABLE track_platform_stats CASCADE;
TRUNCATE TABLE artist_monthly_stats CASCADE;
TRUNCATE TABLE track_countries CASCADE;
TRUNCATE TABLE track_platforms CASCADE;
TRUNCATE TABLE artist_countries CASCADE;
TRUNCATE TABLE artist_platforms CASCADE;
TRUNCATE TABLE track_aggregates CASCADE;
TRUNCATE TABLE artist_aggregates CASCADE;
TRUNCATE TABLE platform_aggregates CASCADE;
TRUNCATE TABLE tracks CASCADE;
TRUNCATE TABLE artists CASCADE;
TRUNCATE TABLE labels CASCADE;
TRUNCATE TABLE platforms CASCADE;
TRUNCATE TABLE countries CASCADE;
TRUNCATE TABLE subscription_types CASCADE;
```

### ШАГ 5: Обновить load_data_to_db.py
Нужно добавить загрузку ISRC в функцию `get_or_create_track()`:

```python
def get_or_create_track(self, track_name, artist_id, label_id, isrc=None):
    """Получить или создать трек"""
    # Если есть ISRC, используем его для уникальности
    if isrc and isrc.strip():
        cache_key = (isrc, track_name, artist_id)
        if cache_key in self.track_cache:
            return self.track_cache[cache_key]
        
        self.cursor.execute(
            """INSERT INTO tracks (track_name, artist_id, label_id, isrc) 
               VALUES (%s, %s, %s, %s) 
               ON CONFLICT (isrc) DO UPDATE SET track_name = EXCLUDED.track_name 
               RETURNING track_id""",
            (track_name, artist_id, label_id, isrc)
        )
    else:
        # Fallback: без ISRC (старая логика)
        cache_key = (track_name, artist_id)
        if cache_key in self.track_cache:
            return self.track_cache[cache_key]
        
        self.cursor.execute(
            """INSERT INTO tracks (track_name, artist_id, label_id) 
               VALUES (%s, %s, %s) 
               ON CONFLICT (track_name, artist_id) DO UPDATE SET track_name = EXCLUDED.track_name 
               RETURNING track_id""",
            (track_name, artist_id, label_id)
        )
    
    track_id = self.cursor.fetchone()[0]
    self.track_cache[cache_key] = track_id
    return track_id
```

### ШАГ 6: Перезагрузить данные
```bash
python3 load_data_to_db.py
```

### ШАГ 7: Проверить результат
```sql
-- Должна остаться ОДНА запись для Meili от Yenlik
SELECT 
    t.track_id,
    t.track_name,
    t.isrc,
    a.artist_name,
    l.label_name,
    ta.total_revenue,
    ta.total_streams
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN labels l ON t.label_id = l.label_id
LEFT JOIN track_aggregates ta ON t.track_id = ta.track_id
WHERE t.track_name = 'Meili' AND a.artist_name = 'Yenlik';
```

Ожидаемый результат:
```
track_id | track_name |      isrc       | artist_name | label_name | total_revenue | total_streams
---------|------------|-----------------|-------------|------------|---------------|---------------
    X    | Meili      | DG-A05-25-01737 | Yenlik      | õzen       | ~5994.47      | ~19208820
```

---

## ✅ Результат
После исправления:
- ✅ Один трек "Meili" вместо двух
- ✅ Объединённая статистика: **$5,994.47** и **~19.2M стримов**
- ✅ Правильная группировка по ISRC для всех треков
- ✅ Нет дубликатов из-за разных лейблов/релизов

---

## 📝 Примечания
1. **ISRC** - это уникальный код записи. Один трек может быть в разных альбомах, но ISRC один.
2. Некоторые старые записи могут не иметь ISRC - для них используется старая логика (track_name + artist_id).
3. После исправления SQL-агент будет возвращать правильные данные без дубликатов.
