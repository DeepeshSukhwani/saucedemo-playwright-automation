# RPA Take-Home Assignment

Python + Playwright automation for SauceDemo.

## Overview

This automation performs an end-to-end shopping workflow on SauceDemo.

It:

1. Logs in using credentials from environment variables.
2. Collects all available products.
3. Saves product name, description, and price to `products.json`.
4. Reads the shopping list and customer details from `input.json`.
5. Adds requested products to the cart.
6. Handles unavailable products without crashing.
7. Verifies the cart contents.
8. Completes the checkout process.
9. Reads the item total, tax, and final total.
10. Validates the item total against the collected product prices.
11. Fails the automation if the item total does not match the expected value.
12. Completes the order.
13. Saves an order confirmation screenshot.
14. Writes the final execution result to `result.json`.

## Technology

- Python 3
- Playwright
- JSON
- SauceDemo

## Project Structure

```text
saucedemo-playwright-automation/
├── test_playwright.py
├── input.json
├── products.json
├── result.json
├── order_confirmation.png
└── README.md
```

## Prerequisites

- Python 3
- Playwright
- Chromium browser

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install Playwright:

```bash
pip install playwright
```

Install the Chromium browser:

```bash
playwright install chromium
```

## Environment Variables

Credentials are not hardcoded in the Python source code.

Set the following environment variables:

```text
SAUCE_USERNAME=standard_user
SAUCE_PASSWORD=secret_sauce
```

The same automation also supports:

```text
SAUCE_USERNAME=performance_glitch_user
SAUCE_PASSWORD=secret_sauce
```

No Python code changes are required when switching users.

In IntelliJ, environment variables can be configured in:

```text
Run Configuration → Environment Variables
```

## Input

The automation reads `input.json` for the shopping list and customer details.

Example:

```json
{
  "items": [
    "Sauce Labs Backpack",
    "Sauce Labs Onesie",
    "Sauce Labs Water Bottle"
  ],
  "customer": {
    "first_name": "Ada",
    "last_name": "Lovelace",
    "zip": "94105"
  }
}
```

If a requested product is not available, the automation adds it to the `missing_items` list and continues processing the available products.

## Running the Automation

From the project directory:

```bash
python test_playwright.py
```

The browser runs in headed mode so the automation can be observed during execution.

## Output Files

### products.json

Contains all products collected from the inventory page.

Each product contains:

- `name`
- `description`
- `price`

Example:

```json
[
  {
    "name": "Sauce Labs Backpack",
    "description": "Product description",
    "price": 29.99
  }
]
```

### result.json

Contains the final execution result.

Successful execution example:

```json
{
  "status": "success",
  "item_total": 37.98,
  "tax": 3.04,
  "total": 41.02,
  "missing_items": [
    "Sauce Labs Water Bottle"
  ],
  "error": null
}
```

If the automation fails, the result contains:

```json
{
  "status": "failed",
  "item_total": null,
  "tax": null,
  "total": null,
  "missing_items": [],
  "error": "Error message"
}
```

### order_confirmation.png

Screenshot captured after the order is successfully completed.

## Error Handling

The automation uses `try/except/finally` to handle unexpected failures.

If an error occurs:

- The exception is captured.
- The status is set to `failed`.
- The error message is stored in `result.json`.
- `result.json` is generated even when the automation fails.

The automation also explicitly raises an error if the item total displayed by the application does not match the expected item total calculated from the collected product prices.

## Synchronization Strategy

The automation does not use fixed sleeps such as:

```python
time.sleep(5)
```

Instead, it uses Playwright state-based waits.

Examples:

```python
page.wait_for_url("**/inventory.html")
```

and:

```python
product_cards.first.wait_for(state="visible")
```

This approach makes the automation more reliable when the application responds slowly.

## Performance Glitch User

The automation was tested with both:

```text
standard_user
```

and:

```text
performance_glitch_user
```

The same Python code was used for both users.

Only the environment variable was changed:

```text
SAUCE_USERNAME=performance_glitch_user
```

The `performance_glitch_user` execution successfully completed:

- Login
- Product extraction
- Product file generation
- Cart processing
- Missing-item handling
- Checkout
- Customer details
- Item-total validation
- Tax and total extraction
- Order completion
- Confirmation screenshot
- Result generation

The execution completed with exit code `0`.

## Adapting the Solution to 40 Websites

For supporting approximately 40 websites, I would separate the common automation framework from website-specific logic.

### Common Framework

Reusable components could include:

- Browser management
- Configuration management
- Credential management
- Logging
- Error handling
- Screenshot handling
- Result reporting
- Synchronization/retry utilities
- Input and output models

### Website-Specific Layer

Each website would have its own adapter or Page Object implementation containing website-specific locators and actions.

For example:

```text
automation/
├── core/
│   ├── browser.py
│   ├── config.py
│   ├── logger.py
│   └── result.py
│
├── websites/
│   ├── saucedemo/
│   │   ├── login.py
│   │   ├── products.py
│   │   └── checkout.py
│   │
│   ├── website2/
│   ├── website3/
│   └── ...
│
└── main.py
```

The common workflow can remain reusable while each website implementation provides its own:

- Login locators
- Product locators
- Cart locators
- Checkout locators
- Total locators

This reduces code duplication and makes the automation easier to maintain when supporting many websites.

For 40 websites, I would also consider using configuration-driven selectors where practical and a Page Object Model or adapter pattern for website-specific behavior.

## Key Design Decisions

### Environment-Based Credentials

Credentials are supplied through environment variables instead of being hardcoded.

### State-Based Synchronization

The automation waits for application states instead of using fixed delays.

### Graceful Missing-Item Handling

Unavailable products are recorded in `missing_items` and do not stop the workflow.

### Data Validation

The expected item total is calculated from the collected product prices and compared against the application's displayed item total.

### Structured Result

`result.json` provides a machine-readable execution result that can be consumed by another automation system or CI/CD pipeline.

## Test Result

The automation was successfully tested with:

```text
standard_user
```

and:

```text
performance_glitch_user
```

Both executions completed successfully with:

```text
Process finished with exit code 0
```
