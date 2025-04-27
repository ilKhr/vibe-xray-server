#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import json

class DockerManager:
    """Класс для управления Docker-контейнером с Xray"""

    def __init__(self):
        self.container_name = "xray-reality-container"
        self.image_name = "ghcr.io/xtls/xray-core:latest"

    def _check_docker(self):
        """Проверка доступности Docker"""
        try:
            subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Docker не установлен или недоступен")
            return False

    def _check_container_exists(self):
        """Проверка, существует ли контейнер"""
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
            return self.container_name in result.stdout.split()
        except subprocess.SubprocessError:
            return False

    def _check_container_running(self):
        """Проверка, запущен ли контейнер"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
            return self.container_name in result.stdout.split()
        except subprocess.SubprocessError:
            return False

    def _prepare_config_dir(self, config_path):
        """Подготовка директории для монтирования конфига"""
        config_dir = os.path.dirname(os.path.abspath(config_path))
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return config_dir

    def start_xray(self, config_path, detach=False):
        """Запуск Xray в Docker-контейнере"""
        if not self._check_docker():
            return False

        # Остановить и удалить существующий контейнер, если он есть
        if self._check_container_exists():
            self.stop_xray()

        # Подготовить директорию для конфига
        config_dir = self._prepare_config_dir(config_path)
        config_file = os.path.basename(config_path)

        # Запустить контейнер
        cmd = [
            "docker", "run",
            "--name", self.container_name,
            "-v", f"{config_dir}:/etc/xray",
            "-p", "443:443/tcp",  # Предполагаем, что используется порт 443
            "--restart", "unless-stopped"
        ]

        if detach:
            cmd.append("-d")

        cmd.extend([
            self.image_name,
            "run", "-c", f"/etc/xray/{config_file}"
        ])

        try:
            if detach:
                subprocess.run(cmd, check=True)
                print(f"Xray запущен в фоновом режиме в контейнере {self.container_name}")
            else:
                # Запуск в текущем терминале
                subprocess.Popen(cmd)
                print(f"Xray запущен в контейнере {self.container_name}")
            return True
        except subprocess.SubprocessError as e:
            print(f"Ошибка при запуске контейнера: {e}")
            return False

    def stop_xray(self):
        """Остановка и удаление контейнера Xray"""
        if not self._check_docker():
            return False

        if not self._check_container_exists():
            print("Контейнер не существует")
            return True

        try:
            # Остановить контейнер, если он запущен
            if self._check_container_running():
                subprocess.run(
                    ["docker", "stop", self.container_name],
                    check=True
                )

            # Удалить контейнер
            subprocess.run(
                ["docker", "rm", self.container_name],
                check=True
            )

            print(f"Контейнер {self.container_name} остановлен и удален")
            return True
        except subprocess.SubprocessError as e:
            print(f"Ошибка при остановке контейнера: {e}")
            return False

    def get_container_logs(self, tail=100):
        """Получение логов контейнера"""
        if not self._check_docker():
            return None

        if not self._check_container_exists():
            print("Контейнер не существует")
            return None

        try:
            result = subprocess.run(
                ["docker", "logs", f"--tail={tail}", self.container_name],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.SubprocessError as e:
            print(f"Ошибка при получении логов: {e}")
            return None

    def restart_xray(self):
        """Перезапуск контейнера Xray"""
        if not self._check_docker():
            return False

        if not self._check_container_exists():
            print("Контейнер не существует, нечего перезапускать")
            return False

        try:
            subprocess.run(
                ["docker", "restart", self.container_name],
                check=True
            )
            print(f"Контейнер {self.container_name} перезапущен")
            return True
        except subprocess.SubprocessError as e:
            print(f"Ошибка при перезапуске контейнера: {e}")
            return False
