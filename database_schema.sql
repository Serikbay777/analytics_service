-- =====================================================
-- МУЗЫКАЛЬНАЯ АНАЛИТИКА - СХЕМА БАЗЫ ДАННЫХ
-- =====================================================

-- Основные справочники (Dimension Tables)
-- =====================================================

-- Лейблы
CREATE TABLE labels (
    label_id SERIAL PRIMARY KEY,
    label_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Артисты
CREATE TABLE artists (
    artist_id SERIAL PRIMARY KEY,
    artist_name VARCHAR(255) NOT NULL,
    label_id INTEGER REFERENCES labels(label_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(artist_name, label_id)
);

-- Треки
CREATE TABLE tracks (
    track_id SERIAL PRIMARY KEY,
    track_name VARCHAR(500) NOT NULL,
    artist_id INTEGER REFERENCES artists(artist_id),
    label_id INTEGER REFERENCES labels(label_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(track_name, artist_id)
);

-- Платформы
CREATE TABLE platforms (
    platform_id SERIAL PRIMARY KEY,
    platform_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Страны
CREATE TABLE countries (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Типы подписок
CREATE TABLE subscription_types (
    subscription_type_id SERIAL PRIMARY KEY,
    subscription_type_name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Агрегированные таблицы (Fact Tables)
-- =====================================================

-- Агрегация по трекам (из tracks_aggregated.json)
CREATE TABLE track_aggregates (
    track_aggregate_id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(track_id),
    total_revenue DECIMAL(15, 10) NOT NULL,
    total_streams BIGINT NOT NULL,
    avg_rate DECIMAL(15, 10),
    platforms_count INTEGER,
    countries_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Агрегация по артистам (из artists_aggregated.json)
CREATE TABLE artist_aggregates (
    artist_aggregate_id SERIAL PRIMARY KEY,
    artist_id INTEGER REFERENCES artists(artist_id),
    total_revenue DECIMAL(15, 10) NOT NULL,
    total_streams BIGINT NOT NULL,
    tracks_count INTEGER NOT NULL,
    avg_rate DECIMAL(15, 10),
    avg_revenue_per_track DECIMAL(15, 10),
    platforms_count INTEGER,
    countries_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Агрегация по платформам (из platforms_aggregated.json)
CREATE TABLE platform_aggregates (
    platform_aggregate_id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES platforms(platform_id),
    total_revenue DECIMAL(15, 10) NOT NULL,
    total_streams BIGINT NOT NULL,
    tracks_count INTEGER NOT NULL,
    artists_count INTEGER NOT NULL,
    avg_rate DECIMAL(15, 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Детальные таблицы (Detailed Fact Tables)
-- =====================================================

-- Детальная статистика по трекам и платформам (из track_details.json)
CREATE TABLE track_platform_stats (
    track_platform_stat_id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(track_id),
    platform_id INTEGER REFERENCES platforms(platform_id),
    streams BIGINT NOT NULL,
    revenue DECIMAL(15, 10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(track_id, platform_id)
);

-- Детальная статистика по трекам и странам (из track_details.json)
CREATE TABLE track_country_stats (
    track_country_stat_id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(track_id),
    country_id INTEGER REFERENCES countries(country_id),
    streams BIGINT NOT NULL,
    revenue DECIMAL(15, 10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(track_id, country_id)
);

-- Детальная статистика по трекам и типам подписок (из track_details.json)
CREATE TABLE track_subscription_stats (
    track_subscription_stat_id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(track_id),
    subscription_type_id INTEGER REFERENCES subscription_types(subscription_type_id),
    streams BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(track_id, subscription_type_id)
);

-- Помесячная статистика по трекам (из track_details.json)
CREATE TABLE track_monthly_stats (
    track_monthly_stat_id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(track_id),
    month_date DATE NOT NULL,
    streams BIGINT NOT NULL,
    revenue DECIMAL(15, 10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(track_id, month_date)
);

-- Помесячная статистика по артистам (из monthly_aggregated.json)
CREATE TABLE artist_monthly_stats (
    artist_monthly_stat_id SERIAL PRIMARY KEY,
    artist_id INTEGER REFERENCES artists(artist_id),
    month_date DATE NOT NULL,
    streams BIGINT NOT NULL,
    revenue DECIMAL(15, 10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(artist_id, month_date)
);


-- Связующие таблицы (Many-to-Many)
-- =====================================================

-- Связь треков с платформами (для быстрого поиска)
CREATE TABLE track_platforms (
    track_id INTEGER REFERENCES tracks(track_id),
    platform_id INTEGER REFERENCES platforms(platform_id),
    PRIMARY KEY (track_id, platform_id)
);

-- Связь треков со странами (для быстрого поиска)
CREATE TABLE track_countries (
    track_id INTEGER REFERENCES tracks(track_id),
    country_id INTEGER REFERENCES countries(country_id),
    PRIMARY KEY (track_id, country_id)
);

-- Связь артистов с платформами (для быстрого поиска)
CREATE TABLE artist_platforms (
    artist_id INTEGER REFERENCES artists(artist_id),
    platform_id INTEGER REFERENCES platforms(platform_id),
    PRIMARY KEY (artist_id, platform_id)
);

-- Связь артистов со странами (для быстрого поиска)
CREATE TABLE artist_countries (
    artist_id INTEGER REFERENCES artists(artist_id),
    country_id INTEGER REFERENCES countries(country_id),
    PRIMARY KEY (artist_id, country_id)
);


-- Индексы для оптимизации запросов
-- =====================================================

-- Индексы для треков
CREATE INDEX idx_tracks_artist_id ON tracks(artist_id);
CREATE INDEX idx_tracks_label_id ON tracks(label_id);
CREATE INDEX idx_tracks_name ON tracks(track_name);

-- Индексы для артистов
CREATE INDEX idx_artists_label_id ON artists(label_id);
CREATE INDEX idx_artists_name ON artists(artist_name);

-- Индексы для агрегатов треков
CREATE INDEX idx_track_aggregates_track_id ON track_aggregates(track_id);
CREATE INDEX idx_track_aggregates_revenue ON track_aggregates(total_revenue DESC);
CREATE INDEX idx_track_aggregates_streams ON track_aggregates(total_streams DESC);

-- Индексы для агрегатов артистов
CREATE INDEX idx_artist_aggregates_artist_id ON artist_aggregates(artist_id);
CREATE INDEX idx_artist_aggregates_revenue ON artist_aggregates(total_revenue DESC);
CREATE INDEX idx_artist_aggregates_streams ON artist_aggregates(total_streams DESC);

-- Индексы для платформ
CREATE INDEX idx_platform_aggregates_platform_id ON platform_aggregates(platform_id);
CREATE INDEX idx_platform_aggregates_revenue ON platform_aggregates(total_revenue DESC);

-- Индексы для детальной статистики
CREATE INDEX idx_track_platform_stats_track_id ON track_platform_stats(track_id);
CREATE INDEX idx_track_platform_stats_platform_id ON track_platform_stats(platform_id);
CREATE INDEX idx_track_country_stats_track_id ON track_country_stats(track_id);
CREATE INDEX idx_track_country_stats_country_id ON track_country_stats(country_id);

-- Индексы для помесячной статистики
CREATE INDEX idx_track_monthly_stats_track_id ON track_monthly_stats(track_id);
CREATE INDEX idx_track_monthly_stats_month ON track_monthly_stats(month_date);
CREATE INDEX idx_artist_monthly_stats_artist_id ON artist_monthly_stats(artist_id);
CREATE INDEX idx_artist_monthly_stats_month ON artist_monthly_stats(month_date);


-- Представления (Views) для удобных запросов
-- =====================================================

-- Полная информация о треках с агрегатами
CREATE VIEW v_tracks_full AS
SELECT 
    t.track_id,
    t.track_name,
    a.artist_name,
    l.label_name,
    ta.total_revenue,
    ta.total_streams,
    ta.avg_rate,
    ta.platforms_count,
    ta.countries_count
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN labels l ON t.label_id = l.label_id
LEFT JOIN track_aggregates ta ON t.track_id = ta.track_id;

-- Полная информация об артистах с агрегатами
CREATE VIEW v_artists_full AS
SELECT 
    a.artist_id,
    a.artist_name,
    l.label_name,
    aa.total_revenue,
    aa.total_streams,
    aa.tracks_count,
    aa.avg_rate,
    aa.avg_revenue_per_track,
    aa.platforms_count,
    aa.countries_count
FROM artists a
JOIN labels l ON a.label_id = l.label_id
LEFT JOIN artist_aggregates aa ON a.artist_id = aa.artist_id;

-- Топ треков по выручке
CREATE VIEW v_top_tracks_by_revenue AS
SELECT 
    t.track_name,
    a.artist_name,
    l.label_name,
    ta.total_revenue,
    ta.total_streams,
    ta.avg_rate
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN labels l ON t.label_id = l.label_id
JOIN track_aggregates ta ON t.track_id = ta.track_id
ORDER BY ta.total_revenue DESC;

-- Топ артистов по выручке
CREATE VIEW v_top_artists_by_revenue AS
SELECT 
    a.artist_name,
    l.label_name,
    aa.total_revenue,
    aa.total_streams,
    aa.tracks_count,
    aa.avg_revenue_per_track
FROM artists a
JOIN labels l ON a.label_id = l.label_id
JOIN artist_aggregates aa ON a.artist_id = aa.artist_id
ORDER BY aa.total_revenue DESC;

-- Топ платформ по выручке
CREATE VIEW v_top_platforms_by_revenue AS
SELECT 
    p.platform_name,
    pa.total_revenue,
    pa.total_streams,
    pa.tracks_count,
    pa.artists_count,
    pa.avg_rate
FROM platforms p
JOIN platform_aggregates pa ON p.platform_id = pa.platform_id
ORDER BY pa.total_revenue DESC;

-- Помесячная динамика по артистам
CREATE VIEW v_artist_monthly_trends AS
SELECT 
    a.artist_name,
    l.label_name,
    ams.month_date,
    ams.streams,
    ams.revenue
FROM artist_monthly_stats ams
JOIN artists a ON ams.artist_id = a.artist_id
JOIN labels l ON a.label_id = l.label_id
ORDER BY a.artist_name, ams.month_date;

-- Помесячная динамика по трекам
CREATE VIEW v_track_monthly_trends AS
SELECT 
    t.track_name,
    a.artist_name,
    tms.month_date,
    tms.streams,
    tms.revenue
FROM track_monthly_stats tms
JOIN tracks t ON tms.track_id = t.track_id
JOIN artists a ON t.artist_id = a.artist_id
ORDER BY t.track_name, tms.month_date;


-- Комментарии к таблицам
-- =====================================================

COMMENT ON TABLE labels IS 'Справочник лейблов';
COMMENT ON TABLE artists IS 'Справочник артистов';
COMMENT ON TABLE tracks IS 'Справочник треков';
COMMENT ON TABLE platforms IS 'Справочник платформ (Spotify, Apple Music, и т.д.)';
COMMENT ON TABLE countries IS 'Справочник стран';
COMMENT ON TABLE subscription_types IS 'Типы подписок (Premium, Freemium, Ad Supported)';

COMMENT ON TABLE track_aggregates IS 'Агрегированная статистика по трекам';
COMMENT ON TABLE artist_aggregates IS 'Агрегированная статистика по артистам';
COMMENT ON TABLE platform_aggregates IS 'Агрегированная статистика по платформам';

COMMENT ON TABLE track_platform_stats IS 'Детальная статистика: трек + платформа';
COMMENT ON TABLE track_country_stats IS 'Детальная статистика: трек + страна';
COMMENT ON TABLE track_subscription_stats IS 'Детальная статистика: трек + тип подписки';
COMMENT ON TABLE track_monthly_stats IS 'Помесячная статистика по трекам';
COMMENT ON TABLE artist_monthly_stats IS 'Помесячная статистика по артистам';

COMMENT ON VIEW v_tracks_full IS 'Полная информация о треках с агрегатами';
COMMENT ON VIEW v_artists_full IS 'Полная информация об артистах с агрегатами';
COMMENT ON VIEW v_top_tracks_by_revenue IS 'Топ треков по выручке';
COMMENT ON VIEW v_top_artists_by_revenue IS 'Топ артистов по выручке';
COMMENT ON VIEW v_top_platforms_by_revenue IS 'Топ платформ по выручке';
