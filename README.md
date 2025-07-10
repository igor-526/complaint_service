# 🚀 Complaint Service API

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-24.0-blue?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Микросервис для управления жалобами с современным API и интеграциями.

---

## 🌟 Особенности

- 📝 **CRUD операции** с жалобами
- ✉️ **Telegram-уведомления** при новых жалобах
- **Добавление записей в GoogleSheets** при новых жалобах
- 🐳 **Docker-контейнеризация**
- 📚 **Автодокументация** (Swagger/ReDoc)

---

## 🛠 Технологии

| Категория       | Технологии                                |
|-----------------|-------------------------------------------|
| **Backend**     | Python 3.11, FastAPI, SQLAlchemy, AIOHTTP |
| **База данных** | PostgreSQL, Alembic                       |
| **Документация** | Swagger UI, ReDoc                         |
| **Инфраструктура** | Docker, Docker Compose                    |

---

## 🚀 Запуск проекта

### 1. Клонирование проекта
```bash
git clone https://github.com/igor-526/complaint_service.git
cd complaint_service
```
### 2. Настройка окружения

Создайте файл `.env` в корне проекта на основе примера `.env.example`:

```ini
# ========================
# 🌐 Основные настройки
# ========================
API_PORT=8000  # Порт для FastAPI приложения

# ========================
# ☁ Yandex Cloud
# ========================
YA_CLOUD_OAUTH_TOKEN=your_oauth_token  # OAuth-токен для Yandex Cloud API
YA_CLOUD_CATALOG_ID=b1gxxxxxxxxxxxxxxx  # ID каталога в Yandex Cloud

# ========================
# 🤖 AI Промты
# ========================
AI_COMPLAINT_CATEGORY_PROMT="Определи категорию жалобы (доставка/качество/сервис)"
AI_COMPLAINT_SENTIMENT_PROMT="Определи тональность (позитив/нейтрал/негатив)"
AI_SPAM_PROMT="Является ли сообщение спамом (да/нет)"

# ========================
# ⏱ Настройки HTTP-клиента
# ========================
HTTP_CONNECTION_TIMEOUT=10      # Таймаут соединения в секундах
HTTP_CONNECTION_RETRY_DELAY=5   # Задержка между попытками в секундах
HTTP_CONNECTION_RETRIES=3       # Количество попыток подключения

# ========================
# 🔌 Настройки n8n
# ========================
N8N_PORT=5678                   # Порт для доступа к n8n
N8N_USER=admin                  # Логин для входа в n8n
N8N_PASSWORD=your_strong_pass   # Пароль для входа в n8n
```
