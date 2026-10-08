import requests

from status_detector import get_product_status


session = requests.Session()


def get_products(collection_url, previous_products=None):
    if previous_products is None:
        previous_products = {}

    url = f"{collection_url}/products.json?limit=250"

    response = session.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    products = {}

    base_url = collection_url.split("/collections/")[0]

    for product in data["products"]:
        product_id = str(product["id"])

        previous_product = previous_products.get(
            product_id,
            {}
        )

        cached_status = previous_product.get("status")
        last_checked = previous_product.get("last_checked", 0)

        product_url = (
            f"{base_url}/products/{product['handle']}"
        )

        status, checked_at = get_product_status(
            product,
            session,
            cached_status,
            last_checked,
            product_url
        )

        variants = {}
        available_variants = []

        for variant in product["variants"]:
            variant_id = str(variant["id"])

            variants[variant_id] = {
                "title": variant["title"],
                "available": variant["available"],
                "price": variant["price"],
            }

            if variant["available"]:
                available_variants.append({
                    "title": variant["title"],
                    "price": variant["price"],
                })

        if available_variants:
            price = available_variants[0]["price"]

        elif product["variants"]:
            price = product["variants"][0]["price"]

        else:
            price = None

        products[product_id] = {
            "title": product["title"],
            "status": status,
            "price": price,
            "available_variants": available_variants,
            "variants": variants,
            "handle": product["handle"],
            "url": product_url,
            "last_checked": checked_at,
        }

    return products