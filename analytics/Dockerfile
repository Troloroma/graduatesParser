# Базовый образ с Jupyter и Python
FROM jupyter/base-notebook:latest

# Убедимся, что работаем от пользователя root
USER root

# Устанавливаем необходимые зависимости
RUN pip install --no-cache-dir \
    pandas \
    matplotlib \
    sqlalchemy \
    geopandas \
    psycopg2-binary \
    shapely \
    nbconvert

# Устанавливаем рабочую директорию для Jupyter
WORKDIR /home/jovyan/analytics

# Копируем geojson файл в контейнер
COPY ./russia_regions/russia_regions.geojson ./russia_regions/russia_regions.geojson

# Копируем Jupyter Notebook в контейнер
COPY analytics.ipynb ./

# Создаем директорию для вывода и настраиваем права
RUN mkdir -p ./output && \
    chown -R jovyan:users ./output && \
    chmod -R 755 ./output


# Открываем порт для Jupyter
EXPOSE 8888

# Запускаем Jupyter Notebook
CMD ["jupyter", "notebook", "--ip='*'", "--port=8888", "--no-browser", "--allow-root"]
