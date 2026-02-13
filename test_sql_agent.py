#!/usr/bin/env python3
"""
Тестовый клиент для SQL Agent API
"""

import requests
import json

API_URL = "http://localhost:5001"

def test_query(query: str):
    """Тестирует запрос к API"""
    print(f"\n{'='*60}")
    print(f"📝 Запрос: {query}")
    print('='*60)
    
    try:
        response = requests.post(
            f"{API_URL}/api/query",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n💡 Объяснение: {result.get('explanation', 'N/A')}")
            print(f"\n🔍 SQL запрос:")
            print(result.get('sql', 'N/A'))
            
            if result.get('success'):
                print(f"\n✅ Результат ({result.get('count', 0)} записей):")
                data = result.get('data', [])
                
                if data:
                    # Выводим первые 10 записей
                    for i, row in enumerate(data[:10], 1):
                        print(f"\n  {i}. {json.dumps(row, ensure_ascii=False, indent=4)}")
                    
                    if len(data) > 10:
                        print(f"\n  ... и еще {len(data) - 10} записей")
                else:
                    print("  Нет данных")
            else:
                print(f"\n❌ Ошибка выполнения: {result.get('error')}")
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def test_schema():
    """Получает схему БД"""
    print(f"\n{'='*60}")
    print("📊 Схема базы данных")
    print('='*60)
    
    try:
        response = requests.get(f"{API_URL}/api/schema")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📋 Таблицы ({len(result.get('tables', []))}):")
            for table in result.get('tables', []):
                count = result.get('statistics', {}).get(table, 0)
                print(f"  - {table}: {count:,} записей")
            
            print(f"\n👁️  Представления ({len(result.get('views', []))}):")
            for view in result.get('views', []):
                print(f"  - {view}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def test_examples():
    """Получает примеры запросов"""
    print(f"\n{'='*60}")
    print("💡 Примеры запросов")
    print('='*60)
    
    try:
        response = requests.get(f"{API_URL}/api/examples")
        
        if response.status_code == 200:
            result = response.json()
            
            for i, example in enumerate(result.get('examples', []), 1):
                print(f"\n{i}. {example['query']}")
                print(f"   → {example['description']}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == '__main__':
    print("🧪 Тестирование SQL Agent API")
    
    # Проверка доступности
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API доступен\n")
        else:
            print("❌ API недоступен")
            exit(1)
    except:
        print("❌ API не запущен. Запустите: python sql_agent_api.py")
        exit(1)
    
    # Тесты
    test_schema()
    test_examples()
    
    # Примеры запросов
    test_query("Сколько заработал Yenlik?")
    test_query("Топ 5 треков по выручке")
    test_query("Yenlik на Spotify в Казахстане")
    test_query("Какие треки у Ernar Amandyq?")
    test_query("Топ 3 платформы по выручке")
    
    print(f"\n{'='*60}")
    print("✅ Тестирование завершено")
    print('='*60)
