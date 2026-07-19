import pytest

from src.main.api.configs.classes.api_manager import ApiManager


"""
 Любой тест, который укажет api_manager как параметр, 
 получит готовый, полностью настроенный объект 
 ApiManager — со всеми его admin_steps/user_steps внутри, 
 без необходимости самому писать ApiManager(...) в каждом тесте.
"""
@pytest.fixture
def api_manager(created_obj):
    return ApiManager(created_obj)