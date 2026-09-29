# Django_DRF_project

# Структура
- `config/` - настройки проекта (settings, urls, wsgi и т.д.)
- `materials/` — приложение курсов, уроков и подписок
- `users/` — приложение пользователей и платежей
## Установка
1. `poetry install`
2. `poetry shell`
3. `python manage.py runserver`


## Запуск через Docker

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
## Эндпоинты
- http://localhost:8000/admin/ — админка Django
- http://localhost:8000/swagger/ — Swagger-документация
- /users/register/ — регистрация
- /users/token/ — JWT-токены
- /users/ — пользователи
- /users/payments/ — платежи
- /materials/courses/ — курсы (CRUD)
- /materials/lessons/ — уроки (CRUD)
- /materials/subscription/ — подписка на курс

## Остановка

```bash
docker-compose down
```



