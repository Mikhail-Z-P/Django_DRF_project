# Django_DRF_project

Проект онлайн-обучения на Django REST Framework с поддержкой платежей Stripe,
Celery-задач и контейнеризации через Docker.

# Структура
- `config/` - настройки проекта (settings, urls, wsgi и т.д.)
- `materials/` — приложение курсов, уроков и подписок
- `users/` — приложение пользователей и платежей
- `.github/workflows/ci.yml` — CI/CD пайплайн (GitHub Actions)
- `Dockerfile` — образ приложения
- `docker-compose.yml` — dev-конфигурация
- `docker-compose.prod.yml` — prod-конфигурация (Gunicorn + Nginx)
- `nginx/nginx.conf` — конфигурация Nginx
- `gunicorn_config.py` — конфигурация Gunicorn
- `.flake8` — конфигурация линтера
-  
## Установка через Poetry
1. `poetry install`
2. `poetry shell`


## Локальный запуск (dev)

1. Скопируйте `.env.template` в `.env` и заполните значения:

```bash
cp .env.template .env
```

2. Запустите через Docker:

```bash
docker-compose up -d --build
```

3. Примените миграции и создайте суперпользователя:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

4. Откройте http://localhost:8000/swagger/

## Локальный запуск (prod)

1. Скопируйте `.env.template` в `.env` и заполните значения:

```bash
cp .env.template .env
```

2. Соберите и запустите:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

3. Примените миграции, соберите статику, создайте админа:

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

4. Перезапустите Nginx:

```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

5. Откройте http://localhost:80/swagger/

## Тесты и линтер

```bash
poetry run flake8 .
poetry run python manage.py test
```

## Эндпоинты

- `/` — редирект на Swagger
- `/admin/` — админка Django
- `/swagger/` — Swagger-документация
- `/redoc/` — ReDoc-документация
- `/users/register/` — регистрация
- `/users/token/` — JWT-токены
- `/users/` — пользователи
- `/users/payments/` — платежи
- `/materials/courses/` — курсы (CRUD)
- `/materials/lessons/` — уроки (CRUD)
- `/materials/subscription/` — подписка на курс

## Деплой на удалённый сервер

### Шаг 1. Аренда VPS

Арендуйте VPS с Ubuntu 22.04

### Шаг 2. Подключение по SSH

```bash
ssh root@<IP-адрес-сервера>
```

### Шаг 3. Обновление системы и установка Docker

```bash
apt update && apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Шаг 4. Настройка файрвола

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Шаг 5. SSH-ключи для GitHub Actions

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/github_actions
```

Скопируйте вывод последней команды — это приватный ключ для GitHub Secrets.

### Шаг 6. Клонирование и запуск

```bash
cd /opt
git clone <URL-репозитория> django_drf_project
cd django_drf_project
cp .env.template .env
nano .env
```

Заполните `.env` реальными значениями (IP сервера, секретный ключ, ключи Stripe).

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker compose -f docker-compose.prod.yml restart nginx
```

### Шаг 7. Проверка

Откройте в браузере: `http://<IP-сервера>/swagger/`

## CI/CD (GitHub Actions)

Пайплайн запускается при push и pull request в main/master.

### Этапы

1. **lint** — проверка кода flake8
2. **test** — миграции и тесты Django (PostgreSQL + Redis как services)
3. **build** — сборка Docker-образа и пуш в Docker Hub (только push в main)
4. **deploy** — деплой на сервер через SSH (только push в main)

Цепочка: `lint → test → build → deploy`. Если любой этап падает — следующие не запускаются.

### GitHub Secrets

Добавьте в Settings → Secrets and variables → Actions:

| Секрет | Описание |
|--------|----------|
| `SSH_KEY` | Приватный SSH-ключ сервера |
| `SSH_USER` | Пользователь на сервере (например root) |
| `SERVER_IP` | IP-адрес сервера |
| `DEPLOY_DIR` | Путь к проекту на сервере (например /opt/django_drf_project) |
| `DOCKER_HUB_USERNAME` | Логин Docker Hub |
| `DOCKER_HUB_ACCESS_TOKEN` | Токен Docker Hub |

## Остановка

```bash
docker-compose down
docker-compose -f docker-compose.prod.yml down
```