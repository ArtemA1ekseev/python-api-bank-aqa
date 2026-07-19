from dataclasses import dataclass

"""
контейнер-маркер
для этого конкретного поля используй не случайное число/строку, а сгенерируй значение по этому regex-шаблону
"""


@dataclass
class CreationRule:
    regex: str
