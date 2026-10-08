import requests
from config import DISCORD_WEBHOOK_URL


def send_stock_alert(
    store,
    product,
    price,
    status,
    url,
    available_variants=None
):

    message = (
        "PRODUCT STOCK ALERT\n\n"
        f"{product}\n\n"
        f"Store: {store}\n"
    )

    if available_variants:

        message += "\nAvailable variants:\n"

        for variant in available_variants:

            message += (
                f"- {variant['title']} — "
                f"{variant['price']} SEK\n"
            )

    else:

        message += f"Price: {price} SEK\n"

    message += (
        f"\nStatus: {status}\n\n"
        f"{url}"
    )

    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message}
    )

    if response.status_code != 204:

        print(f"Discord error: {response.status_code}")
        print(response.text)

    else:

        print("Stock alert sent successfully")