#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import qrcode
import base64
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime

class UserManager:
    """Класс для управления пользователями в конфигурации Xray"""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def add_user(self, name):
        """Добавление нового пользователя в конфигурацию"""
        # Проверка, существует ли пользователь с таким именем
        existing_user = self.config_manager.get_client_by_name(name)
        if existing_user:
            print(f"Пользователь с именем {name} уже существует")
            return existing_user[0]  # Вернуть ID существующего пользователя

        # Генерация UUID для нового пользователя
        user_id = self.config_manager.generate_uuid()

        # Добавление пользователя в конфигурацию
        clients = self.config_manager.get_clients()
        client_data = {
            "id": user_id,
            "flow": "xtls-rprx-vision"
        }
        clients.append(client_data)

        # Сохранение метаданных о пользователе
        self.config_manager.update_client(user_id, name, client_data)

        return user_id

    def remove_user(self, name):
        """Удаление пользователя из конфигурации"""
        # Поиск пользователя по имени
        user_info = self.config_manager.get_client_by_name(name)
        if not user_info:
            print(f"Пользователь с именем {name} не найден")
            return False

        user_id, _ = user_info

        # Удаление пользователя из списка клиентов
        clients = self.config_manager.get_clients()
        for i, client in enumerate(clients):
            if client["id"] == user_id:
                clients.pop(i)
                break

        # Удаление метаданных о пользователе
        if "users" in self.config_manager.user_metadata:
            if user_id in self.config_manager.user_metadata["users"]:
                del self.config_manager.user_metadata["users"][user_id]

        return True

    def list_users(self):
        """Получение списка всех пользователей"""
        users = []
        if "users" in self.config_manager.user_metadata:
            for user_id, user_data in self.config_manager.user_metadata["users"].items():
                users.append({
                    "id": user_id,
                    "name": user_data["name"]
                })
        return users

    def get_external_ip(self):
        """Определение внешнего IP-адреса сервера"""
        try:
            # Используем сервис ipify для определения внешнего IP-адреса
            with urllib.request.urlopen('https://api.ipify.org') as response:
                ip = response.read().decode('utf-8')
                return ip
        except Exception as e:
            print(f"Ошибка при определении внешнего IP-адреса: {e}")
            # Пробуем альтернативный сервис, если первый не сработал
            try:
                with urllib.request.urlopen('https://ifconfig.me/ip') as response:
                    ip = response.read().decode('utf-8')
                    return ip
            except Exception as e:
                print(f"Ошибка при определении внешнего IP-адреса: {e}")
                return ""

    def generate_client_config(self, name):
        """Генерация конфигурации для клиента"""
        # Поиск пользователя по имени
        user_info = self.config_manager.get_client_by_name(name)
        if not user_info:
            print(f"Пользователь с именем {name} не найден")
            return None

        user_id, user_data = user_info
        server_info = self.config_manager.get_server_info()

        if not server_info:
            print("Ошибка: информация о сервере не найдена")
            return None

        # Создание конфигурации для клиента
        client_config = {
            "log": {
                "loglevel": "warning"
            },
            "routing": {
                "rules": [
                    {
                        "ip": [
                            "geoip:private"
                        ],
                        "outboundTag": "direct"
                    }
                ]
            },
            "inbounds": [
                {
                    "listen": "127.0.0.1",
                    "port": 10808,
                    "protocol": "socks"
                },
                {
                    "listen": "127.0.0.1",
                    "port": 10809,
                    "protocol": "http"
                }
            ],
            "outbounds": [
                {
                    "protocol": "vless",
                    "settings": {
                        "vnext": [
                            {
                                "address": "",  # IP-адрес сервера заполняется клиентом
                                "port": server_info["port"],
                                "users": [
                                    {
                                        "id": user_id,
                                        "encryption": "none",
                                        "flow": "xtls-rprx-vision"
                                    }
                                ]
                            }
                        ]
                    },
                    "streamSettings": {
                        "network": "tcp",
                        "security": "reality",
                        "realitySettings": {
                            "fingerprint": "chrome",
                            "serverName": server_info["serverName"],
                            "publicKey": server_info["publicKey"],
                            "shortId": server_info["shortId"]
                        }
                    },
                    "tag": "proxy"
                },
                {
                    "protocol": "freedom",
                    "tag": "direct"
                }
            ]
        }

        return client_config

    def generate_vless_link(self, name, server_address=""):
        """Генерация URI-ссылки VLESS для быстрой настройки клиента"""
        # Поиск пользователя по имени
        user_info = self.config_manager.get_client_by_name(name)
        if not user_info:
            print(f"Пользователь с именем {name} не найден")
            return None

        user_id, user_data = user_info
        server_info = self.config_manager.get_server_info()

        if not server_info:
            print("Ошибка: информация о сервере не найдена")
            return None

        # Если сервер не указан, пытаемся определить его автоматически
        if not server_address:
            server_address = self.get_external_ip()
            if server_address:
                print(f"Автоматически определен IP-адрес сервера: {server_address}")
            else:
                print("Не удалось автоматически определить IP-адрес сервера. Указывайте адрес вручную с помощью параметра --server")

        # Формирование параметров для ссылки
        params = {
            "flow": "xtls-rprx-vision",
            "type": "tcp",
            "security": "reality",
            "sni": server_info["serverName"],
            "pbk": server_info["publicKey"],
            "sid": server_info["shortId"],
            "spx": "/"  # Путь по умолчанию
        }

        # Кодирование параметров для URL
        query_string = "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in params.items()])

        # Формирование ссылки
        vless_link = f"vless://{user_id}@{server_address}:{server_info['port']}?{query_string}#{urllib.parse.quote(name)}"

        return vless_link

    def generate_vless_qr(self, name, server_address="", save_path=None):
        """Генерация QR-кода на основе VLESS URI-ссылки"""
        # Получаем VLESS-ссылку
        vless_link = self.generate_vless_link(name, server_address)
        if not vless_link:
            return False

        # Создание QR-кода
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(vless_link)
        qr.make(fit=True)

        # Обработка в зависимости от наличия save_path
        if save_path:
            # Создание изображения QR-кода и сохранение в файл
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(save_path)
            print(f"QR-код с VLESS-ссылкой сохранен в {save_path}")
        else:
            # Отображение QR-кода прямо в терминале
            print("\nQR-код для VLESS URI-ссылки:")
            qr.print_ascii(invert=True)
            print("\nVLESS URI-ссылка:")
            print(vless_link)

        return True

    def generate_qr_code(self, name, save_path=None):
        """Генерация QR-кода с конфигурацией для клиента"""
        client_config = self.generate_client_config(name)
        if not client_config:
            return False

        # Преобразование конфигурации в JSON-строку
        config_json = json.dumps(client_config)

        # Создание QR-кода
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(config_json)
        qr.make(fit=True)

        # Обработка в зависимости от наличия save_path
        if save_path:
            # Создание изображения QR-кода и сохранение в файл
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(save_path)
            print(f"QR-код с конфигурацией сохранен в {save_path}")
        else:
            # Отображение QR-кода прямо в терминале
            print("\nQR-код для конфигурации клиента:")
            qr.print_ascii(invert=True)
            print("\nКонфигурация для клиента (JSON):")
            print(json.dumps(client_config, indent=2))

        return True
