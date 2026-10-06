import json
import os

from playwright.sync_api import sync_playwright


result = {
    "status": "failed",
    "item_total": None,
    "tax": None,
    "total": None,
    "missing_items": [],
    "error": None
}

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Open SauceDemo
        page.goto("https://www.saucedemo.com")

        # Read credentials from environment variables
        username = os.getenv("SAUCE_USERNAME")
        password = os.getenv("SAUCE_PASSWORD")

        if not username or not password:
            raise ValueError(
                "SAUCE_USERNAME and SAUCE_PASSWORD environment variables are required"
            )

        # Login
        page.get_by_placeholder("Username").fill(username)
        page.get_by_placeholder("Password").fill(password)
        page.get_by_role("button", name="Login").click()

        page.wait_for_url("**/inventory.html")

        print("Logged in successfully")
        print("Current URL:", page.url)

        # Wait for products
        product_cards = page.locator('[data-test="inventory-item"]')
        product_cards.first.wait_for(state="visible")

        # Read input.json
        with open("input.json", "r", encoding="utf-8") as file:
            input_data = json.load(file)

        shopping_items = input_data["items"]
        customer = input_data["customer"]

        print("Shopping list:", shopping_items)
        print("Customer:", customer)

        # Collect all products
        products = []

        for i in range(product_cards.count()):
            card = product_cards.nth(i)

            name = card.locator(".inventory_item_name").inner_text()
            description = card.locator(".inventory_item_desc").inner_text()

            price_text = card.locator(".inventory_item_price").inner_text()
            price = float(price_text.replace("$", ""))

            products.append({
                "name": name,
                "description": description,
                "price": price
            })

        # Save products.json
        with open("products.json", "w", encoding="utf-8") as file:
            json.dump(products, file, indent=2)

        print(f"Saved {len(products)} products to products.json")

        # Add requested items to cart
        items_not_found = []

        for item_name in shopping_items:
            found = False

            for i in range(product_cards.count()):
                card = product_cards.nth(i)

                name = card.locator(
                    ".inventory_item_name"
                ).inner_text().strip()

                if name == item_name:
                    card.get_by_role(
                        "button",
                        name="Add to cart"
                    ).click()

                    print(f"Added to cart: {item_name}")

                    found = True
                    break

            if not found:
                items_not_found.append(item_name)
                print(f"Item not found: {item_name}")

        result["missing_items"] = items_not_found

        print("Missing items:", items_not_found)

        # Open cart
        page.locator('[data-test="shopping-cart-link"]').click()

        page.wait_for_url("**/cart.html")

        print("Opened cart successfully")

        # Verify cart items
        cart_items = page.locator(".cart_item")

        print("Items currently in cart:", cart_items.count())

        for i in range(cart_items.count()):
            cart_item = cart_items.nth(i)

            cart_item_name = cart_item.locator(
                ".inventory_item_name"
            ).inner_text()

            print("Cart item:", cart_item_name)

        print("Cart verification completed")

        # Start checkout
        page.get_by_role("button", name="Checkout").click()

        page.wait_for_url("**/checkout-step-one.html")

        print("Checkout page opened")

        # Fill customer details
        page.get_by_placeholder("First Name").fill(
            customer["first_name"]
        )

        page.get_by_placeholder("Last Name").fill(
            customer["last_name"]
        )

        page.get_by_placeholder("Zip/Postal Code").fill(
            customer["zip"]
        )

        print("Customer details entered")

        # Continue to overview
        page.get_by_role("button", name="Continue").click()

        page.wait_for_url("**/checkout-step-two.html")

        print("Order overview opened")

        # Read totals
        item_total_text = page.locator(
            '[data-test="subtotal-label"]'
        ).inner_text()

        tax_text = page.locator(
            '[data-test="tax-label"]'
        ).inner_text()

        total_text = page.locator(
            '[data-test="total-label"]'
        ).inner_text()

        item_total = float(
            item_total_text.replace("Item total: $", "")
        )

        tax = float(
            tax_text.replace("Tax: $", "")
        )

        total = float(
            total_text.replace("Total: $", "")
        )

        result["item_total"] = item_total
        result["tax"] = tax
        result["total"] = total

        print("Item total:", item_total)
        print("Tax:", tax)
        print("Total:", total)

        # Calculate expected item total
        expected_item_total = 0.0

        for product in products:
            if (
                    product["name"] in shopping_items
                    and product["name"] not in items_not_found
            ):
                expected_item_total += product["price"]

        expected_item_total = round(expected_item_total, 2)

        print("Expected item total:", expected_item_total)

        # Validate item total
        if item_total != expected_item_total:
            raise AssertionError(
                f"Item total mismatch. Expected "
                f"{expected_item_total}, but got {item_total}"
            )

        print("Item total validation passed")

        # Finish order
        page.get_by_role("button", name="Finish").click()

        page.wait_for_url("**/checkout-complete.html")

        print("Order completed successfully")

        # Save confirmation screenshot
        page.screenshot(
            path="order_confirmation.png",
            full_page=True
        )

        print("Confirmation screenshot saved")

        result["status"] = "success"

except Exception as error:
    result["status"] = "failed"
    result["error"] = str(error)

    print("Automation failed:", error)

finally:
    with open("result.json", "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print("Result saved to result.json")