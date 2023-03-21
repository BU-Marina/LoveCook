# Foodgram

[![CI](https://github.com/BU-Marina/Foodgram/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/BU-Marina/Foodgram/actions/workflows/main.yml)

## Описание

Платформа для обмена рецептами

## Запуск проекта в dev-режиме

Клонировать репозиторий:

```
git clone https://github.com/BU-Marina/Foodgram/
```

```
cd Foodgram
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

Если у вас linux/MacOS:

```
. venv/bin/activate
```

Если у вас Windows:

```
. venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции из директории с файлом manage.py:

```
python manage.py makemigrations
```

```
python manage.py migrate
```

Загрузить тестовые данные:

    python manage.py load_test_data

Запустить проект:

    python manage.py runserver

Запуск тестов

```
pytest
```

## Документация с примерами запросов доступна по адресу:

    http://127.0.0.1:8000/redoc/
    http://127.0.0.1:8000/swagger/

## Получение токена аутентификации:

POST-запрос с параметрами email и password на эндпоинт
   
    /api/auth/token/login/
