from src.main.ui.steps.catalog_steps import CatalogSteps
from src.main.ui.utils.constants import SortOption, Users


def test_count_catalog(page):
    steps = CatalogSteps(page)
    steps.login(*Users.STANDARD)
    assert steps.get_products_count() == 6


def test_sorted_by_name(page):
    steps = CatalogSteps(page)
    steps.login(*Users.STANDARD)

    steps.sort_items(SortOption.NAME_ASC)
    assert steps.get_product_names() == sorted(steps.get_product_names())

    steps.sort_items(SortOption.NAME_DESC)
    assert steps.get_product_names() == sorted(steps.get_product_names(), reverse=True)


def test_sort_by_price(page):
    steps = CatalogSteps(page)
    steps.login(*Users.STANDARD)

    steps.sort_items(SortOption.PRICE_ASC)
    assert steps.get_product_prices() == sorted(steps.get_product_prices())

    steps.sort_items(SortOption.PRICE_DESC)
    assert steps.get_product_prices() == sorted(steps.get_product_prices(), reverse=True)


def test_add_to_cart(page):
    steps = CatalogSteps(page)
    steps.login(*Users.STANDARD)

    steps.add_to_cart("Sauce Labs Bike Light")
    assert steps.get_cart_count() == 1


def test_add_and_remove_onesie(page):
    steps = CatalogSteps(page)
    steps.login(*Users.STANDARD)

    steps.add_to_cart("Sauce Labs Onesie")
    assert steps.get_cart_count() == 1

    steps.remove_from_cart("Sauce Labs Onesie")
    assert steps.get_cart_count() == 0


def test_product_details_onesie(page):
    steps = CatalogSteps(page)
    steps.login(*Users.STANDARD)

    name, price, detail_name, detail_price = steps.open_product_details("Sauce Labs Onesie")
    assert name == detail_name
    assert price == detail_price


def test_product_details_fleece_jacket(page):
    steps = CatalogSteps(page)
    steps.login(*Users.STANDARD)

    name, price, detail_name, detail_price = steps.open_product_details("Sauce Labs Fleece Jacket")
    assert name == detail_name
    assert price == detail_price


def test_remove_item_from_catalog(page):
    steps = CatalogSteps(page)
    steps.login(*Users.STANDARD)

    steps.remove_from_cart("Test.allTheThings() T-Shirt (Red)")
    assert steps.get_cart_count() == 0, "Ожидаем, что корзина остаётся пустой после снятия товара"
