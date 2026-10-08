import time

from monitor import check_all_collections


CHECK_INTERVAL = 60


def main():
    while True:
        try:
            check_all_collections()

        except Exception as error:
            print(f"UNEXPECTED ERROR: {error}")

        print(
            f"Waiting {CHECK_INTERVAL} seconds...\n"
        )

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()