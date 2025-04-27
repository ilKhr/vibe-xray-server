# Xray Reality CLI Manager

Утилита командной строки для управления Xray с протоколом REALITY.

## Возможности

- Настройка конфигурации Xray
- Запуск и остановка Xray через Docker
- Добавление и удаление пользователей
- Генерация QR-кодов с конфигурацией для клиентов
- Получение JSON-конфигурации для клиентов
- Генерация VLESS URI-ссылок для быстрой настройки клиентов
- Генерация QR-кодов для VLESS URI-ссылок
- Генерация ключей для REALITY
- Частичное обновление конфигурации

## Требования

- Python 3.6+
- Docker
- Библиотеки: qrcode, pillow

## Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/username/xray-reality-manager.git
cd xray-reality-manager
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

## Использование

### Создание конфигурации

```bash
python3 main.py config --dest example.com:443 --server-names example.com www.example.com --port 443 --save config.json
```

### Обновление параметров существующей конфигурации

```bash
python3 main.py config --dest new-example.com:443 --save config.json
```

### Генерация ключей

```bash
python3 main.py gen-keys --save-to-config config.json
```

### Генерация и сохранение ключей в конфигурацию

```bash
python3 main.py gen-keys --save-to-config config.json
```

### Запуск Xray

```bash
python3 main.py start --config config.json --detach
```

### Остановка Xray

```bash
python3 main.py stop
```

### Добавление пользователя

```bash
python3 main.py add-user --name username --config config.json
```

### Удаление пользователя

```bash
python3 main.py remove-user --name username --config config.json
```

### Список пользователей

```bash
python3 main.py list-users --config config.json
```

### Генерация QR-кода для пользователя

```bash
python3 main.py qr --name username --config config.json --save qrcode.png
```

### Отображение QR-кода в терминале

```bash
python3 main.py qr --name username --config config.json
```

### Получение JSON-конфигурации для пользователя

```bash
python3 main.py get-config --name username --config config.json
```

### Сохранение JSON-конфигурации в файл

```bash
python3 main.py get-config --name username --config config.json --save client-config.json
```

### Получение VLESS URI-ссылки

```bash
python3 main.py vless-link --name username --config config.json
```

### Получение VLESS URI-ссылки с указанием сервера

```bash
python3 main.py vless-link --name username --config config.json --server 123.45.67.89
```

### Сохранение VLESS URI-ссылки в файл

```bash
python3 main.py vless-link --name username --config config.json --server 123.45.67.89 --save vless-link.txt
```

### Отображение QR-кода для VLESS URI-ссылки в терминале

```bash
python3 main.py vless-link --name username --config config.json --server 123.45.67.89 --qr
```

### Сохранение QR-кода для VLESS URI-ссылки в файл

```bash
python3 main.py vless-link --name username --config config.json --server 123.45.67.89 --qr-save vless-qr.png
```

## Примеры использования

### Полный процесс настройки

1. Создать конфигурацию:
```bash
python3 main.py config --dest example.com:443 --server-names example.com www.example.com
```

2. Добавить пользователя:
```bash
python3 main.py add-user --name user1
```

3. Запустить Xray:
```bash
python3 main.py start --detach
```

4. Сгенерировать QR-код для пользователя:
```bash
python3 main.py qr --name user1 --save user1_qr.png
```

5. Сгенерировать VLESS ссылку для пользователя:
```bash
python3 main.py vless-link --name user1 --server 123.45.67.89
```

6. Сгенерировать QR-код для VLESS ссылки:
```bash
python3 main.py vless-link --name user1 --server 123.45.67.89 --qr-save vless_qr.png
```

### Обновление существующей конфигурации

Если вам нужно изменить только целевой домен:
```bash
python3 main.py config --dest new-domain.com:443
```

Если вам нужно обновить список имен серверов:
```bash
python3 main.py config --server-names new-domain.com www.new-domain.com
```

### Обновление ключей

```bash
python3 main.py gen-keys --save-to-config config.json
```

## Примечания

- Для работы приложения требуется установленный Docker
- При запуске Xray используется порт 443, убедитесь, что он свободен или измените порт в конфигурации
- Конфигурация и метаданные о пользователях сохраняются в JSON файлах
