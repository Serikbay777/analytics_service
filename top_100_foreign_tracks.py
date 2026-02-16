#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для анализа топ 100 треков по доходам с зарубежных платформ
Исключает российские платформы из анализа
"""

import pandas as pd
import sys
from pathlib import Path

def main():
    # Путь к CSV файлу
    csv_file = Path(__file__).parent / "1855874_704133_2025-10-01_2025-12-01 (1).csv"
    
    print("=" * 80)
    print("Анализ топ 100 треков по доходам с зарубежных платформ")
    print("=" * 80)
    print(f"\nЗагрузка данных из: {csv_file.name}")
    
    # Загрузка данных
    try:
        df = pd.read_csv(
            csv_file,
            sep=';',
            encoding='utf-8',
            decimal=',',
            thousands=None
        )
        print(f"✓ Загружено записей: {len(df):,}")
    except Exception as e:
        print(f"✗ Ошибка при загрузке файла: {e}")
        sys.exit(1)
    
    # Список российских и СНГ платформ для исключения
    russian_platforms = [
        'Yandex',
        'VK',
        'Vkontakte',
        'UMA (Vkontakte)',
        'UMA VK MUSIC',
        'SberZvuk',
        'Zvuk',
        'HITTER',
        'Beeline',
        'UMA (Odnoklassniki)',
        'Odnoklassniki',
        'UMA Video'
    ]
    
    print(f"\n📋 Исключаемые российские и СНГ платформы:")
    for platform in russian_platforms:
        count = df[df['Платформа'].str.contains(platform, case=False, na=False)].shape[0]
        if count > 0:
            print(f"   - {platform}: {count:,} записей")
    
    # Фильтрация: исключаем российские и СНГ платформы
    mask = ~df['Платформа'].str.contains('|'.join(russian_platforms), case=False, na=False)
    df_foreign = df[mask].copy()
    
    print(f"\n✓ После исключения российских и СНГ платформ: {len(df_foreign):,} записей")
    print(f"✗ Исключено записей: {len(df) - len(df_foreign):,}")
    
    # Извлечение первого (основного) артиста из строки с фитами
    print("\n🔄 Обработка артистов (извлечение основного артиста из фитов)...")
    
    def extract_main_artist(artist_string):
        """
        Извлекает основного артиста из строки с фитами
        Примеры:
        "Artist1, Artist2" -> "Artist1"
        "Artist1 feat. Artist2" -> "Artist1"
        "Artist1 ft. Artist2" -> "Artist1"
        """
        if pd.isna(artist_string):
            return artist_string
        
        artist_str = str(artist_string).strip()
        
        # Разделители для фитов
        separators = [' feat. ', ' feat ', ' ft. ', ' ft ', ' featuring ', ', ']
        
        for sep in separators:
            if sep in artist_str.lower():
                # Находим позицию разделителя (case-insensitive)
                pos = artist_str.lower().find(sep)
                return artist_str[:pos].strip()
        
        return artist_str
    
    # Создаем новую колонку с основным артистом
    df_foreign['Основной артист'] = df_foreign['Исполнитель'].apply(extract_main_artist)
    
    print(f"✓ Обработано артистов")
    
    # Группировка по треку и ОСНОВНОМУ исполнителю, суммирование доходов
    print("\n🔄 Группировка данных по трекам и основным исполнителям...")
    
    grouped = df_foreign.groupby(
        ['Название трека', 'Основной артист'],
        as_index=False
    ).agg({
        'Сумма вознаграждения': 'sum',
        'Количество': 'sum',
        'Платформа': lambda x: ', '.join(sorted(set(x))),  # Уникальные платформы
        'Исполнитель': 'first'  # Сохраняем полное имя с фитами для справки
    })
    
    # Сортировка по доходам (убывание)
    grouped = grouped.sort_values('Сумма вознаграждения', ascending=False)
    
    # Топ 100
    top_100 = grouped.head(100).copy()
    
    # Добавление номера позиции
    top_100.insert(0, '№', range(1, len(top_100) + 1))
    
    # Переименование колонок для читаемости
    top_100.columns = [
        '№',
        'Трек',
        'Основной артист',
        'Доход (EUR)',
        'Всего стримов',
        'Платформы',
        'Полное имя (с фитами)'
    ]
    
    # Форматирование доходов
    top_100['Доход (EUR)'] = top_100['Доход (EUR)'].round(2)
    
    # Вывод результатов
    print("\n" + "=" * 80)
    print("ТОП 100 ТРЕКОВ ПО ДОХОДАМ С ЗАРУБЕЖНЫХ ПЛАТФОРМ")
    print("=" * 80)
    print()
    
    # Вывод в консоль (первые 20 для предварительного просмотра)
    for idx, row in top_100.head(20).iterrows():
        print(f"{row['№']:3d}. {row['Трек']:<30s} | {row['Основной артист']:<30s} | €{row['Доход (EUR)']:>10.2f} | {int(row['Всего стримов']):>8,} стримов")
    
    if len(top_100) > 20:
        print(f"\n... и еще {len(top_100) - 20} треков\n")
    
    # Сохранение в CSV
    output_csv = Path(__file__).parent / "top_100_foreign_tracks_report.csv"
    top_100.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✓ Полный отчет сохранен в: {output_csv.name}")
    
    # Сохранение в Excel для удобства
    try:
        output_excel = Path(__file__).parent / "top_100_foreign_tracks_report.xlsx"
        
        # Создаем красивый Excel файл
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            top_100.to_excel(writer, sheet_name='Top 100', index=False)
            
            # Получаем рабочий лист для форматирования
            worksheet = writer.sheets['Top 100']
            
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
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Excel отчет сохранен в: {output_excel.name}")
    except ImportError:
        print("⚠ openpyxl не установлен, Excel файл не создан (только CSV)")
    except Exception as e:
        print(f"⚠ Ошибка при создании Excel: {e}")
    
    # Статистика
    print("\n" + "=" * 80)
    print("СТАТИСТИКА")
    print("=" * 80)
    total_revenue = top_100['Доход (EUR)'].sum()
    total_streams = top_100['Всего стримов'].sum()
    avg_revenue = top_100['Доход (EUR)'].mean()
    
    print(f"Общий доход топ-100:     €{total_revenue:,.2f}")
    print(f"Всего стримов топ-100:   {int(total_streams):,}")
    print(f"Средний доход на трек:   €{avg_revenue:,.2f}")
    print(f"Топ-1 трек:              {top_100.iloc[0]['Трек']} - {top_100.iloc[0]['Основной артист']}")
    print(f"Доход топ-1:             €{top_100.iloc[0]['Доход (EUR)']:,.2f}")
    
    # Анализ платформ
    print("\n📊 Уникальные зарубежные платформы в топ-100:")
    all_platforms = set()
    for platforms_str in df_foreign['Платформа'].unique():
        all_platforms.add(platforms_str)
    
    for platform in sorted(all_platforms):
        count = df_foreign[df_foreign['Платформа'] == platform].shape[0]
        revenue = df_foreign[df_foreign['Платформа'] == platform]['Сумма вознаграждения'].sum()
        print(f"   - {platform:<30s}: {count:>8,} записей | €{revenue:>12.2f}")
    
    print("\n" + "=" * 80)
    print("✓ Анализ завершен успешно!")
    print("=" * 80)

if __name__ == "__main__":
    main()
