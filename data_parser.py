import os
import zipfile

import pandas as pd
import mysql.connector
from mysql.connector import Error


# Подключение к базе данных MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',        # Ваш хост MySQL
            database='graduates_db',  # Ваша БД
            user='root',    # Имя пользователя MySQL
            password='angel' # Пароль
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None


# Функция для загрузки данных в таблицы
def load_data_to_db(connection):
    cursor = connection.cursor()

    archive_folder = './csv_data/'

    for file_name in os.listdir(archive_folder):
        if file_name.startswith('data_graduates_specialty') and file_name.endswith('.zip'):
            archive_path = os.path.join(archive_folder, file_name)
            break
    else:
        raise FileNotFoundError("Archive with name 'data_graduates_specialty_...' not found.")

    with zipfile.ZipFile(archive_path, 'r') as archive:
        csv_files = [f for f in archive.namelist() if f.startswith('data_graduates_specialty') and f.endswith('.csv')]
        if not csv_files:
            raise FileNotFoundError("CSV file with name starting 'data_graduates_specialty' not found in archive.")

        with archive.open(csv_files[0]) as file:
            data = pd.read_csv(file, sep=';', encoding='utf-8')

    # Уникальные регионы (заполнение таблицы Regions)
    regions = data[['object_level', 'object_name', 'oktmo', 'okato']].drop_duplicates()
    for _, row in regions.iterrows():
        cursor.execute("""
            INSERT INTO Regions (object_level, object_name, oktmo, okato)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE object_name = VALUES(object_name)
        """, (row['object_level'], row['object_name'], row['oktmo'], row['okato']))

    # Уникальные области образования (заполнение таблицы Study_Areas)
    study_areas = data[['study_area']].drop_duplicates()
    for _, row in study_areas.iterrows():
        cursor.execute("""
            INSERT INTO Study_Areas (study_area_name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE study_area_name = VALUES(study_area_name)
        """, (row['study_area'],))

    # Уникальные специальности (заполнение таблицы Specialties)
    specialties = data[['specialty_section', 'specialty_code', 'specialty']].drop_duplicates()
    for _, row in specialties.iterrows():
        cursor.execute("""
            INSERT INTO Specialties (specialty_section, specialty_code, specialty_name)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE specialty_name = VALUES(specialty_name)
        """, (row['specialty_section'], row['specialty_code'], row['specialty']))

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
        cursor.execute("""
            INSERT INTO Graduates (region_id, specialty_id, study_area_id, gender, education_level, year, count_graduate, percent_employed, average_salary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            region_id, specialty_id, study_area_id,
            row['gender'], row['education_level'], row['year'], row['count_graduate'],
            row['percent_employed'], row['average_salary'] if pd.notna(row['average_salary']) else None
        ))

    # Сохранение изменений
    connection.commit()
    print("Data loaded successfully!")


# Закрытие соединения
def close_connection(connection):
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")


def parse_from_csv_to_db():
    conn = create_connection()
    if conn is not None:
        load_data_to_db(conn)
        close_connection(conn)