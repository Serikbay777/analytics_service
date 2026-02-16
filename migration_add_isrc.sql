-- ============================================================================
-- МИГРАЦИЯ: Добавление ISRC в таблицу tracks
-- ============================================================================
-- Дата: 2026-02-16
-- Описание: Добавляем колонку ISRC для уникальной идентификации треков
-- ============================================================================

BEGIN;

-- Шаг 1: Добавляем колонку ISRC
ALTER TABLE tracks ADD COLUMN IF NOT EXISTS isrc VARCHAR(50);

-- Шаг 2: Создаём индекс для быстрого поиска по ISRC
CREATE INDEX IF NOT EXISTS idx_tracks_isrc ON tracks(isrc);

-- Шаг 3: Удаляем старый constraint (track_name, artist_id)
-- и добавляем новый constraint по ISRC
ALTER TABLE tracks DROP CONSTRAINT IF EXISTS tracks_track_name_artist_id_key;

-- Шаг 4: Добавляем UNIQUE constraint на ISRC
-- (только для записей с непустым ISRC)
CREATE UNIQUE INDEX IF NOT EXISTS tracks_isrc_unique 
ON tracks(isrc) 
WHERE isrc IS NOT NULL AND isrc != '';

-- Шаг 5: Для записей без ISRC оставляем старый constraint
CREATE UNIQUE INDEX IF NOT EXISTS tracks_name_artist_unique_no_isrc 
ON tracks(track_name, artist_id) 
WHERE isrc IS NULL OR isrc = '';

COMMIT;

-- Проверка результата
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'tracks' 
ORDER BY ordinal_position;

-- Проверка индексов
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'tracks';
