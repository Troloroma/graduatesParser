# Базовый образ с Python
FROM python:3.10-slim

# Устанавливаем зависимости для работы с PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем библиотеки Python (postgres, pandas)
RUN pip install --no-cache-dir psycopg2-binary pandas

# Создаем рабочую директорию
WORKDIR /app

# Копируем скрипты в контейнер
COPY create_data_base.py data_parser.py main.py ./

# Копируем папку с данными (zip и geojson файлы)
COPY ./csv_data ./csv_data

# Устанавливаем точку входа для main.py
ENTRYPOINT ["python", "main.py"]