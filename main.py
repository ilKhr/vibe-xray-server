#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import json
from config_manager import ConfigManager
from user_manager import UserManager
from docker_manager import DockerManager

def main():
    parser = argparse.ArgumentParser(description='Xray Reality CLI Manager')
    subparsers = parser.add_subparsers(dest='command', help='Команды')

    # Команда для настройки конфигурации
    config_parser = subparsers.add_parser('config', help='Настройка xray конфигурации')
    config_parser.add_argument('--dest', type=str, help='Целевой домен (например, example.com:443)')
    config_parser.add_argument('--server-names', type=str, nargs='+', help='Список имен серверов')
    config_parser.add_argument('--port', type=int, default=443, help='Порт для прослушивания')
    config_parser.add_argument('--save', type=str, help='Путь для сохранения конфигурации', default='config.json')

    # Команда для запуска xray
    start_parser = subparsers.add_parser('start', help='Запуск xray с указанным конфигом')
    start_parser.add_argument('--config', type=str, default='config.json', help='Путь к файлу конфигурации')
    start_parser.add_argument('--detach', action='store_true', help='Запуск в фоновом режиме')

    # Команда для остановки xray
    stop_parser = subparsers.add_parser('stop', help='Остановка xray')

    # Команда для добавления пользователя
    add_user_parser = subparsers.add_parser('add-user', help='Добавление пользователя в конфигурацию')
    add_user_parser.add_argument('--name', type=str, required=True, help='Имя пользователя')
    add_user_parser.add_argument('--config', type=str, default='config.json', help='Путь к файлу конфигурации')

    # Команда для удаления пользователя
    remove_user_parser = subparsers.add_parser('remove-user', help='Удаление пользователя из конфигурации')
    remove_user_parser.add_argument('--name', type=str, required=True, help='Имя пользователя')
    remove_user_parser.add_argument('--config', type=str, default='config.json', help='Путь к файлу конфигурации')

    # Команда для получения QR-кода
    qr_parser = subparsers.add_parser('qr', help='Получение QR-кода с конфигурацией для клиента')
    qr_parser.add_argument('--name', type=str, required=True, help='Имя пользователя')
    qr_parser.add_argument('--config', type=str, default='config.json', help='Путь к файлу конфигурации')
    qr_parser.add_argument('--save', type=str, help='Путь для сохранения QR-кода')

    # Команда для получения JSON-конфигурации пользователя
    get_config_parser = subparsers.add_parser('get-config', help='Получение JSON-конфигурации для клиента')
    get_config_parser.add_argument('--name', type=str, required=True, help='Имя пользователя')
    get_config_parser.add_argument('--config', type=str, default='config.json', help='Путь к файлу конфигурации')
    get_config_parser.add_argument('--save', type=str, help='Путь для сохранения JSON-конфигурации в файл')

    # Команда для генерации ключей
    keys_parser = subparsers.add_parser('gen-keys', help='Генерация ключей для Reality')
    keys_parser.add_argument('--save-to-config', type=str, help='Сохранить ключи в указанный файл конфигурации')

    # Команда для просмотра всех пользователей
    list_users_parser = subparsers.add_parser('list-users', help='Список всех пользователей')
    list_users_parser.add_argument('--config', type=str, default='config.json', help='Путь к файлу конфигурации')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    config_manager = ConfigManager()
    user_manager = UserManager(config_manager)
    docker_manager = DockerManager()

    if args.command == 'config':
        # Проверяем, существует ли файл конфигурации
        try:
            config_manager.load_config(args.save)
            print(f"Найдена существующая конфигурация в {args.save}, обновляю указанные параметры")
        except:
            print(f"Создаю новую конфигурацию в {args.save}")

        # Проверяем наличие обязательных параметров при создании новой конфигурации
        if not config_manager.has_reality_settings() and not all([args.dest, args.server_names]):
            print("Ошибка: при создании новой конфигурации требуются параметры --dest и --server-names")
            return

        # Обновляем параметры
        if args.dest:
            config_manager.update_dest(args.dest)
            print(f"Обновлен dest: {args.dest}")

        if args.server_names:
            config_manager.update_server_names(args.server_names)
            print(f"Обновлены server_names: {', '.join(args.server_names)}")

        if args.port:
            config_manager.update_port(args.port)
            print(f"Обновлен порт: {args.port}")

        # Если конфигурация новая, генерируем ключи
        if not config_manager.has_reality_settings():
            private_key, public_key = config_manager.generate_keys()
            short_id = config_manager.generate_short_id()
            config_manager.update_keys(private_key, public_key, short_id)
            print("Сгенерированы новые ключи и short_id")

        config_manager.save_config(args.save)
        print(f"Конфигурация сохранена в {args.save}")

    elif args.command == 'start':
        docker_manager.start_xray(args.config, args.detach)
        print("Xray запущен")

    elif args.command == 'stop':
        docker_manager.stop_xray()
        print("Xray остановлен")

    elif args.command == 'add-user':
        config_manager.load_config(args.config)
        user_id = user_manager.add_user(args.name)
        config_manager.save_config(args.config)
        print(f"Пользователь {args.name} добавлен с ID: {user_id}")

    elif args.command == 'remove-user':
        config_manager.load_config(args.config)
        user_manager.remove_user(args.name)
        config_manager.save_config(args.config)
        print(f"Пользователь {args.name} удален")

    elif args.command == 'qr':
        config_manager.load_config(args.config)
        user_manager.generate_qr_code(args.name, args.save)
        if args.save:
            print(f"QR-код сохранен в {args.save}")

    elif args.command == 'get-config':
        config_manager.load_config(args.config)
        client_config = user_manager.generate_client_config(args.name)
        if client_config:
            if args.save:
                # Сохранение конфигурации в файл
                with open(args.save, 'w') as f:
                    json.dump(client_config, f, indent=2)
                print(f"Конфигурация сохранена в {args.save}")
            else:
                # Вывод конфигурации в терминал
                print(json.dumps(client_config, indent=2))

    elif args.command == 'gen-keys':
        private_key, public_key = config_manager.generate_keys()
        print(f"Приватный ключ: {private_key}")
        print(f"Публичный ключ: {public_key}")

        if args.save_to_config:
            config_manager.load_config(args.save_to_config)
            inbound = config_manager.get_inbound()
            reality_settings = inbound["streamSettings"]["realitySettings"]
            reality_settings["privateKey"] = private_key

            # Обновление публичного ключа в метаданных для клиентов
            server_info = config_manager.get_server_info()
            server_info["publicKey"] = public_key

            config_manager.save_config(args.save_to_config)
            print(f"Ключи сохранены в конфигурации {args.save_to_config}")

    elif args.command == 'list-users':
        config_manager.load_config(args.config)
        users = user_manager.list_users()
        if users:
            print("Список пользователей:")
            for idx, user in enumerate(users, 1):
                print(f"{idx}. {user['name']} (ID: {user['id']})")
        else:
            print("Пользователи не найдены")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
