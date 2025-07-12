<div id="header" align="center">
  <img src="https://media.giphy.com/media/h408T6Y5GfmXBKW62l/giphy.gif" width="200"/>
</div>

<div id="badges" align="center">
  <a href="https://t.me/devil_on_the_wheel">
    <img src="https://img.shields.io/badge/telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Badge"/>
  </a>
  <a href="https://wa.me/+79117488008">
    <img src="https://img.shields.io/badge/whatsapp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="Telegram Badge"/>
  </a>
  <a href="https://www.linkedin.com/in/igor526/">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Badge"/>
  </a>
  <a href="igor-526@yandex.ru">
    <img src="https://img.shields.io/badge/email-orange?style=for-the-badge&logo=mail.ru&logoColor=white" alt="LinkedIn Badge"/>
  </a>
</div>

<div id="view_counter" align="center">
  <img src="https://komarev.com/ghpvc/?username=igor-526&color=blue&style=for-the-badge&label=ПРОСМОТРЫ"/>
</div>

# 🚀 Complaint Service API

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
| **Backend**     | Python, FastAPI, SQLAlchemy, AioHTTP      |
| **База данных** | PostgreSQL, Alembic                       |
| **Автоматизация** | n8n                                     |
| **Документация** | Swagger UI, ReDoc                        |
| **Инфраструктура** | Docker, Docker Compose                 |

---

## Тестирование проекта
#### API Endpoint: https://complaint.dotw-soft.ru/api/v1/
#### [n8n](https://complaintn8n.dotw-soft.ru/) (для доступа напишите в Telegram в шапке проекта)

---

## 🚀 Запуск проекта

### 1. Клонирование проекта
```bash
git clone https://github.com/igor-526/complaint_service.git
cd complaint_service
```
### 2. Настройка окружения

Создайте файл `.env` в корне проекта на основе примера `example.env`:

```ini
# ========================
# 🌐 Основные настройки
# ========================
API_PORT=8000  # Порт для FastAPI приложения
N8N_PORT=5678  # Порт для доступа к n8n

# ========================
# ☁ Yandex Cloud
# ========================
YA_CLOUD_OAUTH_TOKEN=your_oauth_token  # OAuth-токен для Yandex Cloud API
YA_CLOUD_CATALOG_ID=b1gxxxxxxxxxxxxxxx  # ID каталога в Yandex Cloud

# ========================
#  DaData Service
# ========================
DADATA_API_KEY="your_api_key"  # API Key сервиса DaData

# ========================
# 🤖 AI Промты
# ========================
AI_COMPLAINT_CATEGORY_PROMT="Определи категорию жалобы"
AI_COMPLAINT_SENTIMENT_PROMT="Определи тональность жалобы"
AI_SPAM_PROMT="Это сервис для приёма жалоб. Определи наличие спама в тексте"

# ========================
# ⏱ Настройки HTTP-клиента
# ========================
HTTP_CONNECTION_TIMEOUT=10  # Таймаут соединения в секундах
HTTP_CONNECTION_RETRY_DELAY=5  # Задержка между попытками в секундах
HTTP_CONNECTION_RETRIES=8  # Количество попыток запроса

# ========================
# 🔌 Настройки n8n
# ========================
N8N_USER=admin                  # Логин для входа в n8n
N8N_PASSWORD=your_strong_pass   # Пароль для входа в n8n
N8N_ENCRYPTION_KEY='be1dace747b17baa4417fg20717acfe5' # Encryption key для credentials n8n
```

### 3. Настройка прав доступа каталога n8n
```bash
sudo chown -R 1000:1000 ./n8n_data
sudo chmod -R 755 ./n8n_data
```

### 4. Запуск
```bash
docker compose up
```

### 5. Настройка n8n
Перейдите в панель управления n8n и настройте credentials для Telegram и Google Sheet

---

## Документация API и тестирование сервиса
#### [Swagger UI](https://complaint.dotw-soft.ru/docs)
#### [ReDoc](https://complaint.dotw-soft.ru/redoc)

---

## Дополнительно
#### [Автоматизация](./docs/automatization.md)
#### [Нагрузочное тестирование](./docs/loading_tests.md)
#### [Получение OAuth токена Yandex](https://yandex.cloud/ru/docs/iam/operations/iam-token/create) (Платный сервис)
#### [DaData](https://dadata.ru/api/) (Лимит бесплатных запросов)
#### [Получение Telegram Bot Token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
#### [Создание сервисного аккаунта Google](https://developers.google.com/identity/protocols/oauth2/service-account?hl=ru#creatinganaccount)


