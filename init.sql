-- Создаем базу данных, если она еще не существует
CREATE DATABASE qwertytown
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Предоставляем все права пользователю postgres
GRANT ALL PRIVILEGES ON DATABASE qwertytown TO postgres;

-- Комментарий к базе данных
COMMENT ON DATABASE qwertytown IS 'База данных для бизнес-модуля QwertyTown'; 