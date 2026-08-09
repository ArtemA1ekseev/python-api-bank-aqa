class Urls:
    BASE = "https://www.saucedemo.com/"
    INVENTORY = f"{BASE}inventory.html"
    CART = f"{BASE}cart.html"
    CHECKOUT = f"{BASE}checkout-step-one.html"


class Users:
    STANDARD = ("standard_user", "secret_sauce")
    LOCKED_OUT = ("locked_out_user", "secret_sauce")
    VISUAL = ("visual_user", "secret_sauce")


class SortOption:
    NAME_ASC = "az"
    NAME_DESC = "za"
    PRICE_ASC = "lohi"
    PRICE_DESC = "hilo"
