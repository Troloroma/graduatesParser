# Базовый образ с Jupyter и Python
FROM jupyter/base-notebook:latest

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

# Открываем порт для Jupyter
EXPOSE 8888

# Запускаем Jupyter Notebook
CMD ["jupyter", "notebook", "--ip='*'", "--port=8888", "--no-browser", "--allow-root"]
