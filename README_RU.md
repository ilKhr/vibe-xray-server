# Xray Reality CLI Manager

Утилита командной строки для управления Xray с протоколом REALITY.

## Возможности

- Настройка конфигурации Xray
- Запуск и остановка Xray через Docker
- Добавление и удаление пользователей
- Генерация QR-кодов с конфигурацией для клиентов
- Генерация ключей для REALITY

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
python main.py config --dest example.com:443 --server-names example.com www.example.com --port 443 --save config.json
```

### Генерация ключей

```bash
python main.py gen-keys
```

### Запуск Xray

```bash
python main.py start --config config.json --detach
```

### Остановка Xray

```bash
python main.py stop
```

### Добавление пользователя

```bash
python main.py add-user --name username --config config.json
```

### Удаление пользователя

```bash
python main.py remove-user --name username --config config.json
```

### Список пользователей

```bash
python main.py list-users --config config.json
```

### Генерация QR-кода для пользователя

```bash
python main.py qr --name username --config config.json --save qrcode.png
```

## Примеры использования

### Полный процесс настройки

1. Создать конфигурацию:
```bash
python main.py config --dest example.com:443 --server-names example.com www.example.com
```

2. Добавить пользователя:
```bash
python main.py add-user --name user1
```

3. Запустить Xray:
```bash
python main.py start --detach
```

4. Сгенерировать QR-код для пользователя:
```bash
python main.py qr --name user1 --save user1_qr.png
```

## Примечания

- Для работы приложения требуется установленный Docker
- При запуске Xray используется порт 443, убедитесь, что он свободен или измените порт в конфигурации
- Конфигурация и метаданные о пользователях сохраняются в JSON файлах
