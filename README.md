Простая реализация API печати счетов и чеков на устройствах Штрих-М для Windows.

Проверялась Windows 7 32-bit.

Написана как переходный этап для ПО 1с 7.7 и ФФД1.2

Поддерживает простые чеки и чеки с маркировкой разливного пива для horeca

Файл внешних параметров .env

```
ORG_TITLE=Название
MAX_DISCOUNT=True # параметр учитывать ли ограничение максимальную скидку на товар
CUT_INVOICE=True # отрезка счета
EGAIS_HOST=http://localhost:8080
EGAIS_LOGIN=your_login
EGAIS_PASSWORD=your_password
EGAIS_SEND=false # отправлять ли в ЕГАИС (true/false)
KKT_NUMBER=0000000000000000
FN_NUMBER=9999999999999999

# PostgreSQL настройки
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=print_logs
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
```

Uvicorn, FastAPI

```uvicorn srv:app --host 0.0.0.0```

## Новое в API

- Все попытки пробития чеков и отправки в ЕГАИС логируются в PostgreSQL БД с использованием Tortoise ORM.
- При успешной и неуспешной печати чеков API возвращает статус ("success" или "error"), сообщение и, при ошибке, текст ошибки.
- При успешной отправке чека в ЕГАИС, если в ответе есть QR-код, он автоматически печатается на ККТ.
- Поддержка переменной EGAIS_SEND для управления отправкой в ЕГАИС (true/false).

## Примеры эндпоинтов

- POST `/api/v1/payment/cash` и `/api/v1/payment/card` — пробитие чека. Возвращает:
  ```json
  {"status": "success", "message": "Чек успешно напечатан"}
  {"status": "error", "message": "Ошибка при печати чека", "error": "..."}
  ```
- POST `/api/v1/send-egais-check` — отправка чека с алкогольной позицией в ЕГАИС. Возвращает:
  ```json
  {"message": "Чек v4 отправлен в ЕГАИС", "egais_response": "...", "qr_code": "...", "saved_file": "egais_response_YYYYMMDD_HHMMSS.txt", "xml_file": "egais_xml_YYYYMMDD_HHMMSS.xml"}
  ```
  QR-код из ответа ЕГАИС печатается на ККТ автоматически.

## API для просмотра логов

- GET `/api/v1/logs/checks?page=1&limit=50&status=success` — получить список логов чеков с пагинацией
- GET `/api/v1/logs/egais?page=1&limit=50&status=success` — получить список логов ЕГАИС с пагинацией  
- GET `/api/v1/logs/stats` — получить статистику по логам (общее количество, успешные, ошибки)

**Параметры пагинации:**
- `page` — номер страницы (по умолчанию 1)
- `limit` — количество записей на странице (по умолчанию 50)
- `status` — фильтр по статусу (success, error, saved)

**Пример ответа с пагинацией:**
```json
{
  "status": "success",
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 150,
    "pages": 3
  }
}
```

## Логирование

- **Приоритет**: PostgreSQL БД (если доступна) → файловое логирование (резервный способ)
- При подключении к БД: данные сохраняются в таблицы `check_logs` и `egais_logs`
- При отсутствии подключения к БД: автоматическое переключение на файловое логирование
- Данные заказов сохраняются в JSON-формате (БД) или текстовом виде (файлы)
- XML-данные и ответы ЕГАИС сохраняются в текстовом виде
- Автоматическое создание схемы БД при запуске приложения (если БД доступна)

## Переменные окружения

- ORG_TITLE — название организации
- MAX_DISCOUNT — учитывать ли ограничение максимальной скидки
- CUT_INVOICE — отрезка счета
- EGAIS_HOST — адрес УТМ ЕГАИС
- EGAIS_LOGIN, EGAIS_PASSWORD — логин/пароль для ЕГАИС (если требуется)
- EGAIS_SEND — отправлять ли в ЕГАИС (true/false)
- KKT_NUMBER, FN_NUMBER — реквизиты ККТ и ФН для формирования чека v4
- POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD — настройки PostgreSQL

## Установка зависимостей

```bash
pip install tortoise-orm[asyncpg] fastapi uvicorn python-dotenv requests lxml
```