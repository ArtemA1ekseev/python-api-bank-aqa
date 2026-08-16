from src.main.ui.steps.catalog_steps import CatalogSteps
from src.main.ui.steps.login_steps import LoginSteps
from src.main.ui.utils.constants import Urls, Users


def test_auth(page):
    steps = LoginSteps(page)
    steps.open_login_page().login(*Users.STANDARD)
    assert page.url == Urls.INVENTORY, "Ожидаем переход на страницу каталога после успешного логина"


def test_login_locked_out_user(page):
    steps = LoginSteps(page)
    steps.open_login_page().login(*Users.LOCKED_OUT)
    assert page.url == Urls.BASE, "Ожидаем остаться на странице логина после блокировки"

    error_text = steps.get_error_text()
    assert "locked out" in error_text, "Ожидаем сообщение о заблокированном пользователе"


def test_logout(page):
    login = LoginSteps(page)
    catalog = CatalogSteps(page)

    login.open_login_page().login(*Users.STANDARD)
    assert catalog.get_products_count() > 0, "Ожидаем, что в каталоге есть товары"

    catalog.logout()
    assert page.url == Urls.BASE, "Ожидаем возврат на страницу логина"


def test_logout_visual_user(page):
    login = LoginSteps(page)
    catalog = CatalogSteps(page)

    login.open_login_page().login(*Users.VISUAL)
    assert catalog.get_products_count() > 0, "Ожидаем, что в каталоге есть товары"

    catalog.logout()
    assert page.url == Urls.BASE, "Ожидаем возврат на страницу логина"
