#!/bin/bash

# Переменные
OUTPUT_DIR="./output"
DOCKER_COMPOSE_FILE="docker-compose.yml"
PARSER_CONTAINER="parser-container"
ANALYSIS_CONTAINER="analysis-container"
DB_CONTAINER="data-base-container"
OUTPUT_FILE="${OUTPUT_DIR}/output.html"

# Проверка прав пользователя
if [ "$EUID" -ne 0 ]; then
  echo "Пожалуйста, запустите этот скрипт с правами root (используйте sudo)."
  exit 1
fi

# Создание и настройка папки output
if [ -d "$OUTPUT_DIR" ]; then
  echo "Папка output существует. Перезаписываем её."
  rm -rf "$OUTPUT_DIR"
fi

mkdir "$OUTPUT_DIR"
chmod -R 775 "$OUTPUT_DIR"
chown -R $(id -u):$(id -g) "$OUTPUT_DIR"
echo "Папка output создана и настроена."

# Билд и запуск контейнеров
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
  echo "Осуществляем сборку и запуск контейнеров через docker-compose..."
  docker-compose up --build -d
  echo "Контейнеры запущены."
else
  echo "Файл docker-compose.yml не найден. Убедитесь, что он находится в корневой папке дистрибутива."
  exit 1
fi

# Функция для проверки состояния контейнера
check_container_status() {
  local container_name=$1
  docker inspect -f '{{.State.Status}}' "$container_name" 2>/dev/null
}

# Следим за состоянием контейнеров
while true; do
  PARSER_STATUS=$(check_container_status "$PARSER_CONTAINER")
  ANALYSIS_STATUS=$(check_container_status "$ANALYSIS_CONTAINER")
  DB_STATUS=$(check_container_status "$DB_CONTAINER")

  if [ "$PARSER_STATUS" == "exited" ]; then
    echo "Передача данных в БД завершена. Осуществляется обработка данных."
  fi

  if [ -f "$OUTPUT_FILE" ]; then
    echo "Обработка данных завершена! Результат находится в папке output."
    echo "Останавливаем контейнер analysis-container..."
    docker stop "$ANALYSIS_CONTAINER"
    echo "Контейнер analysis-container остановлен."

    echo "Останавливаем контейнер data-base-container..."
    docker stop "$DB_CONTAINER"
    echo "Контейнер data-base-container остановлен."
    break
  fi

  if [ "$PARSER_STATUS" == "exited" ] && [ "$ANALYSIS_STATUS" == "exited" ] && [ "$DB_STATUS" == "exited" ]; then
    echo "Все контейнеры завершили свою работу."
    break
  fi

  sleep 5  # Задержка перед следующей проверкой
done

exit 0
