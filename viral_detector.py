#!/usr/bin/env python3
"""
Viral Track Detector - детектор вирусных треков
Анализирует рост стримов на Instagram/TikTok и отправляет алерты
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

class ViralDetector:
    def __init__(self, csv_file, viral_platforms=None, min_streams=10000):
        """
        Инициализация детектора
        
        Args:
            csv_file: путь к CSV файлу с данными
            viral_platforms: список платформ для отслеживания (по умолчанию Instagram/TikTok)
            min_streams: минимальное количество стримов для рассмотрения
        """
        self.csv_file = Path(csv_file)
        self.min_streams = min_streams
        
        if viral_platforms is None:
            self.viral_platforms = [
                'Facebook / Instagram',
                'Instagram',
                'TikTok',
                'TikTok Music'
            ]
        else:
            self.viral_platforms = viral_platforms
        
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
    
    def filter_viral_platforms(self):
        """Фильтрует данные только по вирусным платформам"""
        mask = self.df['Платформа'].str.contains(
            '|'.join(self.viral_platforms),
            case=False,
            na=False
        )
        return self.df[mask].copy()
    
    def calculate_growth(self, track_data):
        """
        Рассчитывает показатели роста для трека
        
        Returns:
            dict с метриками роста
        """
        monthly = track_data.groupby('Месяц продажи').agg({
            'Количество': 'sum'
        }).sort_index()
        
        if len(monthly) < 2:
            return None
        
        months = list(monthly.index)
        streams = list(monthly['Количество'])
        
        # Максимальный месячный рост
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
        
        # Общий рост (первый vs последний)
        total_growth_pct = 0
        if streams[0] > 0:
            total_growth_pct = ((streams[-1] - streams[0]) / streams[0]) * 100
        
        # Коэффициент вирусности (пик / средний)
        peak_streams = max(streams)
        avg_streams = np.mean(streams)
        virality_coef = peak_streams / avg_streams if avg_streams > 0 else 0
        
        # Текущий тренд (последние 2 месяца)
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
            'max_growth_pct': max_growth_pct,
            'max_growth_abs': max_growth_abs,
            'max_growth_month': max_growth_month,
            'prev_month': prev_month,
            'total_growth_pct': total_growth_pct,
            'virality_coef': virality_coef,
            'peak_streams': peak_streams,
            'avg_streams': avg_streams,
            'total_streams': sum(streams),
            'months_count': len(streams),
            'current_trend': current_trend,
            'latest_month': months[-1],
            'latest_streams': streams[-1],
            'monthly_data': dict(zip(months, streams))
        }
    
    def detect_viral_tracks(self, 
                           min_growth_pct=100,
                           min_virality_coef=3.0,
                           top_n=50):
        """
        Детектирует вирусные треки
        
        Args:
            min_growth_pct: минимальный процент роста для алерта (по умолчанию 100%)
            min_virality_coef: минимальный коэффициент вирусности (по умолчанию 3.0)
            top_n: количество топ треков для вывода
        
        Returns:
            DataFrame с вирусными треками
        """
        print(f"\n🔍 Анализ вирусности...")
        print(f"   Платформы: {', '.join(self.viral_platforms)}")
        print(f"   Минимальный рост: {min_growth_pct}%")
        print(f"   Минимальный коэфф вирусности: {min_virality_coef}x")
        
        viral_data = self.filter_viral_platforms()
        
        # Группируем по треку и артисту
        tracks = viral_data.groupby(['Название трека', 'Исполнитель']).agg({
            'Количество': 'sum'
        }).reset_index()
        
        # Фильтруем по минимальному количеству стримов
        tracks = tracks[tracks['Количество'] >= self.min_streams]
        
        print(f"✓ Найдено {len(tracks):,} треков с >{self.min_streams:,} стримов")
        
        # Анализируем рост для каждого трека
        viral_tracks = []
        
        for _, row in tracks.iterrows():
            track = row['Название трека']
            artist = row['Исполнитель']
            
            track_data = viral_data[
                (viral_data['Название трека'] == track) &
                (viral_data['Исполнитель'] == artist)
            ]
            
            growth_metrics = self.calculate_growth(track_data)
            
            if growth_metrics is None:
                continue
            
            # Проверяем критерии вирусности
            is_viral = (
                growth_metrics['max_growth_pct'] >= min_growth_pct or
                growth_metrics['virality_coef'] >= min_virality_coef
            )
            
            if is_viral:
                viral_tracks.append({
                    'track': track,
                    'artist': artist,
                    'total_streams': growth_metrics['total_streams'],
                    'max_growth_pct': growth_metrics['max_growth_pct'],
                    'max_growth_abs': growth_metrics['max_growth_abs'],
                    'max_growth_month': growth_metrics['max_growth_month'],
                    'prev_month': growth_metrics['prev_month'],
                    'virality_coef': growth_metrics['virality_coef'],
                    'peak_streams': growth_metrics['peak_streams'],
                    'current_trend': growth_metrics['current_trend'],
                    'latest_month': growth_metrics['latest_month'],
                    'latest_streams': growth_metrics['latest_streams'],
                    'months_active': growth_metrics['months_count'],
                    'monthly_data': growth_metrics['monthly_data']
                })
        
        if not viral_tracks:
            print("❌ Вирусные треки не найдены")
            return pd.DataFrame()
        
        viral_df = pd.DataFrame(viral_tracks)
        viral_df = viral_df.sort_values('max_growth_pct', ascending=False)
        
        print(f"✓ Обнаружено {len(viral_df):,} вирусных треков")
        
        return viral_df.head(top_n)
    
    def generate_alerts(self, viral_df, alert_threshold=500):
        """
        Генерирует алерты для вирусных треков
        
        Args:
            viral_df: DataFrame с вирусными треками
            alert_threshold: порог роста для критического алерта (%)
        """
        if len(viral_df) == 0:
            return
        
        print("\n" + "=" * 80)
        print("🚨 АЛЕРТЫ: ВИРУСНЫЕ ТРЕКИ ОБНАРУЖЕНЫ!")
        print("=" * 80)
        
        critical_alerts = viral_df[viral_df['max_growth_pct'] >= alert_threshold]
        warning_alerts = viral_df[viral_df['max_growth_pct'] < alert_threshold]
        
        if len(critical_alerts) > 0:
            print(f"\n🔥 КРИТИЧЕСКИЕ АЛЕРТЫ (рост >{alert_threshold}%):")
            print("-" * 80)
            
            for idx, row in critical_alerts.iterrows():
                print(f"\n🚨 {row['track']} - {row['artist']}")
                print(f"   📊 Рост: +{row['max_growth_pct']:,.0f}% ({row['prev_month']} → {row['max_growth_month']})")
                print(f"   📈 Абсолютный рост: +{int(row['max_growth_abs']):,} стримов")
                print(f"   🔥 Коэфф вирусности: {row['virality_coef']:.1f}x")
                print(f"   💫 Текущий тренд: {row['current_trend']}")
                print(f"   📍 Последний месяц: {row['latest_month']} ({int(row['latest_streams']):,} стримов)")
                print(f"   ⏱️  Активен: {row['months_active']} месяцев")
        
        if len(warning_alerts) > 0:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ (рост 100-{alert_threshold}%):")
            print("-" * 80)
            
            for idx, row in warning_alerts.head(10).iterrows():
                print(f"\n⚠️  {row['track']} - {row['artist']}")
                print(f"   📊 Рост: +{row['max_growth_pct']:,.0f}%")
                print(f"   🔥 Коэфф вирусности: {row['virality_coef']:.1f}x")
                print(f"   💫 Тренд: {row['current_trend']}")
    
    def export_report(self, viral_df, output_file='viral_tracks_report.json'):
        """Экспортирует отчет в JSON"""
        if len(viral_df) == 0:
            return
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'source_file': str(self.csv_file.name),
            'total_viral_tracks': len(viral_df),
            'tracks': []
        }
        
        for _, row in viral_df.iterrows():
            report['tracks'].append({
                'track': row['track'],
                'artist': row['artist'],
                'total_streams': int(row['total_streams']),
                'max_growth_pct': float(row['max_growth_pct']),
                'max_growth_abs': int(row['max_growth_abs']),
                'max_growth_month': row['max_growth_month'],
                'virality_coef': float(row['virality_coef']),
                'peak_streams': int(row['peak_streams']),
                'current_trend': row['current_trend'],
                'latest_month': row['latest_month'],
                'latest_streams': int(row['latest_streams']),
                'monthly_data': {k: int(v) for k, v in row['monthly_data'].items()}
            })
        
        output_path = Path(__file__).parent / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Отчет сохранен: {output_file}")
    
    def print_summary_table(self, viral_df):
        """Выводит сводную таблицу вирусных треков"""
        if len(viral_df) == 0:
            return
        
        print("\n" + "=" * 80)
        print("📋 СВОДНАЯ ТАБЛИЦА ВИРУСНЫХ ТРЕКОВ")
        print("=" * 80)
        
        print(f"\n{'№':<3s} {'Трек':<30s} {'Артист':<20s} {'Рост %':>10s} {'Коэфф':>8s} {'Тренд':<15s}")
        print("-" * 95)
        
        for idx, row in viral_df.iterrows():
            track_short = row['track'][:28] + '..' if len(row['track']) > 30 else row['track']
            artist_short = row['artist'][:18] + '..' if len(row['artist']) > 20 else row['artist']
            
            print(f"{idx+1:<3d} {track_short:<30s} {artist_short:<20s} "
                  f"{row['max_growth_pct']:>9,.0f}% {row['virality_coef']:>7.1f}x {row['current_trend']:<15s}")


def main():
    """Основная функция"""
    print("=" * 80)
    print("🎯 VIRAL TRACK DETECTOR - Детектор вирусных треков")
    print("=" * 80)
    
    # Путь к файлу
    csv_file = Path(__file__).parent / "1855874_704133_2025-10-01_2025-12-01 (1).csv"
    
    if not csv_file.exists():
        print(f"❌ Файл не найден: {csv_file}")
        return
    
    # Создаем детектор
    detector = ViralDetector(
        csv_file=csv_file,
        min_streams=50000  # минимум 50K стримов для рассмотрения
    )
    
    # Детектируем вирусные треки
    viral_tracks = detector.detect_viral_tracks(
        min_growth_pct=100,      # минимум 100% рост
        min_virality_coef=3.0,   # минимум 3x коэффициент
        top_n=50                 # топ 50 треков
    )
    
    if len(viral_tracks) > 0:
        # Выводим сводную таблицу
        detector.print_summary_table(viral_tracks)
        
        # Генерируем алерты
        detector.generate_alerts(viral_tracks, alert_threshold=500)
        
        # Экспортируем отчет
        detector.export_report(viral_tracks, 'viral_tracks_q4_2025.json')
        
        print("\n" + "=" * 80)
        print("✅ АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 80)
    else:
        print("\n❌ Вирусные треки не обнаружены")


if __name__ == '__main__':
    main()
