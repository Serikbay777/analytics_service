#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Инструменты (Tools) для AI агента аналитики
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

class AnalyticsTools:
    """Набор инструментов для анализа музыкальных данных"""
    
    def __init__(self, data_dir: str = "precalc_data"):
        # Если путь относительный, делаем его относительно этого файла
        if not Path(data_dir).is_absolute():
            self.data_dir = Path(__file__).parent / data_dir
        else:
            self.data_dir = Path(data_dir)
        self._load_data()
    
    def _load_data(self):
        """Загружает все прекалькулированные данные"""
        with open(self.data_dir / "metadata.json", 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        with open(self.data_dir / "tracks_aggregated.json", 'r', encoding='utf-8') as f:
            self.tracks = json.load(f)
        
        with open(self.data_dir / "artists_aggregated.json", 'r', encoding='utf-8') as f:
            self.artists = json.load(f)
        
        with open(self.data_dir / "platforms_aggregated.json", 'r', encoding='utf-8') as f:
            self.platforms = json.load(f)
        
        with open(self.data_dir / "countries_aggregated.json", 'r', encoding='utf-8') as f:
            self.countries = json.load(f)
        
        with open(self.data_dir / "monthly_aggregated.json", 'r', encoding='utf-8') as f:
            self.monthly = json.load(f)
        
        with open(self.data_dir / "track_details.json", 'r', encoding='utf-8') as f:
            self.track_details = json.load(f)
    
    def get_top_tracks(self, limit: int = 10, sort_by: str = "revenue") -> List[Dict]:
        """
        Получить топ треков
        
        Args:
            limit: количество треков
            sort_by: поле для сортировки (revenue, streams, avg_rate)
        
        Returns:
            Список треков с информацией
        """
        sorted_tracks = sorted(self.tracks, key=lambda x: x.get(sort_by, 0), reverse=True)
        return sorted_tracks[:limit]
    
    def get_top_artists(self, limit: int = 10, sort_by: str = "revenue") -> List[Dict]:
        """
        Получить топ артистов
        
        Args:
            limit: количество артистов
            sort_by: поле для сортировки (revenue, streams, tracks_count, avg_rate)
        
        Returns:
            Список артистов с информацией
        """
        sorted_artists = sorted(self.artists, key=lambda x: x.get(sort_by, 0), reverse=True)
        return sorted_artists[:limit]
    
    def search_track(self, query: str) -> List[Dict]:
        """
        Поиск трека по названию
        
        Args:
            query: поисковый запрос
        
        Returns:
            Список найденных треков
        """
        query_lower = query.lower()
        results = [
            track for track in self.tracks
            if query_lower in track['track'].lower()
        ]
        return results
    
    def search_artist(self, query: str) -> List[Dict]:
        """
        Поиск артиста по имени
        
        Args:
            query: поисковый запрос
        
        Returns:
            Список найденных артистов
        """
        query_lower = query.lower()
        results = [
            artist for artist in self.artists
            if query_lower in artist['artist'].lower()
        ]
        return results
    
    def get_track_details(self, track_name: str, artist_name: Optional[str] = None) -> Optional[Dict]:
        """
        Получить детальную информацию о треке
        
        Args:
            track_name: название трека
            artist_name: имя артиста (опционально)
        
        Returns:
            Детальная информация о треке
        """
        track_lower = track_name.lower()
        
        for detail in self.track_details:
            if track_lower in detail['track'].lower():
                if artist_name is None or artist_name.lower() in detail['artist'].lower():
                    return detail
        
        return None
    
    def get_artist_tracks(self, artist_name: str) -> List[Dict]:
        """
        Получить все треки артиста
        
        Args:
            artist_name: имя артиста
        
        Returns:
            Список треков артиста
        """
        artist_lower = artist_name.lower()
        results = [
            track for track in self.tracks
            if artist_lower in track['artist'].lower()
        ]
        return sorted(results, key=lambda x: x['revenue'], reverse=True)
    
    def get_platform_stats(self, platform_name: Optional[str] = None) -> Dict:
        """
        Получить статистику по платформе(ам)
        
        Args:
            platform_name: название платформы (если None, вернет все)
        
        Returns:
            Статистика по платформе(ам)
        """
        if platform_name is None:
            return {
                'total_platforms': len(self.platforms),
                'platforms': sorted(self.platforms, key=lambda x: x['revenue'], reverse=True)
            }
        
        platform_lower = platform_name.lower()
        for platform in self.platforms:
            if platform_lower in platform['platform'].lower():
                return platform
        
        return {}
    
    def get_country_stats(self, country_name: Optional[str] = None) -> Dict:
        """
        Получить статистику по стране(ам)
        
        Args:
            country_name: название страны (если None, вернет топ)
        
        Returns:
            Статистика по стране(ам)
        """
        if country_name is None:
            return {
                'total_countries': len(self.countries),
                'top_countries': sorted(self.countries, key=lambda x: x['revenue'], reverse=True)[:20]
            }
        
        country_lower = country_name.lower()
        for country in self.countries:
            if country_lower in country['country'].lower():
                return country
        
        return {}
    
    def get_artist_timeline(self, artist_name: str) -> List[Dict]:
        """
        Получить временную динамику артиста
        
        Args:
            artist_name: имя артиста
        
        Returns:
            Список месячных данных
        """
        artist_lower = artist_name.lower()
        results = [
            entry for entry in self.monthly
            if artist_lower in entry['artist'].lower()
        ]
        return sorted(results, key=lambda x: x['month'])
    
    def compare_artists(self, artist1: str, artist2: str) -> Dict:
        """
        Сравнить двух артистов
        
        Args:
            artist1: имя первого артиста
            artist2: имя второго артиста
        
        Returns:
            Сравнительная статистика
        """
        artist1_data = None
        artist2_data = None
        
        for artist in self.artists:
            if artist1.lower() in artist['artist'].lower():
                artist1_data = artist
            if artist2.lower() in artist['artist'].lower():
                artist2_data = artist
        
        if not artist1_data or not artist2_data:
            return {'error': 'Один или оба артиста не найдены'}
        
        return {
            'artist1': artist1_data,
            'artist2': artist2_data,
            'comparison': {
                'revenue_diff': artist1_data['revenue'] - artist2_data['revenue'],
                'streams_diff': artist1_data['streams'] - artist2_data['streams'],
                'tracks_diff': artist1_data['tracks_count'] - artist2_data['tracks_count'],
                'avg_rate_diff': artist1_data['avg_rate'] - artist2_data['avg_rate']
            }
        }
    
    def get_viral_tracks(self, threshold: float = 10.0) -> List[Dict]:
        """
        Найти вирусные треки (с большими колебаниями стримов)
        
        Args:
            threshold: порог вирусности (коэффициент)
        
        Returns:
            Список вирусных треков
        """
        viral_tracks = []
        
        for detail in self.track_details:
            if 'monthly' in detail and len(detail['monthly']) > 1:
                monthly_streams = [
                    data['Количество'] 
                    for data in detail['monthly'].values()
                ]
                
                if len(monthly_streams) > 1:
                    max_streams = max(monthly_streams)
                    avg_streams = sum(monthly_streams) / len(monthly_streams)
                    
                    if avg_streams > 0:
                        virality_coef = max_streams / avg_streams
                        
                        if virality_coef >= threshold:
                            viral_tracks.append({
                                'track': detail['track'],
                                'artist': detail['artist'],
                                'virality_coefficient': virality_coef,
                                'max_streams': max_streams,
                                'avg_streams': avg_streams,
                                'total_revenue': detail['total_revenue']
                            })
        
        return sorted(viral_tracks, key=lambda x: x['virality_coefficient'], reverse=True)
    
    def get_summary_stats(self) -> Dict:
        """
        Получить общую статистику
        
        Returns:
            Общая статистика по всем данным
        """
        return {
            'metadata': self.metadata,
            'top_5_tracks': self.get_top_tracks(5),
            'top_5_artists': self.get_top_artists(5),
            'top_5_platforms': sorted(self.platforms, key=lambda x: x['revenue'], reverse=True)[:5],
            'top_5_countries': sorted(self.countries, key=lambda x: x['revenue'], reverse=True)[:5]
        }
    
    def analyze_monetization(self, artist_name: Optional[str] = None) -> Dict:
        """
        Анализ монетизации
        
        Args:
            artist_name: имя артиста (если None, общая статистика)
        
        Returns:
            Анализ монетизации
        """
        if artist_name:
            tracks = self.get_artist_tracks(artist_name)
            if not tracks:
                return {'error': 'Артист не найден'}
            
            total_revenue = sum(t['revenue'] for t in tracks)
            total_streams = sum(t['streams'] for t in tracks)
            avg_rate = total_revenue / total_streams if total_streams > 0 else 0
            
            return {
                'artist': artist_name,
                'total_revenue': total_revenue,
                'total_streams': total_streams,
                'avg_rate_per_stream': avg_rate,
                'tracks_count': len(tracks),
                'avg_revenue_per_track': total_revenue / len(tracks) if tracks else 0,
                'best_track': tracks[0] if tracks else None,
                'worst_track': tracks[-1] if tracks else None
            }
        else:
            total_revenue = self.metadata['stats']['total_revenue']
            total_streams = self.metadata['stats']['total_streams']
            
            return {
                'total_revenue': total_revenue,
                'total_streams': total_streams,
                'avg_rate_per_stream': total_revenue / total_streams if total_streams > 0 else 0,
                'unique_tracks': self.metadata['stats']['unique_tracks'],
                'unique_artists': self.metadata['stats']['unique_artists']
            }


# Функции-обертки для LangGraph tools
def get_top_tracks_tool(limit: int = 10, sort_by: str = "revenue") -> str:
    """Получить топ треков по доходу или стримам"""
    tools = AnalyticsTools()
    result = tools.get_top_tracks(limit, sort_by)
    return json.dumps(result, ensure_ascii=False, indent=2)

def get_top_artists_tool(limit: int = 10, sort_by: str = "revenue") -> str:
    """Получить топ артистов по доходу или стримам"""
    tools = AnalyticsTools()
    result = tools.get_top_artists(limit, sort_by)
    return json.dumps(result, ensure_ascii=False, indent=2)

def search_track_tool(query: str) -> str:
    """Поиск трека по названию"""
    tools = AnalyticsTools()
    result = tools.search_track(query)
    return json.dumps(result, ensure_ascii=False, indent=2)

def search_artist_tool(query: str) -> str:
    """Поиск артиста по имени"""
    tools = AnalyticsTools()
    result = tools.search_artist(query)
    return json.dumps(result, ensure_ascii=False, indent=2)

def get_track_details_tool(track_name: str, artist_name: str = "") -> str:
    """Получить детальную информацию о треке"""
    tools = AnalyticsTools()
    result = tools.get_track_details(track_name, artist_name if artist_name else None)
    return json.dumps(result, ensure_ascii=False, indent=2)

def get_artist_tracks_tool(artist_name: str) -> str:
    """Получить все треки артиста"""
    tools = AnalyticsTools()
    result = tools.get_artist_tracks(artist_name)
    return json.dumps(result, ensure_ascii=False, indent=2)

def get_platform_stats_tool(platform_name: str = "") -> str:
    """Получить статистику по платформе"""
    tools = AnalyticsTools()
    result = tools.get_platform_stats(platform_name if platform_name else None)
    return json.dumps(result, ensure_ascii=False, indent=2)

def get_country_stats_tool(country_name: str = "") -> str:
    """Получить статистику по стране"""
    tools = AnalyticsTools()
    result = tools.get_country_stats(country_name if country_name else None)
    return json.dumps(result, ensure_ascii=False, indent=2)

def get_artist_timeline_tool(artist_name: str) -> str:
    """Получить временную динамику артиста по месяцам"""
    tools = AnalyticsTools()
    result = tools.get_artist_timeline(artist_name)
    return json.dumps(result, ensure_ascii=False, indent=2)

def compare_artists_tool(artist1: str, artist2: str) -> str:
    """Сравнить двух артистов"""
    tools = AnalyticsTools()
    result = tools.compare_artists(artist1, artist2)
    return json.dumps(result, ensure_ascii=False, indent=2)

def get_viral_tracks_tool(threshold: float = 10.0) -> str:
    """Найти вирусные треки с коэффициентом вирусности выше порога"""
    tools = AnalyticsTools()
    result = tools.get_viral_tracks(threshold)
    return json.dumps(result, ensure_ascii=False, indent=2)

def get_summary_stats_tool() -> str:
    """Получить общую статистику по всем данным"""
    tools = AnalyticsTools()
    result = tools.get_summary_stats()
    return json.dumps(result, ensure_ascii=False, indent=2)

def analyze_monetization_tool(artist_name: str = "") -> str:
    """Анализ монетизации артиста или общей статистики"""
    tools = AnalyticsTools()
    result = tools.analyze_monetization(artist_name if artist_name else None)
    return json.dumps(result, ensure_ascii=False, indent=2)
