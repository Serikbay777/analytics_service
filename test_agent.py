#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки агента (без API ключа)
"""

from analytics_tools import AnalyticsTools
import json

def test_tools():
    """Тестирует все инструменты без LLM"""
    
    print("=" * 80)
    print("🧪 ТЕСТИРОВАНИЕ ИНСТРУМЕНТОВ АГЕНТА")
    print("=" * 80)
    
    tools = AnalyticsTools()
    
    # 1. Топ треки
    print("\n1️⃣  ТОП-5 ТРЕКОВ ПО ДОХОДУ:")
    print("-" * 80)
    top_tracks = tools.get_top_tracks(5)
    for i, track in enumerate(top_tracks, 1):
        print(f"{i}. {track['track']} - {track['artist']}")
        print(f"   Доход: €{track['revenue']:.2f} | Стримы: {track['streams']:,}")
    
    # 2. Топ артисты
    print("\n2️⃣  ТОП-5 АРТИСТОВ ПО ДОХОДУ:")
    print("-" * 80)
    top_artists = tools.get_top_artists(5)
    for i, artist in enumerate(top_artists, 1):
        print(f"{i}. {artist['artist']}")
        print(f"   Доход: €{artist['revenue']:.2f} | Треков: {artist['tracks_count']}")
    
    # 3. Поиск трека
    print("\n3️⃣  ПОИСК ТРЕКА 'Meili':")
    print("-" * 80)
    search_results = tools.search_track("Meili")
    for track in search_results[:3]:
        print(f"• {track['track']} - {track['artist']}")
        print(f"  Доход: €{track['revenue']:.2f} | Стримы: {track['streams']:,}")
    
    # 4. Детали трека
    print("\n4️⃣  ДЕТАЛИ ТРЕКА 'Meili':")
    print("-" * 80)
    details = tools.get_track_details("Meili")
    if details:
        print(f"Трек: {details['track']}")
        print(f"Артист: {details['artist']}")
        print(f"Лейбл: {details['label']}")
        print(f"Доход: €{details['total_revenue']:.2f}")
        print(f"Стримы: {details['total_streams']:,}")
        print(f"Средняя ставка: €{details['avg_rate']:.6f}")
        
        print("\nТоп-3 платформы:")
        platforms = sorted(
            details['platforms'].items(),
            key=lambda x: x[1]['Количество'],
            reverse=True
        )[:3]
        for platform, data in platforms:
            print(f"  • {platform}: {int(data['Количество']):,} стримов")
        
        print("\nТоп-3 страны:")
        countries = sorted(
            details['countries'].items(),
            key=lambda x: x[1]['Количество'],
            reverse=True
        )[:3]
        for country, data in countries:
            print(f"  • {country}: {int(data['Количество']):,} стримов")
    
    # 5. Сравнение артистов
    print("\n5️⃣  СРАВНЕНИЕ: Yenlik vs Shiza:")
    print("-" * 80)
    comparison = tools.compare_artists("Yenlik", "Shiza")
    if 'error' not in comparison:
        a1 = comparison['artist1']
        a2 = comparison['artist2']
        diff = comparison['comparison']
        
        print(f"\n{a1['artist']}:")
        print(f"  Доход: €{a1['revenue']:.2f}")
        print(f"  Стримы: {a1['streams']:,}")
        print(f"  Треков: {a1['tracks_count']}")
        
        print(f"\n{a2['artist']}:")
        print(f"  Доход: €{a2['revenue']:.2f}")
        print(f"  Стримы: {a2['streams']:,}")
        print(f"  Треков: {a2['tracks_count']}")
        
        print(f"\nРазница:")
        print(f"  Доход: €{diff['revenue_diff']:.2f}")
        print(f"  Стримы: {diff['streams_diff']:,}")
        print(f"  Треков: {diff['tracks_diff']}")
    
    # 6. Вирусные треки
    print("\n6️⃣  ВИРУСНЫЕ ТРЕКИ (коэффициент > 10):")
    print("-" * 80)
    viral = tools.get_viral_tracks(10.0)
    for i, track in enumerate(viral[:5], 1):
        print(f"{i}. {track['track']} - {track['artist']}")
        print(f"   Коэффициент вирусности: {track['virality_coefficient']:.1f}x")
        print(f"   Макс стримы: {track['max_streams']:,} | Средние: {int(track['avg_streams']):,}")
    
    # 7. Платформы
    print("\n7️⃣  ТОП-5 ПЛАТФОРМ ПО ДОХОДУ:")
    print("-" * 80)
    platform_stats = tools.get_platform_stats()
    for i, platform in enumerate(platform_stats['platforms'][:5], 1):
        print(f"{i}. {platform['platform']}")
        print(f"   Доход: €{platform['revenue']:.2f} | Стримы: {platform['streams']:,}")
        print(f"   Средняя ставка: €{platform['avg_rate']:.6f}")
    
    # 8. Страны
    print("\n8️⃣  ТОП-5 СТРАН ПО ДОХОДУ:")
    print("-" * 80)
    country_stats = tools.get_country_stats()
    for i, country in enumerate(country_stats['top_countries'][:5], 1):
        print(f"{i}. {country['country']}")
        print(f"   Доход: €{country['revenue']:.2f} | Стримы: {country['streams']:,}")
    
    # 9. Временная динамика
    print("\n9️⃣  ДИНАМИКА АРТИСТА Yenlik ПО МЕСЯЦАМ:")
    print("-" * 80)
    timeline = tools.get_artist_timeline("Yenlik")
    for entry in timeline:
        print(f"{entry['month']}: {entry['streams']:,} стримов, €{entry['revenue']:.2f}")
    
    # 10. Монетизация
    print("\n🔟 АНАЛИЗ МОНЕТИЗАЦИИ - Ernar Amandyq:")
    print("-" * 80)
    monetization = tools.analyze_monetization("Ernar Amandyq")
    if 'error' not in monetization:
        print(f"Артист: {monetization['artist']}")
        print(f"Общий доход: €{monetization['total_revenue']:.2f}")
        print(f"Всего стримов: {monetization['total_streams']:,}")
        print(f"Средняя ставка: €{monetization['avg_rate_per_stream']:.6f}")
        print(f"Треков: {monetization['tracks_count']}")
        print(f"Средний доход на трек: €{monetization['avg_revenue_per_track']:.2f}")
        
        if monetization['best_track']:
            best = monetization['best_track']
            print(f"\nЛучший трек: {best['track']}")
            print(f"  Доход: €{best['revenue']:.2f}")
    
    print("\n" + "=" * 80)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 80)
    print("\n💡 Для запуска AI агента:")
    print("   1. Установите API ключ: export ANTHROPIC_API_KEY='your-key'")
    print("   2. Запустите: python analytics_agent.py")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_tools()
