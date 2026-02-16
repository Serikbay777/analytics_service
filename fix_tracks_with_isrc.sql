-- ============================================================================
-- СКРИПТ ДЛЯ ИСПРАВЛЕНИЯ БД: ДОБАВЛЕНИЕ ISRC И ОБЪЕДИНЕНИЕ ДУБЛИКАТОВ
-- ============================================================================
-- Проблема: Трек "Meili" от Yenlik разбит на 2 записи из-за разных лейблов,
-- хотя у них одинаковый ISRC код (DG-A05-25-01737)
-- ============================================================================

-- ШАГ 1: Добавляем колонку ISRC в таблицу tracks
ALTER TABLE tracks ADD COLUMN IF NOT EXISTS isrc VARCHAR(50);

-- ШАГ 2: Создаём индекс на ISRC для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_tracks_isrc ON tracks(isrc);

-- ШАГ 3: Показываем текущее состояние (до исправления)
SELECT 
    t.track_id,
    t.track_name,
    a.artist_name,
    l.label_name,
    t.isrc,
    ta.total_revenue,
    ta.total_streams
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN labels l ON t.label_id = l.label_id
LEFT JOIN track_aggregates ta ON t.track_id = ta.track_id
WHERE t.track_name = 'Meili' AND a.artist_name = 'Yenlik'
ORDER BY ta.total_revenue DESC;

-- ============================================================================
-- ВАЖНО: Дальнейшие шаги нужно выполнять только после того, как:
-- 1. Пересоздадите precalc_data с ISRC (запустите precalc_data.py)
-- 2. Очистите и перезагрузите данные (запустите load_data_to_db.py)
-- ============================================================================

-- Для справки: после перезагрузки данных должна остаться только ОДНА запись
-- для трека "Meili" от Yenlik с ISRC = 'DG-A05-25-01737'
