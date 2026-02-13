#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для извлечения всех уникальных артистов из топ 100 треков
"""

import pandas as pd
import sys
from pathlib import Path

def main():
    # Путь к файлу с топ 100
    top100_file = Path(__file__).parent / "top_100_foreign_tracks_report.csv"
    
    print("=" * 80)
    print("ИЗВЛЕЧЕНИЕ АРТИСТОВ ИЗ ТОП 100 ТРЕКОВ")
    print("=" * 80)
    
    # Загрузка данных топ 100
    try:
        df = pd.read_csv(top100_file, encoding='utf-8')
        print(f"\n✓ Загружено топ {len(df)} треков из: {top100_file.name}")
    except FileNotFoundError:
        print(f"\n✗ Файл не найден: {top100_file.name}")
        print("   Сначала запустите скрипт top_100_foreign_tracks.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка при загрузке файла: {e}")
        sys.exit(1)
    
    # Извлечение всех артистов (используем колонку "Основной артист")
    all_artists = set()
    
    # Проверяем какая колонка есть в файле
    artist_column = 'Основной артист' if 'Основной артист' in df.columns else 'Исполнитель'
    
    for artists_str in df[artist_column]:
        # Добавляем артиста как есть (уже основной)
        all_artists.add(str(artists_str).strip())
    
    # Сортировка артистов по алфавиту
    sorted_artists = sorted(all_artists)
    
    print(f"\n🎤 Всего уникальных артистов: {len(sorted_artists)}")
    print("\n" + "=" * 80)
    print("ПОЛНЫЙ СПИСОК АРТИСТОВ")
    print("=" * 80)
    print()
    
    # Вывод списка артистов с нумерацией
    for idx, artist in enumerate(sorted_artists, 1):
        print(f"{idx:3d}. {artist}")
    
    # Сохранение в текстовый файл
    output_txt = Path(__file__).parent / "top100_artists_list.txt"
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("СПИСОК АРТИСТОВ ИЗ ТОП 100 ТРЕКОВ ПО ДОХОДАМ\n")
        f.write(f"Всего уникальных артистов: {len(sorted_artists)}\n")
        f.write("=" * 80 + "\n\n")
        
        for idx, artist in enumerate(sorted_artists, 1):
            f.write(f"{idx:3d}. {artist}\n")
    
    print(f"\n✓ Список сохранен в: {output_txt.name}")
    
    # Создание DataFrame для удобства
    artists_df = pd.DataFrame({
        '№': range(1, len(sorted_artists) + 1),
        'Артист': sorted_artists
    })
    
    # Добавление статистики по каждому артисту
    artist_stats = []
    
    for artist in sorted_artists:
        # Подсчет треков где артист является основным
        track_count = 0
        total_revenue = 0
        total_streams = 0
        
        for idx, row in df.iterrows():
            if artist == str(row[artist_column]).strip():
                track_count += 1
                total_revenue += row['Доход (EUR)']
                total_streams += row['Всего стримов']
        
        artist_stats.append({
            'Артист': artist,
            'Треков в топ-100': track_count,
            'Общий доход (EUR)': round(total_revenue, 2),
            'Всего стримов': int(total_streams)
        })
    
    # Создание DataFrame со статистикой
    stats_df = pd.DataFrame(artist_stats)
    stats_df = stats_df.sort_values('Общий доход (EUR)', ascending=False)
    stats_df.insert(0, '№', range(1, len(stats_df) + 1))
    
    # Сохранение статистики в CSV
    output_csv = Path(__file__).parent / "top100_artists_stats.csv"
    stats_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✓ Статистика артистов сохранена в: {output_csv.name}")
    
    # Сохранение в Excel
    try:
        output_excel = Path(__file__).parent / "top100_artists_stats.xlsx"
        
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            stats_df.to_excel(writer, sheet_name='Статистика артистов', index=False)
            
            # Форматирование
            worksheet = writer.sheets['Статистика артистов']
            
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Excel отчет сохранен в: {output_excel.name}")
    except Exception as e:
        print(f"⚠ Ошибка при создании Excel: {e}")
    
    # Топ-10 артистов по доходам
    print("\n" + "=" * 80)
    print("ТОП-10 АРТИСТОВ ПО ДОХОДАМ")
    print("=" * 80)
    print()
    
    for idx, row in stats_df.head(10).iterrows():
        print(f"{row['№']:3d}. {row['Артист']:<40s} | {row['Треков в топ-100']:2d} треков | €{row['Общий доход (EUR)']:>10.2f} | {row['Всего стримов']:>12,} стримов")
    
    print("\n" + "=" * 80)
    print("✓ Извлечение завершено успешно!")
    print("=" * 80)

if __name__ == "__main__":
    main()
