import os
import zipfile

import pandas as pd
import psycopg2
from psycopg2 import sql

# Подключение к базе данных PostgreSQL
def create_connection():
    try:
        connection = psycopg2.connect(
            dbname='graduates_db',  # База данных
            user='postgres',  # Имя пользователя PostgreSQL
            password='12345678',  # Пароль
            host='localhost',        # Адрес PostgreSQL
            port='5432'
        )
        print("Подключение к базе данных PostgreSQL успешно!")
        return connection
    except psycopg2.Error as e:
        print("Ошибка подключения к базе данных PostgeSQL")
        print(f"Error: '{e}'")
        return None

# Функция для проверки пустоты таблиц
def is_table_empty(cursor, table_name):
    cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1;")
    return cursor.fetchone() is None

# Функция для загрузки данных в таблицы
def load_data_to_db(connection):
    cursor = connection.cursor()

    # Проверяем, есть ли данные в таблицах
    tables = ['Regions', 'Study_Areas', 'Specialties', 'Graduates']
    if all(not is_table_empty(cursor, table) for table in tables):
        print("Таблицы уже содержат необходимые данные, останавливаю перенос.")
        return

    archive_folder = './csv_data/'

    for file_name in os.listdir(archive_folder):
        if file_name.startswith('data_graduates_specialty') and file_name.endswith('.zip'):
            archive_path = os.path.join(archive_folder, file_name)
            break
    else:
        raise FileNotFoundError("Архив с именем 'data_graduates_specialty_...' не найден.")

    with zipfile.ZipFile(archive_path, 'r') as archive:
        csv_files = [f for f in archive.namelist() if f.startswith('data_graduates_specialty') and f.endswith('.csv')]
        if not csv_files:
            raise FileNotFoundError("CSV файл 'data_graduates_specialty' не найден в архиве.")

        with archive.open(csv_files[0]) as file:
            data = pd.read_csv(file, sep=';', encoding='utf-8')

    # Уникальные регионы (заполнение таблицы Regions)
    regions = data[['object_level', 'object_name', 'oktmo', 'okato']].drop_duplicates()
    for _, row in regions.iterrows():
        cursor.execute(sql.SQL("""
            INSERT INTO Regions (object_level, object_name, oktmo, okato)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (object_name) DO UPDATE
            SET object_name = EXCLUDED.object_name
        """), (row['object_level'], row['object_name'], row['oktmo'], row['okato']))

    # Уникальные области образования (заполнение таблицы Study_Areas)
    study_areas = data[['study_area']].drop_duplicates()
    for _, row in study_areas.iterrows():
        cursor.execute(sql.SQL("""
            INSERT INTO Study_Areas (study_area_name)
            VALUES (%s)
            ON CONFLICT (study_area_name) DO UPDATE
            SET study_area_name = EXCLUDED.study_area_name
        """), (row['study_area'],))

    # Уникальные специальности (заполнение таблицы Specialties)
    specialties = data[['specialty_section', 'specialty_code', 'specialty']].drop_duplicates()
    for _, row in specialties.iterrows():
        cursor.execute(sql.SQL("""
            INSERT INTO Specialties (specialty_section, specialty_code, specialty_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (specialty_code) DO UPDATE
            SET specialty_name = EXCLUDED.specialty_name
        """), (row['specialty_section'], row['specialty_code'], row['specialty']))

    # Основные данные выпускников (заполнение таблицы Graduates)
    for _, row in data.iterrows():
        # Получение ID региона
        cursor.execute("SELECT region_id FROM Regions WHERE object_name = %s", (row['object_name'],))
        region_id = cursor.fetchone()[0]

        # Получение ID области образования
        cursor.execute("SELECT study_area_id FROM Study_Areas WHERE study_area_name = %s", (row['study_area'],))
        study_area_id = cursor.fetchone()[0]

        # Получение ID специальности
        cursor.execute("SELECT specialty_id FROM Specialties WHERE specialty_code = %s", (row['specialty_code'],))
        specialty_id = cursor.fetchone()[0]

        # Вставка данных о выпускниках
        cursor.execute(sql.SQL("""
            INSERT INTO Graduates (region_id, specialty_id, study_area_id, gender, education_level, year, count_graduate, percent_employed, average_salary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """), (
            region_id, specialty_id, study_area_id,
            row['gender'], row['education_level'], row['year'], row['count_graduate'],
            row['percent_employed'], row['average_salary'] if pd.notna(row['average_salary']) else None
        ))

    # Сохранение изменений
    connection.commit()
    print("Данные успешно загружены в базу данных!")

# Закрытие соединения
def close_connection(connection):
    if connection:
        connection.close()
        print("Соединение с PostgreSQL закрыто.")

# Главная функция
def parse_from_csv_to_db():
    conn = create_connection()
    if conn is not None:
        try:
            load_data_to_db(conn)
        finally:
            close_connection(conn)
