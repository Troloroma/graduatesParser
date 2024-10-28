import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Подключение к базе данных MySQL
def create_connection():
    connection = mysql.connector.connect(
        host='localhost',        # Ваш хост MySQL
        database='graduates_db',  # Ваша БД
        user='root',    # Имя пользователя MySQL
        password='angel' # Пароль
    )
    return connection

# Функция для извлечения данных из базы данных
def fetch_data(connection):
    query = """
        SELECT year, education_level, SUM(count_graduate) as total_graduates, 
               SUM(count_graduate * percent_employed / 100) as total_employed
        FROM Graduates
        GROUP BY year, education_level
        ORDER BY year;
    """
    df = pd.read_sql(query, connection)
    return df

# Функция для создания графика
def plot_data(df):
    # Создаем график по уровням образования
    education_levels = df['education_level'].unique()
    plt.figure(figsize=(10, 6))

    for level in education_levels:
        data = df[df['education_level'] == level]
        plt.plot(data['year'], data['total_employed'], label=level)

    plt.title('Трудоустройство выпускников по годам и уровням образования')
    plt.xlabel('Год выпуска')
    plt.ylabel('Количество трудоустроенных выпускников')
    plt.legend(title='Уровень образования')
    plt.grid(True)
    plt.show()

# Основная программа

# Подключение к базе данных
conn = create_connection()

# Извлечение данных
if conn.is_connected():
    df = fetch_data(conn)
    conn.close()  # Закрытие соединения

    # Визуализация данных
    plot_data(df)
