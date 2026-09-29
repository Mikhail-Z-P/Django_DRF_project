# Django_DRF_project

# Структура
- `config/` - настройки проекта (settings, urls, wsgi и т.д.)
- `catalog/` - приложение каталога

## Установка
1. `poetry install`
2. `poetry shell`
3. `python manage.py runserver`


## Запуск

1. Скопируйте `.env.sample` в `.env` и заполните значения:

```bash
cp .env.sample .env
```

2. Соберите и запустите все сервисы:

```bash
docker-compose up -d --build
```

3. Создайте суперпользователя:

```bash
docker-compose exec web python manage.py createsuperuser
```


## Остановка

```bash
docker-compose down
```



