import psycopg2
import contextlib

def create_database_and_tables():
    # Параметры подключения к PostgreSQL
    db_params = {
        'dbname': 'postgres',   # Используем системную БД для проверки и создания базы
        'user': 'postgres',         # Логин БД
        'password': '12345678', # Пароль от БД
        'host': 'postgres',    # Адрес БД
        'port': '5432'            # Порт БД
    }

    # Имя создаваемой базы данных
    target_db = 'graduates_db'

    # Подключаемся к PostgreSQL
    try:
        with contextlib.closing(psycopg2.connect(**db_params)) as conn:
            conn.autocommit = True  # Включаем autocommit для создания базы
            with conn.cursor() as cursor:
                # Проверяем существование базы данных
                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{target_db}';")
                db_exists = cursor.fetchone()

                # Если не существует, создаем её
                if not db_exists:
                    cursor.execute(f"CREATE DATABASE {target_db};")
                    print(f"База данных '{target_db}' успешно создана.")
                else:
                    print(f"База данных '{target_db}' уже существует.")
    except Exception as e:
        print("Ошибка подключения к базе данных")
        print(f"Error: {e}")
        return

    # Подключаемся к созданной (или существующей) базе данных
    db_params['dbname'] = target_db
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cursor:
                # Проверяем и создаем таблицы
                create_tables(cursor)
    except Exception as e:
        print(f"Error: {e}")


def create_tables(cursor):
    tables = {
        "Regions": """
            CREATE TABLE IF NOT EXISTS Regions (
                region_id SERIAL PRIMARY KEY,
                object_level VARCHAR(100) NOT NULL,
                object_name VARCHAR(255) NOT NULL,
                oktmo VARCHAR(11) NOT NULL,
                okato VARCHAR(11) NOT NULL
            );
            CREATE UNIQUE INDEX ON Regions (object_name);
        """,
        "Study_Areas": """
            CREATE TABLE IF NOT EXISTS Study_Areas (
                study_area_id SERIAL PRIMARY KEY,
                study_area_name VARCHAR(255) NOT NULL
            );
            CREATE UNIQUE INDEX ON Study_Areas (study_area_name);  
        """,
        "Specialties": """
            CREATE TABLE IF NOT EXISTS Specialties (
                specialty_id SERIAL PRIMARY KEY,
                specialty_section VARCHAR(255) NOT NULL,
                specialty_code VARCHAR(10) NOT NULL,
                specialty_name VARCHAR(255) NOT NULL
            );
            CREATE UNIQUE INDEX ON Specialties (specialty_code);
        """,
        "Graduates": """
            CREATE TABLE IF NOT EXISTS Graduates (
                graduate_id SERIAL PRIMARY KEY,
                region_id INT NOT NULL,
                specialty_id INT NOT NULL,
                study_area_id INT NOT NULL,
                gender VARCHAR(20) CHECK (gender IN ('Мужской', 'Женский', 'Всего')) NOT NULL,
                education_level VARCHAR(255) NOT NULL,
                year INT NOT NULL,
                count_graduate INT NOT NULL,
                percent_employed FLOAT NOT NULL,
                average_salary FLOAT,
                FOREIGN KEY (region_id) REFERENCES Regions(region_id),
                FOREIGN KEY (specialty_id) REFERENCES Specialties(specialty_id),
                FOREIGN KEY (study_area_id) REFERENCES Study_Areas(study_area_id)
            );
        """
    }

    for table_name, create_query in tables.items():
        try:
            cursor.execute(create_query)
            print(f"Таблица '{table_name}' готова к использованию.")
        except Exception as e:
            print(f"Ошибка в создании/использовании таблицы '{table_name}': {e}")


"""
Описание полей:
        object_level -- Уровень территориальной единицы
        object_name -- Название региона
        oktmo -- Код ОКТМО региона
        okato -- Код ОКАТО региона
        study_area_name -- Область образования
        specialty_section -- Укрупненная группа направлений подготовки
        specialty_code -- Код специальности
        specialty_name -- Название специальности
        region_id INT NOT NULL,                -- Внешний ключ к Regions
        specialty_id -- Внешний ключ к Specialties
        study_area_id -- Внешний ключ к Study_Areas
        gender -- Пол выпускника
        education_level -- Уровень образования
        year -- Год выпуска
        count_graduate -- Количество выпускников
        percent_employed -- Доля трудоустроенных выпускников
        average_salary -- Средняя зарплата (может быть NULL)
"""