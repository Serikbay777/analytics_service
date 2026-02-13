#!/usr/bin/env python3
"""
Instagram Viral Detector - детектор треков с взрывным ростом на Instagram
Находит треки, которые взрываются на Instagram, но еще не подхвачены другими платформами
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

class InstagramViralDetector:
    def __init__(self, csv_file, min_streams=50000):
        """
        Инициализация детектора
        
        Args:
            csv_file: путь к CSV файлу с данными
            min_streams: минимальное количество стримов для рассмотрения
        """
        self.csv_file = Path(csv_file)
        self.min_streams = min_streams
        
        print(f"🔍 Загрузка данных из {self.csv_file.name}...")
        self.df = pd.read_csv(
            self.csv_file,
            sep=';',
            encoding='utf-8',
            decimal=',',
            thousands=None,
            low_memory=False
        )
        print(f"✓ Загружено {len(self.df):,} записей")
    
    def calculate_platform_distribution(self, track_data):
        """
        Рассчитывает распределение стримов по платформам
        
        Returns:
            dict с процентами по платформам
        """
        total_streams = track_data['Количество'].sum()
        
        if total_streams == 0:
            return None
        
        # Instagram/Facebook
        instagram_mask = track_data['Платформа'].str.contains(
            'Facebook|Instagram', case=False, na=False
        )
        instagram_streams = track_data[instagram_mask]['Количество'].sum()
        instagram_pct = (instagram_streams / total_streams) * 100
        
        # Spotify
        spotify_mask = track_data['Платформа'].str.contains(
            'Spotify', case=False, na=False
        )
        spotify_streams = track_data[spotify_mask]['Количество'].sum()
        spotify_pct = (spotify_streams / total_streams) * 100
        
        # YouTube
        youtube_mask = track_data['Платформа'].str.contains(
            'YouTube', case=False, na=False
        )
        youtube_streams = track_data[youtube_mask]['Количество'].sum()
        youtube_pct = (youtube_streams / total_streams) * 100
        
        # Yandex
        yandex_mask = track_data['Платформа'].str.contains(
            'Yandex', case=False, na=False
        )
        yandex_streams = track_data[yandex_mask]['Количество'].sum()
        yandex_pct = (yandex_streams / total_streams) * 100
        
        # TikTok
        tiktok_mask = track_data['Платформа'].str.contains(
            'TikTok', case=False, na=False
        )
        tiktok_streams = track_data[tiktok_mask]['Количество'].sum()
        tiktok_pct = (tiktok_streams / total_streams) * 100
        
        # Apple Music
        apple_mask = track_data['Платформа'].str.contains(
            'Apple Music', case=False, na=False
        )
        apple_streams = track_data[apple_mask]['Количество'].sum()
        apple_pct = (apple_streams / total_streams) * 100
        
        return {
            'instagram_pct': instagram_pct,
            'instagram_streams': instagram_streams,
            'spotify_pct': spotify_pct,
            'spotify_streams': spotify_streams,
            'youtube_pct': youtube_pct,
            'youtube_streams': youtube_streams,
            'yandex_pct': yandex_pct,
            'yandex_streams': yandex_streams,
            'tiktok_pct': tiktok_pct,
            'tiktok_streams': tiktok_streams,
            'apple_pct': apple_pct,
            'apple_streams': apple_streams,
            'total_streams': total_streams
        }
    
    def calculate_instagram_growth(self, track_data):
        """
        Рассчитывает рост Instagram стримов по месяцам
        
        Returns:
            dict с метриками роста Instagram
        """
        # Фильтруем только Instagram
        instagram_data = track_data[
            track_data['Платформа'].str.contains('Facebook|Instagram', case=False, na=False)
        ]
        
        if len(instagram_data) == 0:
            return None
        
        # Группируем по месяцам
        monthly = instagram_data.groupby('Месяц продажи').agg({
            'Количество': 'sum'
        }).sort_index()
        
        if len(monthly) < 2:
            return None
        
        months = list(monthly.index)
        streams = list(monthly['Количество'])
        
        # Максимальный месячный рост Instagram
        max_growth_pct = 0
        max_growth_abs = 0
        max_growth_month = None
        prev_month = None
        
        for i in range(1, len(streams)):
            if streams[i-1] > 0:
                growth_pct = ((streams[i] - streams[i-1]) / streams[i-1]) * 100
                growth_abs = streams[i] - streams[i-1]
                
                if growth_pct > max_growth_pct:
                    max_growth_pct = growth_pct
                    max_growth_abs = growth_abs
                    max_growth_month = months[i]
                    prev_month = months[i-1]
        
        # Текущий тренд Instagram
        current_trend = "стабильно"
        if len(streams) >= 2:
            if streams[-1] > streams[-2] * 1.5:
                current_trend = "🚀 взрывной рост"
            elif streams[-1] > streams[-2] * 1.2:
                current_trend = "📈 рост"
            elif streams[-1] < streams[-2] * 0.5:
                current_trend = "📉 падение"
            elif streams[-1] < streams[-2] * 0.8:
                current_trend = "↘️ спад"
        
        return {
            'instagram_growth_pct': max_growth_pct,
            'instagram_growth_abs': max_growth_abs,
            'instagram_growth_month': max_growth_month,
            'instagram_prev_month': prev_month,
            'instagram_trend': current_trend,
            'instagram_latest_month': months[-1],
            'instagram_latest_streams': streams[-1],
            'instagram_monthly_data': dict(zip(months, streams))
        }
    
    def detect_instagram_viral_tracks(self, 
                                     min_instagram_pct=70,
                                     max_spotify_pct=10,
                                     min_growth_pct=100,
                                     top_n=50):
        """
        Детектирует треки с Instagram-вирусностью
        
        Args:
            min_instagram_pct: минимальный % Instagram (по умолчанию 70%)
            max_spotify_pct: максимальный % Spotify (по умолчанию 10%)
            min_growth_pct: минимальный рост Instagram (по умолчанию 100%)
            top_n: количество топ треков
        
        Returns:
            DataFrame с Instagram-вирусными треками
        """
        print(f"\n🔍 Поиск Instagram-вирусных треков...")
        print(f"   Критерии:")
        print(f"   • Instagram: >{min_instagram_pct}%")
        print(f"   • Spotify: <{max_spotify_pct}%")
        print(f"   • Рост Instagram: >{min_growth_pct}%")
        print(f"   • Минимум стримов: {self.min_streams:,}")
        
        # Группируем по треку и артисту
        tracks = self.df.groupby(['Название трека', 'Исполнитель']).agg({
            'Количество': 'sum'
        }).reset_index()
        
        # Фильтруем по минимальному количеству стримов
        tracks = tracks[tracks['Количество'] >= self.min_streams]
        
        print(f"✓ Анализируем {len(tracks):,} треков...")
        
        instagram_viral_tracks = []
        
        for _, row in tracks.iterrows():
            track = row['Название трека']
            artist = row['Исполнитель']
            
            track_data = self.df[
                (self.df['Название трека'] == track) &
                (self.df['Исполнитель'] == artist)
            ]
            
            # Рассчитываем распределение по платформам
            platform_dist = self.calculate_platform_distribution(track_data)
            
            if platform_dist is None:
                continue
            
            # Рассчитываем рост Instagram
            instagram_growth = self.calculate_instagram_growth(track_data)
            
            if instagram_growth is None:
                continue
            
            # Проверяем критерии Instagram-вирусности
            is_instagram_viral = (
                platform_dist['instagram_pct'] >= min_instagram_pct and
                platform_dist['spotify_pct'] <= max_spotify_pct and
                instagram_growth['instagram_growth_pct'] >= min_growth_pct
            )
            
            if is_instagram_viral:
                # Рассчитываем "упущенную выгоду" (потенциальный доход если бы на Spotify)
                # Средняя ставка Instagram: €0.000022
                # Средняя ставка Spotify: €0.001000
                instagram_revenue = platform_dist['instagram_streams'] * 0.000022
                potential_spotify_revenue = platform_dist['instagram_streams'] * 0.001000
                missed_revenue = potential_spotify_revenue - instagram_revenue
                
                instagram_viral_tracks.append({
                    'track': track,
                    'artist': artist,
                    'total_streams': platform_dist['total_streams'],
                    'instagram_pct': platform_dist['instagram_pct'],
                    'instagram_streams': platform_dist['instagram_streams'],
                    'spotify_pct': platform_dist['spotify_pct'],
                    'spotify_streams': platform_dist['spotify_streams'],
                    'youtube_pct': platform_dist['youtube_pct'],
                    'yandex_pct': platform_dist['yandex_pct'],
                    'tiktok_pct': platform_dist['tiktok_pct'],
                    'apple_pct': platform_dist['apple_pct'],
                    'instagram_growth_pct': instagram_growth['instagram_growth_pct'],
                    'instagram_growth_abs': instagram_growth['instagram_growth_abs'],
                    'instagram_growth_month': instagram_growth['instagram_growth_month'],
                    'instagram_trend': instagram_growth['instagram_trend'],
                    'instagram_latest_streams': instagram_growth['instagram_latest_streams'],
                    'instagram_revenue': instagram_revenue,
                    'potential_spotify_revenue': potential_spotify_revenue,
                    'missed_revenue': missed_revenue,
                    'opportunity_score': missed_revenue * (platform_dist['instagram_pct'] / 100)
                })
        
        if not instagram_viral_tracks:
            print("❌ Instagram-вирусные треки не найдены")
            return pd.DataFrame()
        
        viral_df = pd.DataFrame(instagram_viral_tracks)
        viral_df = viral_df.sort_values('opportunity_score', ascending=False)
        
        print(f"✓ Обнаружено {len(viral_df):,} Instagram-вирусных треков")
        
        return viral_df.head(top_n)
    
    def generate_alerts(self, viral_df, critical_threshold=90):
        """
        Генерирует алерты для Instagram-вирусных треков
        
        Args:
            viral_df: DataFrame с вирусными треками
            critical_threshold: порог Instagram % для критического алерта
        """
        if len(viral_df) == 0:
            return
        
        print("\n" + "=" * 80)
        print("🚨 АЛЕРТЫ: INSTAGRAM-ВИРУСНЫЕ ТРЕКИ (СРОЧНО КОНВЕРТИРОВАТЬ!)")
        print("=" * 80)
        
        critical_alerts = viral_df[viral_df['instagram_pct'] >= critical_threshold]
        warning_alerts = viral_df[viral_df['instagram_pct'] < critical_threshold]
        
        if len(critical_alerts) > 0:
            print(f"\n🔥 КРИТИЧЕСКИЕ АЛЕРТЫ (Instagram >{critical_threshold}%):")
            print("   Треки ПОЛНОСТЬЮ зависят от Instagram! Другие платформы НЕ подхватили!")
            print("-" * 80)
            
            for idx, row in critical_alerts.head(20).iterrows():
                print(f"\n🚨 {row['track']} - {row['artist']}")
                print(f"   📊 Instagram: {row['instagram_pct']:.1f}% ({int(row['instagram_streams']):,} стримов)")
                print(f"   📈 Рост Instagram: +{row['instagram_growth_pct']:,.0f}% ({row['instagram_growth_month']})")
                print(f"   💫 Тренд: {row['instagram_trend']}")
                print(f"   ❌ Spotify: {row['spotify_pct']:.1f}% ({int(row['spotify_streams']):,} стримов)")
                print(f"   ❌ YouTube: {row['youtube_pct']:.1f}%")
                print(f"   ❌ Yandex: {row['yandex_pct']:.1f}%")
                print(f"   💰 Текущий доход: €{row['instagram_revenue']:.2f}")
                print(f"   💎 Потенциал (если Spotify): €{row['potential_spotify_revenue']:.2f}")
                print(f"   ⚠️  УПУЩЕНО: €{row['missed_revenue']:.2f}")
                print(f"   🎯 ДЕЙСТВИЕ: Срочно направить трафик на Spotify/YouTube!")
        
        if len(warning_alerts) > 0:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ (Instagram 70-{critical_threshold}%):")
            print("   Треки сильно зависят от Instagram, но есть шанс подхватить!")
            print("-" * 80)
            
            for idx, row in warning_alerts.head(10).iterrows():
                print(f"\n⚠️  {row['track']} - {row['artist']}")
                print(f"   📊 Instagram: {row['instagram_pct']:.1f}% | Spotify: {row['spotify_pct']:.1f}%")
                print(f"   📈 Рост: +{row['instagram_growth_pct']:,.0f}%")
                print(f"   💫 Тренд: {row['instagram_trend']}")
                print(f"   ⚠️  Упущено: €{row['missed_revenue']:.2f}")
    
    def print_summary_table(self, viral_df):
        """Выводит сводную таблицу"""
        if len(viral_df) == 0:
            return
        
        print("\n" + "=" * 80)
        print("📋 INSTAGRAM-ВИРУСНЫЕ ТРЕКИ (ПРИОРИТЕТ КОНВЕРТАЦИИ)")
        print("=" * 80)
        
        print(f"\n{'№':<3s} {'Трек':<25s} {'Артист':<20s} {'IG%':>6s} {'Spot%':>7s} {'Рост':>10s} {'Упущено':>12s}")
        print("-" * 95)
        
        for idx, (i, row) in enumerate(viral_df.iterrows(), 1):
            track_short = row['track'][:23] + '..' if len(row['track']) > 25 else row['track']
            artist_short = row['artist'][:18] + '..' if len(row['artist']) > 20 else row['artist']
            
            print(f"{idx:<3d} {track_short:<25s} {artist_short:<20s} "
                  f"{row['instagram_pct']:>5.1f}% {row['spotify_pct']:>6.1f}% "
                  f"{row['instagram_growth_pct']:>9,.0f}% €{row['missed_revenue']:>10,.0f}")
        
        print("\n💡 Приоритет = чем выше 'Упущено', тем срочнее нужно действовать!")
    
    def export_report(self, viral_df, output_file='instagram_viral_tracks.json'):
        """Экспортирует отчет в JSON"""
        if len(viral_df) == 0:
            return
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'source_file': str(self.csv_file.name),
            'total_tracks': len(viral_df),
            'total_missed_revenue': float(viral_df['missed_revenue'].sum()),
            'tracks': []
        }
        
        for _, row in viral_df.iterrows():
            report['tracks'].append({
                'track': row['track'],
                'artist': row['artist'],
                'total_streams': int(row['total_streams']),
                'instagram_pct': float(row['instagram_pct']),
                'instagram_streams': int(row['instagram_streams']),
                'spotify_pct': float(row['spotify_pct']),
                'spotify_streams': int(row['spotify_streams']),
                'youtube_pct': float(row['youtube_pct']),
                'yandex_pct': float(row['yandex_pct']),
                'instagram_growth_pct': float(row['instagram_growth_pct']),
                'instagram_growth_month': row['instagram_growth_month'],
                'instagram_trend': row['instagram_trend'],
                'instagram_revenue': float(row['instagram_revenue']),
                'potential_spotify_revenue': float(row['potential_spotify_revenue']),
                'missed_revenue': float(row['missed_revenue']),
                'action': 'СРОЧНО направить трафик на Spotify/YouTube/Yandex'
            })
        
        output_path = Path(__file__).parent / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Отчет сохранен: {output_file}")


def main():
    """Основная функция"""
    print("=" * 80)
    print("🎯 INSTAGRAM VIRAL DETECTOR - Детектор Instagram-вирусных треков")
    print("=" * 80)
    
    # Путь к файлу
    csv_file = Path(__file__).parent / "1855874_704133_2025-10-01_2025-12-01 (1).csv"
    
    if not csv_file.exists():
        print(f"❌ Файл не найден: {csv_file}")
        return
    
    # Создаем детектор
    detector = InstagramViralDetector(
        csv_file=csv_file,
        min_streams=100000  # минимум 100K стримов
    )
    
    # Детектируем Instagram-вирусные треки
    viral_tracks = detector.detect_instagram_viral_tracks(
        min_instagram_pct=70,    # минимум 70% Instagram
        max_spotify_pct=10,      # максимум 10% Spotify
        min_growth_pct=100,      # минимум 100% рост Instagram
        top_n=50
    )
    
    if len(viral_tracks) > 0:
        # Выводим сводную таблицу
        detector.print_summary_table(viral_tracks)
        
        # Генерируем алерты
        detector.generate_alerts(viral_tracks, critical_threshold=90)
        
        # Экспортируем отчет
        detector.export_report(viral_tracks, 'instagram_viral_q4_2025.json')
        
        # Статистика
        total_missed = viral_tracks['missed_revenue'].sum()
        print("\n" + "=" * 80)
        print("💰 ОБЩАЯ СТАТИСТИКА")
        print("=" * 80)
        print(f"Треков обнаружено: {len(viral_tracks)}")
        print(f"Общий упущенный доход: €{total_missed:,.2f}")
        print(f"Средний упущенный доход на трек: €{total_missed/len(viral_tracks):,.2f}")
        print(f"\n💡 Если конвертировать хотя бы 10% Instagram трафика на Spotify,")
        print(f"   дополнительный доход составит: €{total_missed * 0.1:,.2f}")
        
        print("\n" + "=" * 80)
        print("✅ АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 80)
    else:
        print("\n❌ Instagram-вирусные треки не обнаружены")


if __name__ == '__main__':
    main()
