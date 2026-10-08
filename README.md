# Product Monitor

A Python-based product monitoring tool that periodically checks online stores for new products and changes in stock status.

The monitor can detect new products, stock changes, variant-level restocks, preorders and upcoming products, and sends notifications through Discord when relevant changes are detected.

## Features

* Periodically monitors product collections
* Detects new products and changes in availability
* Tracks individual product variants
* Detects variant-level restocks
* Supports preorder and "coming soon" detection for supported store structures
* Stores previous product states in a JSON file
* Sends Discord notifications for relevant changes
* Supports different monitoring strategies for different store structures
* Uses concurrent requests when checking products

## Technologies

* Python
* Requests
* JSON
* HTML parsing
* Regular expressions
* ThreadPoolExecutor
* Discord Webhooks

## Project Structure

```text
main.py                  # Starts the monitoring loop
monitor.py               # Coordinates monitoring and state changes
shopify_monitor.py       # Monitoring strategy for Shopify stores
custom_monitor.py        # Custom HTML/JavaScript-based monitoring
status_detector.py       # Determines product availability and preorder status
discord_notifier.py      # Sends Discord notifications
config.py                # Store and monitoring configuration
requirements.txt         # Python dependencies
```

## How It Works

The application periodically scans configured product collections.

For each product, the monitor compares the current state with the state from the previous scan. Changes such as new products, stock changes or variant restocks can trigger a Discord notification.

The previous state is stored locally in `stock_state.json`, allowing the application to detect changes between scans.

Different monitoring strategies can be selected through the store configuration, allowing the application to work with different website structures.

## Configuration

Store monitoring is configured in `config.py`.

The public version of this repository uses placeholder URLs and a placeholder Discord webhook. Real store URLs and credentials are not included.

To use the monitor with a real store, replace the example configuration with the appropriate store URL and Discord webhook.

## Setup

Clone the repository and install the required dependency:

```bash
pip install -r requirements.txt
```

Update `config.py` with the store configuration and Discord webhook, then run:

```bash
python main.py
```

The monitor will continue running and perform scans at the configured interval.

The example configuration included in this repository uses placeholder URLs and is intended to demonstrate the project structure rather than provide a ready-to-run store configuration.

## Disclaimer

This repository is a cleaned and anonymised version of a personal project. Store-specific URLs, credentials and other private configuration have been removed.
