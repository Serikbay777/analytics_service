#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для полного анализа артистов из топ-100
Берет всех основных артистов из топ-100 и анализирует ВСЕ их треки
"""

import pandas as pd
import sys
from pathlib import Path

def extract_main_artist(artist_string):
    """
    Извлекает основного артиста из строки с фитами
    """
    if pd.isna(artist_string):
        return artist_string
    
    artist_str = str(artist_string).strip()
    
    # Разделители для фитов
    separators = [' feat. ', ' feat ', ' ft. ', ' ft ', ' featuring ', ', ']
    
    for sep in separators:
        if sep in artist_str.lower():
            pos = artist_str.lower().find(sep)
            return artist_str[:pos].strip()
    
    return artist_str

def main():
    # Пути к файлам
    csv_file = Path(__file__).parent / "1855874_704133_2025-10-01_2025-12-01 (1).csv"
    top100_file = Path(__file__).parent / "top100_artists_stats.csv"
    
    print("=" * 80)
    print("ПОЛНЫЙ АНАЛИЗ АРТИСТОВ ИЗ ТОП-100")
    print("=" * 80)
    
    # Загрузка списка артистов из топ-100
    try:
        top100_df = pd.read_csv(top100_file, encoding='utf-8')
        artists_from_top100 = set(top100_df['Артист'].tolist())
        print(f"\n✓ Загружено {len(artists_from_top100)} артистов из топ-100")
    except FileNotFoundError:
        print(f"\n✗ Файл не найден: {top100_file.name}")
        print("   Сначала запустите скрипты top_100_foreign_tracks.py и extract_artists_from_top100.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка при загрузке файла: {e}")
        sys.exit(1)
    
    # Загрузка полного CSV файла
    print(f"\n📂 Загрузка полного CSV файла: {csv_file.name}")
    try:
        df = pd.read_csv(
            csv_file,
            sep=';',
            encoding='utf-8',
            decimal=',',
            thousands=None,
            low_memory=False
        )
        print(f"✓ Загружено записей: {len(df):,}")
    except Exception as e:
        print(f"✗ Ошибка при загрузке файла: {e}")
        sys.exit(1)
    
    # Исключение российских и СНГ платформ
    russian_platforms = [
        'Yandex', 'VK', 'Vkontakte', 'UMA (Vkontakte)', 'UMA VK MUSIC',
        'SberZvuk', 'Zvuk', 'HITTER', 'Beeline', 'UMA (Odnoklassniki)',
        'Odnoklassniki', 'UMA Video'
    ]
    
    print(f"\n🔄 Фильтрация российских и СНГ платформ...")
    mask = ~df['Платформа'].str.contains('|'.join(russian_platforms), case=False, na=False, regex=True)
    df_foreign = df[mask].copy()
    print(f"✓ После фильтрации: {len(df_foreign):,} записей")
    
    # Извлечение основного артиста
    print(f"\n🔄 Извлечение основных артистов...")
    df_foreign['Основной артист'] = df_foreign['Исполнитель'].apply(extract_main_artist)
    
    # Фильтрация только артистов из топ-100
    print(f"\n🔄 Фильтрация треков артистов из топ-100...")
    df_top_artists = df_foreign[df_foreign['Основной артист'].isin(artists_from_top100)].copy()
    print(f"✓ Найдено {len(df_top_artists):,} записей для артистов из топ-100")
    
    # Анализ по каждому артисту
    print(f"\n🔄 Анализ всех треков каждого артиста...")
    
    artist_full_stats = []
    
    for artist in sorted(artists_from_top100):
        # Все записи этого артиста
        artist_data = df_top_artists[df_top_artists['Основной артист'] == artist]
        
        if len(artist_data) == 0:
            continue
        
        # Группировка по трекам
        tracks_grouped = artist_data.groupby('Название трека').agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        # Сортировка треков по доходу
        tracks_grouped = tracks_grouped.sort_values('Сумма вознаграждения', ascending=False)
        
        # Общая статистика по артисту
        total_revenue = artist_data['Сумма вознаграждения'].sum()
        total_streams = artist_data['Количество'].sum()
        total_tracks = len(tracks_grouped)
        
        # Формирование списка треков с доходами
        tracks_list = []
        for idx, row in tracks_grouped.iterrows():
            track_name = row['Название трека']
            track_revenue = row['Сумма вознаграждения']
            track_streams = int(row['Количество'])
            tracks_list.append(f"{track_name} (€{track_revenue:.2f}, {track_streams:,} стримов)")
        
        tracks_string = " | ".join(tracks_list)
        
        artist_full_stats.append({
            'Артист': artist,
            'Всего треков': total_tracks,
            'Общий доход (EUR)': round(total_revenue, 2),
            'Всего стримов': int(total_streams),
            'Средний доход на трек (EUR)': round(total_revenue / total_tracks, 2) if total_tracks > 0 else 0,
            'Все треки (с доходами)': tracks_string
        })
    
    # Создание DataFrame
    stats_df = pd.DataFrame(artist_full_stats)
    stats_df = stats_df.sort_values('Общий доход (EUR)', ascending=False)
    stats_df.insert(0, '№', range(1, len(stats_df) + 1))
    
    # Вывод топ-20 в консоль
    print("\n" + "=" * 80)
    print("ТОП-20 АРТИСТОВ ПО ОБЩЕМУ ДОХОДУ (ВСЕ ТРЕКИ)")
    print("=" * 80)
    print()
    
    for idx, row in stats_df.head(20).iterrows():
        print(f"{row['№']:3d}. {row['Артист']:<30s} | {row['Всего треков']:3d} треков | €{row['Общий доход (EUR)']:>10.2f} | {row['Всего стримов']:>12,} стримов")
    
    if len(stats_df) > 20:
        print(f"\n... и еще {len(stats_df) - 20} артистов\n")
    
    # Сохранение в CSV
    output_csv = Path(__file__).parent / "full_artists_analysis.csv"
    stats_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✓ Полный отчет сохранен в: {output_csv.name}")
    
    # Сохранение в Excel
    try:
        output_excel = Path(__file__).parent / "full_artists_analysis.xlsx"
        
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            stats_df.to_excel(writer, sheet_name='Полный анализ артистов', index=False)
            
            # Форматирование
            worksheet = writer.sheets['Полный анализ артистов']
            
            # Автоподбор ширины колонок
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                # Ограничиваем максимальную ширину для колонки со списком треков
                if column_letter == 'G':  # Колонка "Все треки"
                    adjusted_width = 100
                else:
                    adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Excel отчет сохранен в: {output_excel.name}")
    except Exception as e:
        print(f"⚠ Ошибка при создании Excel: {e}")
    
    # Общая статистика
    print("\n" + "=" * 80)
    print("ОБЩАЯ СТАТИСТИКА")
    print("=" * 80)
    total_revenue_all = stats_df['Общий доход (EUR)'].sum()
    total_streams_all = stats_df['Всего стримов'].sum()
    total_tracks_all = stats_df['Всего треков'].sum()
    avg_revenue_per_artist = stats_df['Общий доход (EUR)'].mean()
    
    print(f"Всего артистов:              {len(stats_df)}")
    print(f"Всего треков:                {total_tracks_all:,}")
    print(f"Общий доход всех артистов:   €{total_revenue_all:,.2f}")
    print(f"Всего стримов:               {total_streams_all:,}")
    print(f"Средний доход на артиста:    €{avg_revenue_per_artist:,.2f}")
    print(f"Топ-1 артист:                {stats_df.iloc[0]['Артист']}")
    print(f"Доход топ-1:                 €{stats_df.iloc[0]['Общий доход (EUR)']:,.2f}")
    print(f"Треков у топ-1:              {stats_df.iloc[0]['Всего треков']}")
    
    print("\n" + "=" * 80)
    print("✓ Анализ завершен успешно!")
    print("=" * 80)

if __name__ == "__main__":
    main()
