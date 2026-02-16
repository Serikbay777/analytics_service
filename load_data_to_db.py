#!/usr/bin/env python3
"""
Скрипт для загрузки данных из JSON файлов в PostgreSQL
"""

import json
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
import os
from datetime import datetime
from collections import defaultdict

# Загрузка переменных окружения
load_dotenv('.env.db')

# Параметры подключения
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'music_analytics'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

class DataLoader:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
        # Кэши для ID
        self.label_cache = {}
        self.artist_cache = {}
        self.track_cache = {}
        self.platform_cache = {}
        self.country_cache = {}
        self.subscription_cache = {}
        
    def connect(self):
        """Подключение к БД"""
        print("🔌 Подключение к базе данных...")
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ Подключение установлено")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
    
    def disconnect(self):
        """Отключение от БД"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Соединение закрыто")
    
    def get_or_create_label(self, label_name):
        """Получить или создать лейбл"""
        if label_name in self.label_cache:
            return self.label_cache[label_name]
        
        self.cursor.execute(
            "INSERT INTO labels (label_name) VALUES (%s) ON CONFLICT (label_name) DO UPDATE SET label_name = EXCLUDED.label_name RETURNING label_id",
            (label_name,)
        )
        label_id = self.cursor.fetchone()[0]
        self.label_cache[label_name] = label_id
        return label_id
    
    def get_or_create_artist(self, artist_name, label_id):
        """Получить или создать артиста"""
        cache_key = (artist_name, label_id)
        if cache_key in self.artist_cache:
            return self.artist_cache[cache_key]
        
        self.cursor.execute(
            "INSERT INTO artists (artist_name, label_id) VALUES (%s, %s) ON CONFLICT (artist_name, label_id) DO UPDATE SET artist_name = EXCLUDED.artist_name RETURNING artist_id",
            (artist_name, label_id)
        )
        artist_id = self.cursor.fetchone()[0]
        self.artist_cache[cache_key] = artist_id
        return artist_id
    
    def get_or_create_track(self, track_name, artist_id, label_id, isrc=None):
        """Получить или создать трек"""
        # Если есть ISRC, используем его для уникальности
        if isrc and isrc.strip():
            cache_key = (isrc, track_name, artist_id)
            if cache_key in self.track_cache:
                return self.track_cache[cache_key]
            
            self.cursor.execute(
                "INSERT INTO tracks (track_name, artist_id, label_id, isrc) VALUES (%s, %s, %s, %s) ON CONFLICT (isrc) DO UPDATE SET track_name = EXCLUDED.track_name RETURNING track_id",
                (track_name, artist_id, label_id, isrc)
            )
            track_id = self.cursor.fetchone()[0]
            self.track_cache[cache_key] = track_id
            return track_id
        else:
            # Fallback: без ISRC (старая логика для записей без ISRC)
            cache_key = (track_name, artist_id)
            if cache_key in self.track_cache:
                return self.track_cache[cache_key]
            
            self.cursor.execute(
                "INSERT INTO tracks (track_name, artist_id, label_id) VALUES (%s, %s, %s) ON CONFLICT (track_name, artist_id) DO UPDATE SET track_name = EXCLUDED.track_name RETURNING track_id",
                (track_name, artist_id, label_id)
            )
            track_id = self.cursor.fetchone()[0]
            self.track_cache[cache_key] = track_id
            return track_id
    
    def get_or_create_platform(self, platform_name):
        """Получить или создать платформу"""
        if platform_name in self.platform_cache:
            return self.platform_cache[platform_name]
        
        self.cursor.execute(
            "INSERT INTO platforms (platform_name) VALUES (%s) ON CONFLICT (platform_name) DO UPDATE SET platform_name = EXCLUDED.platform_name RETURNING platform_id",
            (platform_name,)
        )
        platform_id = self.cursor.fetchone()[0]
        self.platform_cache[platform_name] = platform_id
        return platform_id
    
    def get_or_create_country(self, country_name):
        """Получить или создать страну"""
        if country_name in self.country_cache:
            return self.country_cache[country_name]
        
        self.cursor.execute(
            "INSERT INTO countries (country_name) VALUES (%s) ON CONFLICT (country_name) DO UPDATE SET country_name = EXCLUDED.country_name RETURNING country_id",
            (country_name,)
        )
        country_id = self.cursor.fetchone()[0]
        self.country_cache[country_name] = country_id
        return country_id
    
    def get_or_create_subscription_type(self, subscription_type_name):
        """Получить или создать тип подписки"""
        if subscription_type_name in self.subscription_cache:
            return self.subscription_cache[subscription_type_name]
        
        self.cursor.execute(
            "INSERT INTO subscription_types (subscription_type_name) VALUES (%s) ON CONFLICT (subscription_type_name) DO UPDATE SET subscription_type_name = EXCLUDED.subscription_type_name RETURNING subscription_type_id",
            (subscription_type_name,)
        )
        subscription_type_id = self.cursor.fetchone()[0]
        self.subscription_cache[subscription_type_name] = subscription_type_id
        return subscription_type_id
    
    def load_tracks_aggregated(self, filepath='precalc_data/tracks_aggregated.json'):
        """Загрузка агрегированных данных по трекам"""
        print("\n📊 Загрузка tracks_aggregated.json...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = len(data)
        print(f"   Найдено записей: {total}")
        
        for i, item in enumerate(data, 1):
            if i % 100 == 0:
                print(f"   Обработано: {i}/{total} ({i*100//total}%)")
            
            # Создание лейбла, артиста, трека
            label_id = self.get_or_create_label(item['label'])
            artist_id = self.get_or_create_artist(item['artist'], label_id)
            isrc = item.get('isrc', '')  # Получаем ISRC из данных
            track_id = self.get_or_create_track(item['track'], artist_id, label_id, isrc)
            
            # Подсчет платформ и стран
            platforms = item.get('platforms', '').split('|') if item.get('platforms') else []
            countries = item.get('countries', '').split('|') if item.get('countries') else []
            
            # Вставка агрегата трека
            self.cursor.execute("""
                INSERT INTO track_aggregates (track_id, total_revenue, total_streams, avg_rate, platforms_count, countries_count)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (track_id) DO UPDATE SET
                    total_revenue = EXCLUDED.total_revenue,
                    total_streams = EXCLUDED.total_streams,
                    avg_rate = EXCLUDED.avg_rate,
                    platforms_count = EXCLUDED.platforms_count,
                    countries_count = EXCLUDED.countries_count,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                track_id,
                item.get('revenue', 0),
                item.get('streams', 0),
                item.get('avg_rate', 0),
                len(platforms),
                len(countries)
            ))
            
            # Связи трек-платформа
            for platform_name in platforms:
                if platform_name.strip():
                    platform_id = self.get_or_create_platform(platform_name.strip())
                    self.cursor.execute("""
                        INSERT INTO track_platforms (track_id, platform_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (track_id, platform_id))
            
            # Связи трек-страна
            for country_name in countries:
                if country_name.strip():
                    country_id = self.get_or_create_country(country_name.strip())
                    self.cursor.execute("""
                        INSERT INTO track_countries (track_id, country_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (track_id, country_id))
        
        self.conn.commit()
        print(f"✅ Загружено треков: {total}")
    
    def load_artists_aggregated(self, filepath='precalc_data/artists_aggregated.json'):
        """Загрузка агрегированных данных по артистам"""
        print("\n👤 Загрузка artists_aggregated.json...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = len(data)
        print(f"   Найдено записей: {total}")
        
        for i, item in enumerate(data, 1):
            if i % 50 == 0:
                print(f"   Обработано: {i}/{total} ({i*100//total}%)")
            
            label_id = self.get_or_create_label(item['label'])
            artist_id = self.get_or_create_artist(item['artist'], label_id)
            
            platforms = item.get('platforms', '').split('|') if item.get('platforms') else []
            countries = item.get('countries', '').split('|') if item.get('countries') else []
            
            # Вставка агрегата артиста
            self.cursor.execute("""
                INSERT INTO artist_aggregates (artist_id, total_revenue, total_streams, tracks_count, avg_rate, avg_revenue_per_track, platforms_count, countries_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (artist_id) DO UPDATE SET
                    total_revenue = EXCLUDED.total_revenue,
                    total_streams = EXCLUDED.total_streams,
                    tracks_count = EXCLUDED.tracks_count,
                    avg_rate = EXCLUDED.avg_rate,
                    avg_revenue_per_track = EXCLUDED.avg_revenue_per_track,
                    platforms_count = EXCLUDED.platforms_count,
                    countries_count = EXCLUDED.countries_count,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                artist_id,
                item.get('revenue', 0),
                item.get('streams', 0),
                item.get('tracks_count', 0),
                item.get('avg_rate', 0),
                item.get('avg_revenue_per_track', 0),
                len(platforms),
                len(countries)
            ))
            
            # Связи артист-платформа
            for platform_name in platforms:
                if platform_name.strip():
                    platform_id = self.get_or_create_platform(platform_name.strip())
                    self.cursor.execute("""
                        INSERT INTO artist_platforms (artist_id, platform_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (artist_id, platform_id))
            
            # Связи артист-страна
            for country_name in countries:
                if country_name.strip():
                    country_id = self.get_or_create_country(country_name.strip())
                    self.cursor.execute("""
                        INSERT INTO artist_countries (artist_id, country_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (artist_id, country_id))
        
        self.conn.commit()
        print(f"✅ Загружено артистов: {total}")
    
    def load_platforms_aggregated(self, filepath='precalc_data/platforms_aggregated.json'):
        """Загрузка агрегированных данных по платформам"""
        print("\n🎵 Загрузка platforms_aggregated.json...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = len(data)
        print(f"   Найдено записей: {total}")
        
        for item in data:
            platform_id = self.get_or_create_platform(item['platform'])
            
            self.cursor.execute("""
                INSERT INTO platform_aggregates (platform_id, total_revenue, total_streams, tracks_count, artists_count, avg_rate)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (platform_id) DO UPDATE SET
                    total_revenue = EXCLUDED.total_revenue,
                    total_streams = EXCLUDED.total_streams,
                    tracks_count = EXCLUDED.tracks_count,
                    artists_count = EXCLUDED.artists_count,
                    avg_rate = EXCLUDED.avg_rate,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                platform_id,
                item.get('revenue', 0),
                item.get('streams', 0),
                item.get('tracks_count', 0),
                item.get('artists_count', 0),
                item.get('avg_rate', 0)
            ))
        
        self.conn.commit()
        print(f"✅ Загружено платформ: {total}")
    
    def load_monthly_aggregated(self, filepath='precalc_data/monthly_aggregated.json'):
        """Загрузка помесячных данных"""
        print("\n📅 Загрузка monthly_aggregated.json...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = len(data)
        print(f"   Найдено записей: {total}")
        
        for i, item in enumerate(data, 1):
            if i % 500 == 0:
                print(f"   Обработано: {i}/{total} ({i*100//total}%)")
            
            # Парсинг даты
            month_date = datetime.strptime(item['month'], '%Y/%m/%d').date()
            
            # Находим артиста (он уже должен быть создан)
            self.cursor.execute(
                "SELECT artist_id FROM artists WHERE artist_name = %s LIMIT 1",
                (item['artist'],)
            )
            result = self.cursor.fetchone()
            if not result:
                continue
            
            artist_id = result[0]
            
            # Вставка помесячной статистики
            self.cursor.execute("""
                INSERT INTO artist_monthly_stats (artist_id, month_date, streams, revenue)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (artist_id, month_date) DO UPDATE SET
                    streams = EXCLUDED.streams,
                    revenue = EXCLUDED.revenue
            """, (
                artist_id,
                month_date,
                item.get('streams', 0),
                item.get('revenue', 0)
            ))
        
        self.conn.commit()
        print(f"✅ Загружено помесячных записей: {total}")
    
    def load_track_details(self, filepath='precalc_data/track_details.json', limit=None):
        """Загрузка детальных данных по трекам"""
        print("\n🔍 Загрузка track_details.json (детальная статистика)...")
        print("   ⚠️  ВНИМАНИЕ: Этот файл очень большой, загрузка может занять время")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if limit:
            data = data[:limit]
            print(f"   Ограничение: загружаем только первые {limit} записей")
        
        total = len(data)
        print(f"   Найдено записей: {total}")
        
        for i, item in enumerate(data, 1):
            if i % 100 == 0:
                print(f"   Обработано: {i}/{total} ({i*100//total}%)")
            
            # Находим трек
            label_id = self.get_or_create_label(item['label'])
            artist_id = self.get_or_create_artist(item['artist'], label_id)
            isrc = item.get('isrc', '')  # Получаем ISRC из данных
            track_id = self.get_or_create_track(item['track'], artist_id, label_id, isrc)
            
            # Загрузка статистики по платформам
            if 'platforms' in item and isinstance(item['platforms'], dict):
                for platform_name, stats in item['platforms'].items():
                    platform_id = self.get_or_create_platform(platform_name)
                    
                    self.cursor.execute("""
                        INSERT INTO track_platform_stats (track_id, platform_id, streams, revenue)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (track_id, platform_id) DO UPDATE SET
                            streams = EXCLUDED.streams,
                            revenue = EXCLUDED.revenue
                    """, (
                        track_id,
                        platform_id,
                        stats.get('Количество', 0),
                        stats.get('Сумма вознаграждения', 0)
                    ))
            
            # Загрузка статистики по странам
            if 'countries' in item and isinstance(item['countries'], dict):
                for country_name, stats in item['countries'].items():
                    country_id = self.get_or_create_country(country_name)
                    
                    self.cursor.execute("""
                        INSERT INTO track_country_stats (track_id, country_id, streams, revenue)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (track_id, country_id) DO UPDATE SET
                            streams = EXCLUDED.streams,
                            revenue = EXCLUDED.revenue
                    """, (
                        track_id,
                        country_id,
                        stats.get('Количество', 0),
                        stats.get('Сумма вознаграждения', 0)
                    ))
            
            # Загрузка статистики по типам подписок
            if 'subscription_types' in item and isinstance(item['subscription_types'], dict):
                for sub_type_name, streams in item['subscription_types'].items():
                    sub_type_id = self.get_or_create_subscription_type(sub_type_name)
                    
                    self.cursor.execute("""
                        INSERT INTO track_subscription_stats (track_id, subscription_type_id, streams)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (track_id, subscription_type_id) DO UPDATE SET
                            streams = EXCLUDED.streams
                    """, (track_id, sub_type_id, streams))
            
            # Загрузка помесячной статистики
            if 'monthly' in item and isinstance(item['monthly'], dict):
                for month_str, stats in item['monthly'].items():
                    month_date = datetime.strptime(month_str, '%Y/%m/%d').date()
                    
                    self.cursor.execute("""
                        INSERT INTO track_monthly_stats (track_id, month_date, streams, revenue)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (track_id, month_date) DO UPDATE SET
                            streams = EXCLUDED.streams,
                            revenue = EXCLUDED.revenue
                    """, (
                        track_id,
                        month_date,
                        stats.get('Количество', 0),
                        stats.get('Сумма вознаграждения', 0)
                    ))
            
            # Коммит каждые 100 записей
            if i % 100 == 0:
                self.conn.commit()
        
        self.conn.commit()
        print(f"✅ Загружено детальных записей: {total}")
    
    def print_statistics(self):
        """Вывод статистики по загруженным данным"""
        print("\n" + "="*60)
        print("📊 СТАТИСТИКА ЗАГРУЖЕННЫХ ДАННЫХ")
        print("="*60)
        
        tables = [
            ('labels', 'Лейблы'),
            ('artists', 'Артисты'),
            ('tracks', 'Треки'),
            ('platforms', 'Платформы'),
            ('countries', 'Страны'),
            ('subscription_types', 'Типы подписок'),
            ('track_aggregates', 'Агрегаты треков'),
            ('artist_aggregates', 'Агрегаты артистов'),
            ('platform_aggregates', 'Агрегаты платформ'),
            ('track_platform_stats', 'Трек × Платформа'),
            ('track_country_stats', 'Трек × Страна'),
            ('track_subscription_stats', 'Трек × Подписка'),
            ('track_monthly_stats', 'Помесячно (треки)'),
            ('artist_monthly_stats', 'Помесячно (артисты)'),
        ]
        
        for table_name, description in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cursor.fetchone()[0]
            print(f"  {description:.<40} {count:>10,}")
        
        print("="*60)


def main():
    print("="*60)
    print("  🎵 ЗАГРУЗКА ДАННЫХ В БАЗУ ДАННЫХ")
    print("="*60)
    
    loader = DataLoader()
    
    if not loader.connect():
        return
    
    try:
        # Загрузка данных
        loader.load_tracks_aggregated()
        loader.load_artists_aggregated()
        loader.load_platforms_aggregated()
        loader.load_monthly_aggregated()
        
        # Спросить про детальные данные
        print("\n" + "="*60)
        print("⚠️  Файл track_details.json очень большой (989813 строк)")
        print("   Загрузка может занять 30-60 минут")
        choice = input("Загрузить детальные данные? (y/N): ").strip().lower()
        
        if choice == 'y':
            limit_choice = input("Ограничить количество записей? (Enter = все, число = лимит): ").strip()
            limit = int(limit_choice) if limit_choice.isdigit() else None
            loader.load_track_details(limit=limit)
        
        # Статистика
        loader.print_statistics()
        
        print("\n" + "="*60)
        print("✅ ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Ошибка при загрузке данных: {e}")
        import traceback
        traceback.print_exc()
    finally:
        loader.disconnect()


if __name__ == '__main__':
    main()
