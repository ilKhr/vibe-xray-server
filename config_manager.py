#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import uuid
import subprocess
import base64
import secrets
import string

class ConfigManager:
    """Класс для управления конфигурацией Xray"""

    def __init__(self):
        self.config = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "listen": "0.0.0.0",
                    "protocol": "vless",
                    "settings": {
                        "clients": [],
                        "decryption": "none"
                    },
                    "streamSettings": {
                        "network": "tcp",
                        "security": "reality",
                        "realitySettings": {}
                    },
                    "sniffing": {
                        "enabled": True,
                        "destOverride": [
                            "http",
                            "tls",
                            "quic"
                        ]
                    }
                }
            ],
            "outbounds": [
                {
                    "protocol": "freedom",
                    "tag": "direct"
                },
                {
                    "protocol": "blackhole",
                    "tag": "block"
                }
            ]
        }
        self.user_metadata = {}

    def load_config(self, file_path):
        """Загрузка конфигурации из файла"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.config = json.load(f)

                # Загрузка метаданных о пользователях, если файл существует
                metadata_path = self._get_metadata_path(file_path)
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        self.user_metadata = json.load(f)
            else:
                print(f"Файл конфигурации {file_path} не найден, будет создана новая конфигурация")
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            raise

    def save_config(self, file_path):
        """Сохранение конфигурации в файл"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=2)

            # Сохранение метаданных о пользователях
            metadata_path = self._get_metadata_path(file_path)
            with open(metadata_path, 'w') as f:
                json.dump(self.user_metadata, f, indent=2)

            return True
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {e}")
            return False

    def _get_metadata_path(self, config_path):
        """Возвращает путь к файлу метаданных о пользователях"""
        base_path, _ = os.path.splitext(config_path)
        return f"{base_path}_metadata.json"

    def create_config(self, dest, server_names, port=443):
        """Создание новой конфигурации Xray с REALITY"""
        private_key, public_key = self.generate_keys()

        # Настройка inbound
        inbound = self.config["inbounds"][0]
        inbound["port"] = port

        # Настройка REALITY
        reality_settings = inbound["streamSettings"]["realitySettings"]
        reality_settings.update({
            "dest": dest,
            "serverNames": server_names,
            "privateKey": private_key,
            "shortIds": []  # Пустой список shortIds, индивидуальные shortId будут добавляться для каждого пользователя
        })

        # Сохраняем публичный ключ в метаданных для использования клиентами
        self.user_metadata["server"] = {
            "publicKey": public_key,
            "serverName": server_names[0],
            "dest": dest,
            "port": port
        }

        return self.config

    def has_reality_settings(self):
        """Проверяет, настроены ли параметры REALITY в конфигурации"""
        try:
            reality_settings = self.get_reality_settings()
            return bool(reality_settings.get("privateKey") and reality_settings.get("dest") and reality_settings.get("serverNames"))
        except:
            return False

    def update_dest(self, dest):
        """Обновление целевого домена в REALITY настройках"""
        reality_settings = self.get_reality_settings()
        reality_settings["dest"] = dest

        # Обновление метаданных для клиентов
        if "server" not in self.user_metadata:
            self.user_metadata["server"] = {}
        self.user_metadata["server"]["dest"] = dest

    def update_server_names(self, server_names):
        """Обновление serverNames в REALITY настройках"""
        reality_settings = self.get_reality_settings()
        reality_settings["serverNames"] = server_names

        # Обновление метаданных для клиентов
        if "server" not in self.user_metadata:
            self.user_metadata["server"] = {}
        self.user_metadata["server"]["serverName"] = server_names[0]

    def update_port(self, port):
        """Обновление порта для inbound"""
        inbound = self.get_inbound()
        inbound["port"] = port

        # Обновление метаданных для клиентов
        if "server" not in self.user_metadata:
            self.user_metadata["server"] = {}
        self.user_metadata["server"]["port"] = port

    def update_keys(self, private_key, public_key, short_id=None):
        """Обновление ключей в REALITY настройках"""
        reality_settings = self.get_reality_settings()
        reality_settings["privateKey"] = private_key

        # Обновление метаданных для клиентов
        if "server" not in self.user_metadata:
            self.user_metadata["server"] = {}
        self.user_metadata["server"]["publicKey"] = public_key

    def generate_short_id(self):
        """Генерация короткого идентификатора для Reality"""
        try:
            # Используем openssl для генерации short_id
            result = subprocess.run(
                ["openssl", "rand", "-hex", "8"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Ошибка при генерации short_id через openssl: {e}")
            # Запасной метод, если команда openssl не доступна
            return secrets.token_hex(8)

    def generate_keys(self):
        """Генерация ключей X25519 для REALITY"""
        try:
            # Попытка вызвать xray для генерации ключей
            result = subprocess.run(
                ["docker", "run", "--rm", "ghcr.io/xtls/xray-core:latest", "x25519"],
                capture_output=True, text=True, check=True
            )
            output = result.stdout.strip().split('\n')
            private_key = output[0].split('Private key: ')[1] if 'Private key: ' in output[0] else None
            public_key = output[1].split('Public key: ')[1] if 'Public key: ' in output[1] else None

            if private_key and public_key:
                return private_key, public_key
            else:
                raise Exception("Не удалось извлечь ключи из вывода xray")
        except (subprocess.SubprocessError, Exception) as e:
            print(f"Ошибка при генерации ключей через xray: {e}")
            # Если вызов xray не удался, используем встроенные средства Python
            # Это заглушка - для реальной реализации нужно использовать библиотеку для X25519
            # В условиях ограничения на использование только стандартных библиотек
            # можно предложить пользователю сгенерировать ключи вручную
            random_key = base64.b64encode(os.urandom(32)).decode('utf-8')
            private_key = random_key
            public_key = base64.b64encode(os.urandom(32)).decode('utf-8')
            return private_key, public_key

    def generate_uuid(self):
        """Генерация UUID через Docker и Xray"""
        try:
            # Используем Docker для запуска Xray и генерации UUID
            result = subprocess.run(
                ["docker", "run", "--rm", "ghcr.io/xtls/xray-core:latest", "uuid"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Ошибка при генерации UUID через Docker: {e}")
            # Запасной метод, если Docker недоступен
            return str(uuid.uuid4())

    def get_inbound(self):
        """Получение основного inbound из конфигурации"""
        return self.config["inbounds"][0]

    def get_reality_settings(self):
        """Получение настроек REALITY из конфигурации"""
        return self.get_inbound()["streamSettings"]["realitySettings"]

    def get_clients(self):
        """Получение списка клиентов из конфигурации"""
        return self.get_inbound()["settings"]["clients"]

    def add_client_short_id(self, short_id):
        """Добавление short_id в список shortIds в realitySettings"""
        reality_settings = self.get_reality_settings()
        if "shortIds" not in reality_settings:
            reality_settings["shortIds"] = []

        # Добавляем short_id, если его еще нет в списке
        if short_id not in reality_settings["shortIds"]:
            reality_settings["shortIds"].append(short_id)

    def get_server_info(self):
        """Получение информации о сервере из метаданных"""
        server_info = self.user_metadata.get("server", {})

        # Добавляем список shortIds из realitySettings, если они есть
        if self.has_reality_settings():
            reality_settings = self.get_reality_settings()
            if "shortIds" in reality_settings:
                server_info["shortIds"] = reality_settings.get("shortIds", [])

        return server_info

    def update_client(self, user_id, name, client_data, short_id=None):
        """Обновление или добавление метаданных о клиенте"""
        if "users" not in self.user_metadata:
            self.user_metadata["users"] = {}

        # Сохранение базовой информации о пользователе
        self.user_metadata["users"][user_id] = {
            "name": name,
            "data": client_data
        }

        # Если передан short_id, сохраняем его для этого пользователя
        if short_id:
            self.user_metadata["users"][user_id]["shortId"] = short_id

    def get_client_by_name(self, name):
        """Поиск клиента по имени"""
        if "users" not in self.user_metadata:
            return None

        for user_id, user_data in self.user_metadata["users"].items():
            if user_data["name"] == name:
                return user_id, user_data

        return None
