import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Настройка стиля
plt.style.use('default')
fig, ax = plt.subplots(1, 1, figsize=(20, 14))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')

# Цвета для разных типов таблиц
COLOR_DIMENSION = '#E3F2FD'  # Светло-голубой - справочники
COLOR_FACT = '#FFF3E0'  # Светло-оранжевый - факты
COLOR_DETAIL = '#F3E5F5'  # Светло-фиолетовый - детальные данные
COLOR_JUNCTION = '#E8F5E9'  # Светло-зеленый - связующие таблицы

def draw_table(ax, x, y, width, height, title, fields, color):
    """Рисует таблицу БД"""
    # Основной прямоугольник
    box = FancyBboxPatch((x, y), width, height,
                         boxstyle="round,pad=0.05",
                         edgecolor='#333', facecolor=color,
                         linewidth=2, zorder=2)
    ax.add_patch(box)
    
    # Заголовок таблицы
    ax.text(x + width/2, y + height - 0.15, title,
            fontsize=10, fontweight='bold', ha='center', va='top')
    
    # Поля таблицы
    field_y = y + height - 0.4
    for field in fields[:6]:  # Показываем только первые 6 полей
        ax.text(x + 0.1, field_y, f"• {field}",
                fontsize=7, ha='left', va='top', family='monospace')
        field_y -= 0.18
    
    if len(fields) > 6:
        ax.text(x + 0.1, field_y, f"... ({len(fields)-6} more)",
                fontsize=6, ha='left', va='top', style='italic', color='gray')

def draw_arrow(ax, x1, y1, x2, y2, style='->'):
    """Рисует стрелку связи"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle=style, color='#666',
                           linewidth=1.5, alpha=0.6,
                           connectionstyle="arc3,rad=0.1", zorder=1)
    ax.add_patch(arrow)

# ============================================
# СПРАВОЧНИКИ (Dimension Tables) - Верхняя часть
# ============================================

# Labels
draw_table(ax, 0.5, 11.5, 2.5, 1.8, 'labels',
           ['label_id (PK)', 'label_name', 'created_at'], COLOR_DIMENSION)

# Artists
draw_table(ax, 3.5, 11.5, 2.5, 1.8, 'artists',
           ['artist_id (PK)', 'artist_name', 'label_id (FK)', 'created_at'], COLOR_DIMENSION)

# Tracks
draw_table(ax, 6.5, 11.5, 2.5, 1.8, 'tracks',
           ['track_id (PK)', 'track_name', 'artist_id (FK)', 'label_id (FK)', 'created_at'], COLOR_DIMENSION)

# Platforms
draw_table(ax, 10, 11.5, 2.5, 1.8, 'platforms',
           ['platform_id (PK)', 'platform_name', 'created_at'], COLOR_DIMENSION)

# Countries
draw_table(ax, 13, 11.5, 2.5, 1.8, 'countries',
           ['country_id (PK)', 'country_name', 'created_at'], COLOR_DIMENSION)

# Subscription Types
draw_table(ax, 16, 11.5, 2.5, 1.8, 'subscription_types',
           ['subscription_type_id (PK)', 'subscription_type_name', 'created_at'], COLOR_DIMENSION)

# ============================================
# АГРЕГИРОВАННЫЕ ТАБЛИЦЫ (Fact Tables) - Средняя часть
# ============================================

# Track Aggregates
draw_table(ax, 1, 8.5, 3, 2.2, 'track_aggregates',
           ['track_aggregate_id (PK)', 'track_id (FK)', 'total_revenue', 
            'total_streams', 'avg_rate', 'platforms_count', 'countries_count'], COLOR_FACT)

# Artist Aggregates
draw_table(ax, 4.5, 8.5, 3, 2.2, 'artist_aggregates',
           ['artist_aggregate_id (PK)', 'artist_id (FK)', 'total_revenue',
            'total_streams', 'tracks_count', 'avg_rate', 'avg_revenue_per_track'], COLOR_FACT)

# Platform Aggregates
draw_table(ax, 8, 8.5, 3, 2.2, 'platform_aggregates',
           ['platform_aggregate_id (PK)', 'platform_id (FK)', 'total_revenue',
            'total_streams', 'tracks_count', 'artists_count', 'avg_rate'], COLOR_FACT)

# ============================================
# ДЕТАЛЬНЫЕ ТАБЛИЦЫ (Detailed Facts) - Нижняя часть
# ============================================

# Track Platform Stats
draw_table(ax, 0.5, 5, 2.8, 2, 'track_platform_stats',
           ['track_platform_stat_id (PK)', 'track_id (FK)', 'platform_id (FK)',
            'streams', 'revenue'], COLOR_DETAIL)

# Track Country Stats
draw_table(ax, 3.8, 5, 2.8, 2, 'track_country_stats',
           ['track_country_stat_id (PK)', 'track_id (FK)', 'country_id (FK)',
            'streams', 'revenue'], COLOR_DETAIL)

# Track Subscription Stats
draw_table(ax, 7.1, 5, 3, 2, 'track_subscription_stats',
           ['track_subscription_stat_id (PK)', 'track_id (FK)', 
            'subscription_type_id (FK)', 'streams'], COLOR_DETAIL)

# Track Monthly Stats
draw_table(ax, 10.6, 5, 2.8, 2, 'track_monthly_stats',
           ['track_monthly_stat_id (PK)', 'track_id (FK)', 'month_date',
            'streams', 'revenue'], COLOR_DETAIL)

# Artist Monthly Stats
draw_table(ax, 13.9, 5, 2.8, 2, 'artist_monthly_stats',
           ['artist_monthly_stat_id (PK)', 'artist_id (FK)', 'month_date',
            'streams', 'revenue'], COLOR_DETAIL)

# ============================================
# СВЯЗУЮЩИЕ ТАБЛИЦЫ (Junction Tables) - Самый низ
# ============================================

# Track Platforms
draw_table(ax, 1, 2, 2.5, 1.5, 'track_platforms',
           ['track_id (FK)', 'platform_id (FK)'], COLOR_JUNCTION)

# Track Countries
draw_table(ax, 4, 2, 2.5, 1.5, 'track_countries',
           ['track_id (FK)', 'country_id (FK)'], COLOR_JUNCTION)

# Artist Platforms
draw_table(ax, 7, 2, 2.5, 1.5, 'artist_platforms',
           ['artist_id (FK)', 'platform_id (FK)'], COLOR_JUNCTION)

# Artist Countries
draw_table(ax, 10, 2, 2.5, 1.5, 'artist_countries',
           ['artist_id (FK)', 'country_id (FK)'], COLOR_JUNCTION)

# ============================================
# СВЯЗИ (Relationships)
# ============================================

# Labels -> Artists
draw_arrow(ax, 1.75, 11.5, 4.5, 13, '->')

# Labels -> Tracks
draw_arrow(ax, 2.5, 11.5, 6.8, 12.5, '->')

# Artists -> Tracks
draw_arrow(ax, 4.75, 11.5, 7.2, 12.5, '->')

# Tracks -> Track Aggregates
draw_arrow(ax, 7.5, 11.5, 2.5, 10.7, '->')

# Artists -> Artist Aggregates
draw_arrow(ax, 4.75, 11.5, 6, 10.7, '->')

# Platforms -> Platform Aggregates
draw_arrow(ax, 11.25, 11.5, 9.5, 10.7, '->')

# Tracks -> Track Platform Stats
draw_arrow(ax, 7.2, 11.5, 1.9, 7, '->')

# Tracks -> Track Country Stats
draw_arrow(ax, 7.5, 11.5, 5.2, 7, '->')

# Tracks -> Track Subscription Stats
draw_arrow(ax, 7.75, 11.5, 8.6, 7, '->')

# Tracks -> Track Monthly Stats
draw_arrow(ax, 7.8, 11.5, 12, 7, '->')

# Artists -> Artist Monthly Stats
draw_arrow(ax, 5, 11.5, 15.3, 7, '->')

# Platforms -> Track Platform Stats
draw_arrow(ax, 10.5, 11.5, 2.5, 7, '->')

# Countries -> Track Country Stats
draw_arrow(ax, 13.5, 11.5, 5.8, 7, '->')

# Subscription Types -> Track Subscription Stats
draw_arrow(ax, 16.5, 11.5, 9.5, 7, '->')

# Tracks -> Track Platforms (junction)
draw_arrow(ax, 7.2, 11.5, 2.25, 3.5, '->')

# Tracks -> Track Countries (junction)
draw_arrow(ax, 7.5, 11.5, 5.25, 3.5, '->')

# Artists -> Artist Platforms (junction)
draw_arrow(ax, 4.75, 11.5, 8.25, 3.5, '->')

# Artists -> Artist Countries (junction)
draw_arrow(ax, 5, 11.5, 11.25, 3.5, '->')

# Platforms -> Track Platforms (junction)
draw_arrow(ax, 10.8, 11.5, 2.8, 3.5, '->')

# Platforms -> Artist Platforms (junction)
draw_arrow(ax, 11, 11.5, 8.5, 3.5, '->')

# Countries -> Track Countries (junction)
draw_arrow(ax, 13.8, 11.5, 5.8, 3.5, '->')

# Countries -> Artist Countries (junction)
draw_arrow(ax, 14, 11.5, 11.5, 3.5, '->')

# ============================================
# ЛЕГЕНДА И ЗАГОЛОВОК
# ============================================

# Заголовок
ax.text(10, 13.7, 'СХЕМА БАЗЫ ДАННЫХ МУЗЫКАЛЬНОЙ АНАЛИТИКИ',
        fontsize=18, fontweight='bold', ha='center', va='top')

# Легенда
legend_y = 0.8
legend_elements = [
    mpatches.Patch(facecolor=COLOR_DIMENSION, edgecolor='#333', label='Справочники (Dimensions)'),
    mpatches.Patch(facecolor=COLOR_FACT, edgecolor='#333', label='Агрегаты (Fact Tables)'),
    mpatches.Patch(facecolor=COLOR_DETAIL, edgecolor='#333', label='Детальная статистика'),
    mpatches.Patch(facecolor=COLOR_JUNCTION, edgecolor='#333', label='Связующие таблицы (Many-to-Many)')
]
ax.legend(handles=legend_elements, loc='lower center', ncol=4, 
          fontsize=10, frameon=True, fancybox=True)

# Описание уровней
ax.text(19, 12.5, 'УРОВЕНЬ 1:\nСправочники', fontsize=8, ha='right', 
        bbox=dict(boxstyle='round', facecolor=COLOR_DIMENSION, alpha=0.7))
ax.text(19, 9.5, 'УРОВЕНЬ 2:\nАгрегаты', fontsize=8, ha='right',
        bbox=dict(boxstyle='round', facecolor=COLOR_FACT, alpha=0.7))
ax.text(19, 6, 'УРОВЕНЬ 3:\nДетали', fontsize=8, ha='right',
        bbox=dict(boxstyle='round', facecolor=COLOR_DETAIL, alpha=0.7))
ax.text(19, 2.8, 'УРОВЕНЬ 4:\nСвязи M:N', fontsize=8, ha='right',
        bbox=dict(boxstyle='round', facecolor=COLOR_JUNCTION, alpha=0.7))

plt.tight_layout()
plt.savefig('/Users/nuraliserikbay/analytics_scripts/database_schema_diagram.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Диаграмма схемы БД сохранена: database_schema_diagram.png")

# Создаем также упрощенную версию для быстрого понимания
fig2, ax2 = plt.subplots(1, 1, figsize=(16, 10))
ax2.set_xlim(0, 16)
ax2.set_ylim(0, 10)
ax2.axis('off')

# Упрощенная схема - только основные таблицы и связи
def draw_simple_table(ax, x, y, width, height, title, color, key_info=''):
    box = FancyBboxPatch((x, y), width, height,
                         boxstyle="round,pad=0.08",
                         edgecolor='#333', facecolor=color,
                         linewidth=2.5, zorder=2)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2 + 0.15, title,
            fontsize=12, fontweight='bold', ha='center', va='center')
    if key_info:
        ax.text(x + width/2, y + height/2 - 0.2, key_info,
                fontsize=8, ha='center', va='center', style='italic', color='#555')

# Центральные таблицы
draw_simple_table(ax2, 3, 6.5, 2.5, 1.2, 'LABELS', COLOR_DIMENSION, 'Лейблы')
draw_simple_table(ax2, 6.5, 6.5, 2.5, 1.2, 'ARTISTS', COLOR_DIMENSION, 'Артисты')
draw_simple_table(ax2, 10, 6.5, 2.5, 1.2, 'TRACKS', COLOR_DIMENSION, 'Треки')

# Справочники
draw_simple_table(ax2, 0.5, 4, 2, 1, 'PLATFORMS', COLOR_DIMENSION, 'Платформы')
draw_simple_table(ax2, 3, 4, 2, 1, 'COUNTRIES', COLOR_DIMENSION, 'Страны')
draw_simple_table(ax2, 5.5, 4, 2.5, 1, 'SUBSCRIPTION\nTYPES', COLOR_DIMENSION, 'Подписки')

# Агрегаты
draw_simple_table(ax2, 1.5, 2, 3, 1, 'TRACK AGGREGATES', COLOR_FACT, 'Агрегация по трекам')
draw_simple_table(ax2, 5, 2, 3, 1, 'ARTIST AGGREGATES', COLOR_FACT, 'Агрегация по артистам')
draw_simple_table(ax2, 8.5, 2, 3, 1, 'PLATFORM AGGREGATES', COLOR_FACT, 'Агрегация по платформам')

# Детальная статистика
draw_simple_table(ax2, 0.5, 0.2, 2.3, 0.8, 'Track × Platform', COLOR_DETAIL)
draw_simple_table(ax2, 3, 0.2, 2.3, 0.8, 'Track × Country', COLOR_DETAIL)
draw_simple_table(ax2, 5.5, 0.2, 2.3, 0.8, 'Track × Month', COLOR_DETAIL)
draw_simple_table(ax2, 8, 0.2, 2.3, 0.8, 'Artist × Month', COLOR_DETAIL)
draw_simple_table(ax2, 10.5, 0.2, 2.3, 0.8, 'Track × Subscription', COLOR_DETAIL)

# Связи
def draw_simple_arrow(ax, x1, y1, x2, y2, label=''):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', color='#444',
                           linewidth=2, alpha=0.7,
                           connectionstyle="arc3,rad=0.15", zorder=1)
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y, label, fontsize=7, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Основные связи
draw_simple_arrow(ax2, 4.25, 6.5, 6.8, 7.1, '1:N')
draw_simple_arrow(ax2, 7.75, 6.5, 10.2, 7.1, '1:N')
draw_simple_arrow(ax2, 11.25, 6.5, 3, 3, 'aggr')
draw_simple_arrow(ax2, 7.75, 6.5, 6.5, 3, 'aggr')
draw_simple_arrow(ax2, 11.25, 6.5, 1.6, 1, 'detail')
draw_simple_arrow(ax2, 11.25, 6.5, 4.1, 1, 'detail')
draw_simple_arrow(ax2, 11.25, 6.5, 6.6, 1, 'detail')

# Заголовок
ax2.text(8, 9.3, 'УПРОЩЕННАЯ СХЕМА БД - ОСНОВНЫЕ СВЯЗИ',
        fontsize=16, fontweight='bold', ha='center')

# Описание
description = """
📊 СТРУКТУРА ДАННЫХ:
• Справочники (синий): Базовые сущности - лейблы, артисты, треки, платформы, страны
• Агрегаты (оранжевый): Предрасчитанная статистика для быстрых запросов
• Детали (фиолетовый): Детальная разбивка по платформам, странам, месяцам
"""
ax2.text(8, 8.5, description, fontsize=9, ha='center', va='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f0f0', alpha=0.8))

# Легенда
legend_elements2 = [
    mpatches.Patch(facecolor=COLOR_DIMENSION, edgecolor='#333', label='Справочники'),
    mpatches.Patch(facecolor=COLOR_FACT, edgecolor='#333', label='Агрегаты'),
    mpatches.Patch(facecolor=COLOR_DETAIL, edgecolor='#333', label='Детальная статистика')
]
ax2.legend(handles=legend_elements2, loc='lower center', ncol=3, 
          fontsize=10, frameon=True, fancybox=True)

plt.tight_layout()
plt.savefig('/Users/nuraliserikbay/analytics_scripts/database_schema_simple.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Упрощенная диаграмма сохранена: database_schema_simple.png")

plt.close('all')
