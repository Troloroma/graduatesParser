import logging
import os
import pandas as pd
import sqlite3
import zipfile

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def parse_from_csv():
    archive_folder = './csv_data/'

    for file_name in os.listdir(archive_folder):
        if file_name.startswith('data_graduates_specialty') and file_name.endswith('.zip'):
            archive_path = os.path.join(archive_folder, file_name)
            break
    else:
        raise FileNotFoundError("Archive with name 'data_graduates_specialty_...' not found.")

    with zipfile.ZipFile(archive_path, 'r') as archive:

        file_list = archive.namelist()

        csv_files = [f for f in file_list if f.endswith('.csv')]

        # Подключаемся к базе данных
        connection = sqlite3.connect('./databases/graduates_data.db')
        logging.info("Start of importing data from csv to database")

        for csv_file in csv_files:
            with archive.open(csv_file) as file:
                # Читаем данные из CSV
                df = pd.read_csv(file, sep=';')
                logging.info(f"Data from {csv_file}:")
                logging.info(df.head())

                # Определяем имя таблицы по имени файла
                if 'specialty' in csv_file:
                    table_name = 'speciality'
                elif 'study_area' in csv_file:
                    table_name = 'study_area'
                else:
                    logging.warning(f"Unknown file format: {csv_file}, skipping...")
                    continue

                # Сохраняем данные в соответствующую таблицу
                df.to_sql(table_name, connection, if_exists='replace', index=False)
                logging.info(f"Data from {csv_file} successfully saved to {table_name} table.")

        logging.info("Successfully added data from csv to database")
        connection.close()
