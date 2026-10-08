import html
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


BASE_URL = "https://example.com"
MAX_WORKERS = 8

session = requests.Session()


def get_product_data(product_url):
    response = session.get(product_url, timeout=10)
    response.raise_for_status()

    page = response.text

    match = re.search(
        r'data-product-id="([^"]+)".*?x-data="productData\((.*?)\)"',
        page,
        re.DOTALL
    )

    if not match:
        raise ValueError(
            f"Could not find product data on {product_url}"
        )

    product_data = match.group(2)

    available_match = re.search(
        r'available:\s*(true|false)',
        product_data
    )

    quantity_match = re.search(
        r"quantity:\s*'([^']*)'",
        product_data
    )

    price_match = re.search(
        r"price:\s*'([^']*)'",
        product_data
    )

    if not available_match:
        raise ValueError(
            f"Could not determine availability for {product_url}"
        )

    available = available_match.group(1) == "true"

    quantity = (
        quantity_match.group(1)
        if quantity_match
        else "0"
    )

    price = (
        price_match.group(1)
        if price_match
        else "Unknown"
    )

    preorder_match = re.search(
        r'preorder:\s*([0-9]+)',
        product_data
    )

    preorder_quantity = 0

    if preorder_match:
        preorder_quantity = int(
            preorder_match.group(1)
        )

    if available and preorder_quantity > 0:
        status = "PREORDER"

    elif available:
        status = "IN_STOCK"

    else:
        status = "SOLD_OUT"

    return {
        "status": status,
        "quantity": quantity,
        "price": price,
    }


def process_product(product_id, title, url):
    try:
        product_data = get_product_data(url)

        return product_id, {
            "title": title,
            "status": product_data["status"],
            "price": product_data["price"],
            "quantity": product_data["quantity"],
            "handle": url.rsplit("/", 1)[-1],
            "url": url,
            "available_variants": [],
            "last_checked": int(time.time()),
        }

    except Exception as error:
        print(f"Could not check product: {title}")
        print(error)

        return product_id, None


def get_products(category_url, previous_products=None):
    if previous_products is None:
        previous_products = {}

    response = session.get(
        category_url,
        timeout=10
    )
    response.raise_for_status()

    page = response.text
    products = {}

    matches = list(
        re.finditer(
            r'<div[^>]+data-qb-selector="product-item"'
            r'[^>]+data-product-id="([^"]+)"',
            page
        )
    )

    product_tasks = []

    for index, match in enumerate(matches):
        product_id = match.group(1)
        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(page)

        block = page[start:end]

        title_match = re.search(
            r'data-s-title="([^"]*)"',
            block
        )

        url_match = re.search(
            r'<a[^>]+href="([^"]+)"',
            block
        )

        if not title_match or not url_match:
            continue

        title = html.unescape(
            title_match.group(1)
        )

        url = url_match.group(1)

        if url.startswith("/"):
            url = BASE_URL + url

        product_tasks.append(
            (product_id, title, url)
        )

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [
            executor.submit(
                process_product,
                product_id,
                title,
                url
            )
            for product_id, title, url in product_tasks
        ]

        for future in as_completed(futures):
            product_id, product = future.result()

            if product is not None:
                products[product_id] = product

    return products