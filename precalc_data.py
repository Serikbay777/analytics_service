#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Прекалькуляция данных для AI агента
Создает компактные агрегированные файлы для быстрого доступа
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def extract_main_artist(artist_string):
    """Извлекает основного артиста из строки с фитами"""
    if pd.isna(artist_string):
        return artist_string
    
    artist_str = str(artist_string).strip()
    separators = [' feat. ', ' feat ', ' ft. ', ' ft ', ' featuring ', ', ']
    
    for sep in separators:
        if sep in artist_str.lower():
            pos = artist_str.lower().find(sep)
            return artist_str[:pos].strip()
    
    return artist_str

def precalculate_data():
    """Создает все необходимые агрегированные данные"""
    
    print("=" * 80)
    print("ПРЕКАЛЬКУЛЯЦИЯ ДАННЫХ ДЛЯ AI АГЕНТА")
    print("=" * 80)
    
    # Список CSV файлов
    csv_files = [
        "1740260_704133_2025-07-01_2025-09-01 2.csv",
        "1855874_704133_2025-10-01_2025-12-01 (1).csv"
    ]
    
    # Российские платформы для исключения
    russian_platforms = [
        'Yandex', 'VK', 'Vkontakte', 'UMA (Vkontakte)', 'UMA VK MUSIC',
        'SberZvuk', 'Zvuk', 'HITTER', 'Beeline', 'UMA (Odnoklassniki)',
        'Odnoklassniki', 'UMA Video'
    ]
    
    all_data = []
    
    # Загружаем все файлы
    for csv_file in csv_files:
        file_path = Path(__file__).parent / csv_file
        print(f"\n📂 Загрузка: {csv_file}")
        
        try:
            df = pd.read_csv(
                file_path,
                sep=';',
                encoding='utf-8',
                decimal=',',
                low_memory=False
            )
            
            # Фильтруем российские платформы
            mask = ~df['Платформа'].str.contains('|'.join(russian_platforms), case=False, na=False, regex=True)
            df = df[mask].copy()
            
            # Добавляем основного артиста
            df['Основной артист'] = df['Исполнитель'].apply(extract_main_artist)
            
            all_data.append(df)
            print(f"✓ Загружено {len(df):,} записей")
            
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            continue
    
    # Объединяем все данные
    print(f"\n🔄 Объединение данных...")
    df_all = pd.concat(all_data, ignore_index=True)
    print(f"✓ Всего записей: {len(df_all):,}")
    
    output_dir = Path(__file__).parent / "precalc_data"
    output_dir.mkdir(exist_ok=True)
    
    # ============================================================================
    # 1. АГРЕГАЦИЯ ПО ТРЕКАМ
    # ============================================================================
    print(f"\n📊 1. Агрегация по трекам...")
    
    tracks_agg = df_all.groupby(['Название трека', 'Основной артист', 'Лейбл']).agg({
        'Сумма вознаграждения': 'sum',
        'Количество': 'sum',
        'Платформа': lambda x: '|'.join(sorted(set(x))),
        'страна / регион': lambda x: '|'.join(sorted(set(x)))
    }).reset_index()
    
    tracks_agg.columns = ['track', 'artist', 'label', 'revenue', 'streams', 'platforms', 'countries']
    tracks_agg['avg_rate'] = tracks_agg['revenue'] / tracks_agg['streams']
    tracks_agg = tracks_agg.sort_values('revenue', ascending=False)
    
    tracks_file = output_dir / "tracks_aggregated.json"
    tracks_agg.to_json(tracks_file, orient='records', force_ascii=False, indent=2)
    print(f"✓ Сохранено {len(tracks_agg)} треков → {tracks_file.name}")
    
    # ============================================================================
    # 2. АГРЕГАЦИЯ ПО АРТИСТАМ
    # ============================================================================
    print(f"\n🎤 2. Агрегация по артистам...")
    
    artists_agg = df_all.groupby(['Основной артист', 'Лейбл']).agg({
        'Сумма вознаграждения': 'sum',
        'Количество': 'sum',
        'Название трека': 'nunique',
        'Платформа': lambda x: '|'.join(sorted(set(x))),
        'страна / регион': lambda x: '|'.join(sorted(set(x)))
    }).reset_index()
    
    artists_agg.columns = ['artist', 'label', 'revenue', 'streams', 'tracks_count', 'platforms', 'countries']
    artists_agg['avg_rate'] = artists_agg['revenue'] / artists_agg['streams']
    artists_agg['avg_revenue_per_track'] = artists_agg['revenue'] / artists_agg['tracks_count']
    artists_agg = artists_agg.sort_values('revenue', ascending=False)
    
    artists_file = output_dir / "artists_aggregated.json"
    artists_agg.to_json(artists_file, orient='records', force_ascii=False, indent=2)
    print(f"✓ Сохранено {len(artists_agg)} артистов → {artists_file.name}")
    
    # ============================================================================
    # 3. АГРЕГАЦИЯ ПО ПЛАТФОРМАМ
    # ============================================================================
    print(f"\n📱 3. Агрегация по платформам...")
    
    platforms_agg = df_all.groupby('Платформа').agg({
        'Сумма вознаграждения': 'sum',
        'Количество': 'sum',
        'Название трека': 'nunique',
        'Основной артист': 'nunique'
    }).reset_index()
    
    platforms_agg.columns = ['platform', 'revenue', 'streams', 'tracks_count', 'artists_count']
    platforms_agg['avg_rate'] = platforms_agg['revenue'] / platforms_agg['streams']
    platforms_agg = platforms_agg.sort_values('revenue', ascending=False)
    
    platforms_file = output_dir / "platforms_aggregated.json"
    platforms_agg.to_json(platforms_file, orient='records', force_ascii=False, indent=2)
    print(f"✓ Сохранено {len(platforms_agg)} платформ → {platforms_file.name}")
    
    # ============================================================================
    # 4. АГРЕГАЦИЯ ПО СТРАНАМ
    # ============================================================================
    print(f"\n🌍 4. Агрегация по странам...")
    
    countries_agg = df_all.groupby('страна / регион').agg({
        'Сумма вознаграждения': 'sum',
        'Количество': 'sum',
        'Название трека': 'nunique',
        'Основной артист': 'nunique'
    }).reset_index()
    
    countries_agg.columns = ['country', 'revenue', 'streams', 'tracks_count', 'artists_count']
    countries_agg['avg_rate'] = countries_agg['revenue'] / countries_agg['streams']
    countries_agg = countries_agg.sort_values('revenue', ascending=False)
    
    countries_file = output_dir / "countries_aggregated.json"
    countries_agg.to_json(countries_file, orient='records', force_ascii=False, indent=2)
    print(f"✓ Сохранено {len(countries_agg)} стран → {countries_file.name}")
    
    # ============================================================================
    # 5. ВРЕМЕННАЯ АГРЕГАЦИЯ (по месяцам)
    # ============================================================================
    print(f"\n📅 5. Временная агрегация...")
    
    monthly_agg = df_all.groupby(['Месяц отчета', 'Основной артист']).agg({
        'Сумма вознаграждения': 'sum',
        'Количество': 'sum'
    }).reset_index()
    
    monthly_agg.columns = ['month', 'artist', 'revenue', 'streams']
    monthly_agg = monthly_agg.sort_values(['artist', 'month'])
    
    monthly_file = output_dir / "monthly_aggregated.json"
    monthly_agg.to_json(monthly_file, orient='records', force_ascii=False, indent=2)
    print(f"✓ Сохранено {len(monthly_agg)} записей → {monthly_file.name}")
    
    # ============================================================================
    # 6. ДЕТАЛЬНАЯ СТАТИСТИКА ПО ТРЕКАМ (для поиска)
    # ============================================================================
    print(f"\n🔍 6. Детальная статистика по трекам...")
    
    track_details = []
    grouped = df_all.groupby(['Название трека', 'Основной артист'])
    
    for (track_name, artist_name), group in grouped:
        detail = {
            'track': track_name,
            'artist': artist_name,
            'label': group['Лейбл'].iloc[0],
            'total_revenue': float(group['Сумма вознаграждения'].sum()),
            'total_streams': int(group['Количество'].sum()),
            'avg_rate': float(group['Сумма вознаграждения'].sum() / group['Количество'].sum()),
            'platforms': group.groupby('Платформа').agg({
                'Количество': 'sum',
                'Сумма вознаграждения': 'sum'
            }).to_dict('index'),
            'countries': group.groupby('страна / регион').agg({
                'Количество': 'sum',
                'Сумма вознаграждения': 'sum'
            }).to_dict('index'),
            'subscription_types': group.groupby('Тип абонемента на стриминг')['Количество'].sum().to_dict(),
            'monthly': group.groupby('Месяц отчета').agg({
                'Количество': 'sum',
                'Сумма вознаграждения': 'sum'
            }).to_dict('index')
        }
        track_details.append(detail)
    
    details_file = output_dir / "track_details.json"
    with open(details_file, 'w', encoding='utf-8') as f:
        json.dump(track_details, f, ensure_ascii=False, indent=2)
    print(f"✓ Сохранено {len(track_details)} детальных записей → {details_file.name}")
    
    # ============================================================================
    # 7. МЕТАДАННЫЕ
    # ============================================================================
    print(f"\n📋 7. Создание метаданных...")
    
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'source_files': csv_files,
        'total_records': len(df_all),
        'date_range': {
            'start': '2025-07-01',
            'end': '2025-12-01'
        },
        'stats': {
            'total_revenue': float(df_all['Сумма вознаграждения'].sum()),
            'total_streams': int(df_all['Количество'].sum()),
            'unique_tracks': int(df_all['Название трека'].nunique()),
            'unique_artists': int(df_all['Основной артист'].nunique()),
            'unique_platforms': int(df_all['Платформа'].nunique()),
            'unique_countries': int(df_all['страна / регион'].nunique())
        },
        'files': {
            'tracks': 'tracks_aggregated.json',
            'artists': 'artists_aggregated.json',
            'platforms': 'platforms_aggregated.json',
            'countries': 'countries_aggregated.json',
            'monthly': 'monthly_aggregated.json',
            'details': 'track_details.json'
        }
    }
    
    metadata_file = output_dir / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✓ Метаданные сохранены → {metadata_file.name}")
    
    # ============================================================================
    # ИТОГОВАЯ СТАТИСТИКА
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ ПРЕКАЛЬКУЛЯЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)
    print(f"\n📊 Общая статистика:")
    print(f"   • Всего записей: {len(df_all):,}")
    print(f"   • Общий доход: €{df_all['Сумма вознаграждения'].sum():,.2f}")
    print(f"   • Всего стримов: {df_all['Количество'].sum():,}")
    print(f"   • Уникальных треков: {df_all['Название трека'].nunique():,}")
    print(f"   • Уникальных артистов: {df_all['Основной артист'].nunique():,}")
    print(f"   • Платформ: {df_all['Платформа'].nunique():,}")
    print(f"   • Стран: {df_all['страна / регион'].nunique():,}")
    
    print(f"\n📁 Созданные файлы в {output_dir}:")
    for file in output_dir.glob("*.json"):
        size_kb = file.stat().st_size / 1024
        print(f"   • {file.name} ({size_kb:.1f} KB)")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    precalculate_data()
