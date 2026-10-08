import json
from datetime import datetime

from shopify_monitor import get_products as get_shopify_products
from custom_monitor import get_products as get_custom_products

from discord_notifier import send_stock_alert
from config import STORES


STATE_FILE = "stock_state.json"


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_previous_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return {}

    except json.JSONDecodeError:
        print(
            f"[{get_timestamp()}] "
            "ERROR: stock_state.json is invalid."
        )
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            state,
            file,
            indent=4,
            ensure_ascii=False
        )


def get_products(store, collection, previous_state):
    monitor_type = store["monitor"]

    if monitor_type == "shopify":
        return get_shopify_products(
            collection["url"],
            previous_state
        )

    if monitor_type == "custom":
        return get_custom_products(
            collection["url"],
            previous_state
        )

    raise ValueError(
        f"Unknown monitor type: {monitor_type}"
    )


def check_collection(
    store_name,
    alert_new_products,
    store,
    collection,
    previous_state
):
    collection_name = collection["name"]
    collection_url = collection["url"]

    print(
        f"[{get_timestamp()}] "
        f"Scanning {store_name} / {collection_name}"
    )

    try:
        current_products = get_products(
            store,
            collection,
            previous_state.get(collection_name, {})
        )

    except Exception as error:
        print(
            f"[{get_timestamp()}] "
            f"ERROR while fetching {collection_name}:"
        )
        print(error)
        return None

    if not current_products:
        print(
            f"[{get_timestamp()}] "
            f"ERROR: No products returned for "
            f"{collection_name}."
        )
        print("State will NOT be updated.")
        return None

    print(
        f"[{get_timestamp()}] "
        f"{collection_name}: "
        f"{len(current_products)} products"
    )

    old_products = previous_state.get(
        collection_name,
        {}
    )

    for product_id, product in current_products.items():

        previous_product = old_products.get(
            str(product_id)
        )

        if previous_product is None:
            print(
                f"[{get_timestamp()}] "
                f"NEW PRODUCT: {product['title']}"
            )

            if (
                alert_new_products
                and product["status"] == "IN_STOCK"
            ):
                try:
                    send_stock_alert(
                        store=(
                            f"{store_name} / "
                            f"{collection_name}"
                        ),
                        product=product["title"],
                        price=f"{product['price']} SEK",
                        status="NEW PRODUCT / IN STOCK",
                        url=product["url"],
                        available_variants=(
                            product["available_variants"]
                        )
                    )

                except Exception as error:
                    print(
                        f"[{get_timestamp()}] "
                        "ERROR sending Discord alert:"
                    )
                    print(error)

            continue

        old_status = previous_product["status"]
        new_status = product["status"]

        if old_status != new_status:
            print(
                f"[{get_timestamp()}] STATUS CHANGE:\n"
                f"    {product['title']}\n"
                f"    {old_status} → {new_status}"
            )

            if new_status in ["PREORDER", "IN_STOCK"]:
                try:
                    send_stock_alert(
                        store=(
                            f"{store_name} / "
                            f"{collection_name}"
                        ),
                        product=product["title"],
                        price=f"{product['price']} SEK",
                        status=new_status,
                        url=product["url"],
                        available_variants=(
                            product["available_variants"]
                        )
                    )

                except Exception as error:
                    print(
                        f"[{get_timestamp()}] "
                        "ERROR sending Discord alert:"
                    )
                    print(error)

            continue

        old_variants = previous_product.get("variants")

        if old_variants is None:
            continue

        new_variants = product.get("variants", {})

        for variant_id, new_variant in new_variants.items():

            old_variant = old_variants.get(
                str(variant_id)
            )

            if old_variant is None:
                continue

            old_available = old_variant.get(
                "available",
                False
            )

            new_available = new_variant.get(
                "available",
                False
            )

            if not old_available and new_available:
                print(
                    f"[{get_timestamp()}] "
                    "VARIANT IN STOCK:\n"
                    f"    {product['title']}\n"
                    f"    {old_variant['title']} → IN STOCK"
                )

                try:
                    send_stock_alert(
                        store=(
                            f"{store_name} / "
                            f"{collection_name}"
                        ),
                        product=(
                            f"{product['title']} "
                            f"— {new_variant['title']}"
                        ),
                        price=f"{new_variant['price']} SEK",
                        status="VARIANT IN STOCK",
                        url=product["url"],
                        available_variants=[
                            {
                                "title": new_variant["title"],
                                "price": new_variant["price"],
                            }
                        ]
                    )

                except Exception as error:
                    print(
                        f"[{get_timestamp()}] "
                        "ERROR sending Discord alert:"
                    )
                    print(error)

    return current_products


def check_all_collections():
    print(
        f"\n[{get_timestamp()}] "
        "Scan started"
    )

    previous_state = load_previous_state()
    current_state = {}

    for store in STORES:
        store_name = store["name"]

        for collection in store["collections"]:
            collection_name = collection["name"]

            store_previous_state = previous_state.get(
                store_name,
                {}
            )

            products = check_collection(
                store_name,
                store["alert_new_products"],
                store,
                collection,
                store_previous_state
            )

            if products is not None:
                if store_name not in current_state:
                    current_state[store_name] = {}

                current_state[store_name][
                    collection_name
                ] = products

    if not current_state:
        print(
            f"[{get_timestamp()}] "
            "ERROR: No collections were successfully scanned."
        )
        print("State file will NOT be updated.")
        return

    try:
        save_state(current_state)

        print(
            f"[{get_timestamp()}] "
            "State saved."
        )

    except Exception as error:
        print(
            f"[{get_timestamp()}] "
            "ERROR saving state:"
        )
        print(error)

    print(
        f"[{get_timestamp()}] "
        "Scan completed"
    )