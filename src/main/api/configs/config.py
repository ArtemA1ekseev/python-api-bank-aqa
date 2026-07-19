from pathlib import Path
from typing import Any

"""
Singleton
У меня есть один класс, который один раз в начале программы читает файл
с настройками и хранит их в памяти — все остальные части кода спрашивают
у него нужные значения, вместо того чтобы читать файл заново каждый раз.
В программе всегда существует только один объект.
"""


class Config:
    _isinstance = None
    _dictionary = {}

    def __new__(cls):
        if cls._isinstance is None:
            cls._isinstance = super(Config, cls).__new__(cls)

            config_path = Path(__file__).parents[4] / 'resources' / 'urls.properties'

            if not config_path.exists():
                raise FileNotFoundError(f"Config path not found: {config_path}")

            with open(config_path, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.split("=")
                        cls._dictionary[key] = value.strip()

        return cls._isinstance

    @staticmethod
    def fetch(key: str, default_value: Any = None) -> Any:
        return Config()._dictionary.get(key, default_value)
