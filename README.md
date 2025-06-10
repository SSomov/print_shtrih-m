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
KKT_NUMBER=0000000000000000
FN_NUMBER=9999999999999999
```

Uvicorn, FastAPI

```uvicorn srv:app --host 0.0.0.0```

## Новое в API

- Все попытки пробития чеков и отправки в ЕГАИС логируются в текстовые файлы с timestamp (например, check_YYYYMMDD_HHMMSS.txt, egais_response_YYYYMMDD_HHMMSS.txt). В файлы попадают как успешные ответы, так и ошибки.
- При успешной и неуспешной печати чеков API возвращает статус ("success" или "error"), сообщение, имя файла лога и, при ошибке, текст ошибки.
- При успешной отправке чека в ЕГАИС, если в ответе есть QR-код, он автоматически печатается на ККТ.

## Примеры эндпоинтов

- POST `/api/v1/payment/cash` и `/api/v1/payment/card` — пробитие чека. Возвращает:
  ```json
  {"status": "success", "message": "Чек успешно напечатан", "filename": "check_YYYYMMDD_HHMMSS.txt"}
  {"status": "error", "message": "Ошибка при печати чека", "filename": "check_YYYYMMDD_HHMMSS.txt", "error": "..."}
  ```
- POST `/api/v1/send-egais-check` — отправка чека с алкогольной позицией в ЕГАИС. Возвращает:
  ```json
  {"message": "Чек v4 отправлен в ЕГАИС", "egais_response": "...", "qr_code": "...", "saved_file": "egais_response_YYYYMMDD_HHMMSS.txt"}
  ```
  QR-код из ответа ЕГАИС печатается на ККТ автоматически.

## Логирование

- Все ответы и ошибки сохраняются в текстовые файлы в рабочей директории.
- Формат файла: префикс (check/egais_response) + timestamp.
- В случае ошибки в файл добавляется traceback и текст ошибки.

## Переменные окружения

- ORG_TITLE — название организации
- MAX_DISCOUNT — учитывать ли ограничение максимальной скидки
- CUT_INVOICE — отрезка счета
- EGAIS_HOST — адрес УТМ ЕГАИС
- EGAIS_LOGIN, EGAIS_PASSWORD — логин/пароль для ЕГАИС (если требуется)
- KKT_NUMBER, FN_NUMBER — реквизиты ККТ и ФН для формирования чека v4