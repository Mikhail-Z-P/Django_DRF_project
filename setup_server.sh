#!/bin/bash
set -e

echo "Обновление системы"
apt update && apt upgrade -y

echo "Установка Docker"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

echo "Настройка файрвола UFW"
ufw allow OpenSSH
ufw allow 80/tcp
ufw --force enable

echo "Настройка SSH: запрет парольной аутентификации"
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

echo "Сервер готов к деплою"
echo "Следующие шаги:"
echo "1. Добавьте публичный SSH-ключ в ~/.ssh/authorized_keys"
echo "2. Склонируйте репозиторий: git clone <repo-url> /opt/app"
echo "3. Создайте .env из .env.template"
echo "4. Запустите: docker-compose -f docker-compose.prod.yml up -d --build"
