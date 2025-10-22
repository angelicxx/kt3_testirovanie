# Microservices API (Users + Orders) — Flask

Два простых микросервиса на Python/Flask:
- **user-service**: создание и получение пользователей
- **order-service**: создание и получение заказов; при создании заказа обращается к user-service по `user_id`

### user-service
- `POST /users` — создать пользователя
  - Body JSON: `{ "name": "Alice", "email": "alice@example.com" }`
  - Response 201: `{ "id": 1, "name": "Alice", "email": "alice@example.com" }`

- `GET /users/<id>` — получить пользователя
  - Response 200 / 404

### order-service
- `POST /orders` — создать заказ (обращается к user-service)
  - Body JSON: `{ "user_id": 1, "item": "Book", "price": 10.5 }`
  - Response 201: заказ + поля `user_name`, `user_email`
  - Заголовок `X-User-Service-Url` (опционально): переопределяет адрес user-service на время запроса (удобно для негативных тестов)

- `GET /orders/<id>` — получить заказ
  - Response 200 / 404

## Тестирование в Postman (коллекция в `postman_collection.json`)

1) **Create User** — создаёт пользователя и сохраняет `userId` в переменную окружения  
2) **Create Order** — создаёт заказ с использованием `userId`, проверяет статус 201 и время ответа  
3) **Create Order — user-service DOWN** — отправляет заказ с заголовком `X-User-Service-Url: http://127.0.0.1:5999` (недоступный порт) и ожидает 503

Коллекция содержит автотесты:
- успех запроса данных пользователя сервисом заказов
- обработка ошибок при недоступности сервиса пользователей
- проверка времени отклика (по умолчанию < 2000 мс)

- Порты по умолчанию: users — 5001, orders — 5002.
