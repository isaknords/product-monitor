import time

import requests


COMING_SOON_CACHE_TIME = 300
PREORDER_CACHE_TIME = 60


def get_product_status(
    product,
    session,
    cached_status=None,
    last_checked=0,
    product_url=None
):
    tags = product.get("tags", [])

    if any(
        variant["available"]
        for variant in product["variants"]
    ):
        return "IN_STOCK", int(time.time())

    if "preorder" not in tags:
        return "SOLD_OUT", int(time.time())

    now = int(time.time())

    if cached_status is not None:
        if cached_status == "COMING_SOON":
            cache_time = COMING_SOON_CACHE_TIME

        elif cached_status == "PREORDER":
            cache_time = PREORDER_CACHE_TIME

        else:
            cache_time = 0

        if now - last_checked < cache_time:
            return cached_status, last_checked

    if product_url is None:
        return "COMING_SOON", now

    print(
        f"Checking preorder page: "
        f"{product['title']}"
    )

    try:
        response = session.get(
            product_url,
            timeout=10
        )
        response.raise_for_status()

        page = response.text.lower()

        if "coming soon" in page or "kommer snart" in page:
            return "COMING_SOON", now

        return "PREORDER", now

    except requests.RequestException as error:
        print(
            f"Could not check preorder page: "
            f"{product['title']}"
        )
        print(error)

        return "COMING_SOON", now