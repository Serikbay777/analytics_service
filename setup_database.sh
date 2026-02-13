#!/bin/bash

# =====================================================
# Скрипт для создания базы данных музыкальной аналитики
# =====================================================

set -e  # Остановка при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Создание БД музыкальной аналитики                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# =====================================================
# Шаг 1: Проверка PostgreSQL
# =====================================================
echo -e "${YELLOW}[1/5] Проверка PostgreSQL...${NC}"

if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL не установлен!${NC}"
    echo ""
    echo "Установите PostgreSQL:"
    echo "  macOS: brew install postgresql@15"
    echo "  Ubuntu: sudo apt-get install postgresql-15"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL установлен${NC}"
echo ""

# =====================================================
# Шаг 2: Параметры подключения
# =====================================================
echo -e "${YELLOW}[2/5] Настройка параметров подключения...${NC}"

# Значения по умолчанию
DEFAULT_HOST="localhost"
DEFAULT_PORT="5432"
DEFAULT_USER="postgres"
DEFAULT_DBNAME="music_analytics"

# Запрос параметров у пользователя
read -p "Хост БД [$DEFAULT_HOST]: " DB_HOST
DB_HOST=${DB_HOST:-$DEFAULT_HOST}

read -p "Порт БД [$DEFAULT_PORT]: " DB_PORT
DB_PORT=${DB_PORT:-$DEFAULT_PORT}

read -p "Пользователь БД [$DEFAULT_USER]: " DB_USER
DB_USER=${DB_USER:-$DEFAULT_USER}

read -p "Имя БД [$DEFAULT_DBNAME]: " DB_NAME
DB_NAME=${DB_NAME:-$DEFAULT_DBNAME}

read -sp "Пароль БД: " DB_PASSWORD
echo ""
echo ""

# Сохранение параметров в .env файл
cat > .env.db << EOF
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_USER=$DB_USER
DB_NAME=$DB_NAME
DB_PASSWORD=$DB_PASSWORD
EOF

echo -e "${GREEN}✅ Параметры сохранены в .env.db${NC}"
echo ""

# =====================================================
# Шаг 3: Создание базы данных
# =====================================================
echo -e "${YELLOW}[3/5] Создание базы данных '$DB_NAME'...${NC}"

# Проверка существования БД
DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" postgres 2>/dev/null || echo "")

if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${YELLOW}⚠️  База данных '$DB_NAME' уже существует${NC}"
    read -p "Пересоздать БД? (y/N): " RECREATE
    if [[ $RECREATE =~ ^[Yy]$ ]]; then
        echo "Удаление существующей БД..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;" postgres
        echo "Создание новой БД..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;" postgres
        echo -e "${GREEN}✅ База данных пересоздана${NC}"
    else
        echo "Используем существующую БД"
    fi
else
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;" postgres
    echo -e "${GREEN}✅ База данных создана${NC}"
fi
echo ""

# =====================================================
# Шаг 4: Применение схемы
# =====================================================
echo -e "${YELLOW}[4/5] Применение схемы БД...${NC}"

if [ ! -f "database_schema.sql" ]; then
    echo -e "${RED}❌ Файл database_schema.sql не найден!${NC}"
    exit 1
fi

PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database_schema.sql

echo -e "${GREEN}✅ Схема БД применена${NC}"
echo ""

# =====================================================
# Шаг 5: Проверка
# =====================================================
echo -e "${YELLOW}[5/5] Проверка созданных таблиц...${NC}"

TABLES=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")

echo -e "${GREEN}✅ Создано таблиц: $TABLES${NC}"

# Список таблиц
echo ""
echo "Созданные таблицы:"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt"

echo ""
echo "Созданные представления:"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dv"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ База данных успешно создана!                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Строка подключения:"
echo -e "${BLUE}postgresql://$DB_USER:****@$DB_HOST:$DB_PORT/$DB_NAME${NC}"
echo ""
echo "Следующий шаг: загрузка данных"
echo "  python load_data_to_db.py"
echo ""
