from typing import Any, List

from src.main.api.steps.admin_steps import AdminSteps
from src.main.api.steps.user_steps import UserSteps

"""Это класс-фасад (Facade pattern)"""
class ApiManager:
    def __init__(self, created_obj: List[Any]):
        self.admin_steps = AdminSteps(created_obj)
        self.user_steps = UserSteps(created_obj)