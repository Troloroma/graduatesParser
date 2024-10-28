create database graduates_db;
use graduates_db;
CREATE TABLE Regions (
    region_id INT AUTO_INCREMENT PRIMARY KEY,
    object_level VARCHAR(100) NOT NULL,  -- Уровень территориальной единицы
    object_name VARCHAR(255) NOT NULL,   -- Название региона
    oktmo VARCHAR(11) NOT NULL,          -- Код ОКТМО региона
    okato VARCHAR(11) NOT NULL           -- Код ОКАТО региона
);
CREATE TABLE Study_Areas (
    study_area_id INT AUTO_INCREMENT PRIMARY KEY,
    study_area_name VARCHAR(255) NOT NULL -- Область образования
);
CREATE TABLE Specialties (
    specialty_id INT AUTO_INCREMENT PRIMARY KEY,
    specialty_section VARCHAR(255) NOT NULL, -- Укрупненная группа направлений подготовки
    specialty_code VARCHAR(10) NOT NULL,     -- Код специальности
    specialty_name VARCHAR(255) NOT NULL     -- Название специальности
);
CREATE TABLE Graduates (
    graduate_id INT AUTO_INCREMENT PRIMARY KEY,
    region_id INT NOT NULL,                -- Внешний ключ к Regions
    specialty_id INT NOT NULL,             -- Внешний ключ к Specialties
    study_area_id INT NOT NULL,            -- Внешний ключ к Study_Areas
    gender ENUM('Мужской', 'Женский', 'Всего') NOT NULL, -- Пол выпускника
    education_level ENUM('СПО: квалифицированные рабочие и служащие', 
                         'СПО: специалисты среднего звена',
                         'Бакалавриат', 'Специалитет', 'Магистратура') NOT NULL, -- Уровень образования
    year INT NOT NULL,                     -- Год выпуска
    count_graduate INT NOT NULL,           -- Количество выпускников
    percent_employed FLOAT NOT NULL,       -- Доля трудоустроенных выпускников
    average_salary FLOAT,                  -- Средняя зарплата (может быть NULL)
    FOREIGN KEY (region_id) REFERENCES Regions(region_id),
    FOREIGN KEY (specialty_id) REFERENCES Specialties(specialty_id),
    FOREIGN KEY (study_area_id) REFERENCES Study_Areas(study_area_id)
);