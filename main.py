#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
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

    # Команда для генерации ключей
    keys_parser = subparsers.add_parser('gen-keys', help='Генерация ключей для Reality')

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
        if not all([args.dest, args.server_names]):
            print("Ошибка: требуются параметры --dest и --server-names")
            return
        config_manager.create_config(
            dest=args.dest,
            server_names=args.server_names,
            port=args.port
        )
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

    elif args.command == 'gen-keys':
        private_key, public_key = config_manager.generate_keys()
        print(f"Приватный ключ: {private_key}")
        print(f"Публичный ключ: {public_key}")

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
