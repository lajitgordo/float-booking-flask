from flask import Flask, request, jsonify
import requests
import os

application = Flask(__name__)

# WooCommerce API Credentials
WC_API_URL = "https://floatthefox.com/wp-json/wc/v3/orders"
WC_KEY = os.getenv("WC_API_KEY", "your_consumer_key_here")
WC_SECRET = os.getenv("WC_API_SECRET", "your_consumer_secret_here")

@application.route("/")
def home():
    return "Ahoy! Flask is running on Render!"

@application.route("/create_booking", methods=["POST"])
def create_booking():
    data = request.json

    # Required booking details
    first_name = data.get("first_name", "Guest")
    last_name = data.get("last_name", "User")
    email = data.get("email", "no-email@example.com")
    product_id = data.get("product_id", 2240)  # Default: River Tubing
    quantity = data.get("quantity", 1)

    # Optional upsell items (defaults to 0 if not provided)
    extras = {
        "Waterproof Bluetooth Speaker": {"id": 3353, "quantity": data.get("extra_speaker", 0)},
        "Waterproof Phone Case": {"id": 3350, "quantity": data.get("extra_phone_case", 0)},
        "Dry Bag": {"id": 3348, "quantity": data.get("extra_dry_bag", 0)},
        "River Tube Paddle": {"id": 3345, "quantity": data.get("extra_paddle", 0)},
        "Kayak Rental": {"id": 2615, "quantity": data.get("extra_kayak", 0)}
    }

    # Build order line items
    line_items = [{"product_id": product_id, "quantity": quantity}]
    for item, details in extras.items():
        if details["quantity"] > 0:
            line_items.append({"product_id": details["id"], "quantity": details["quantity"]})

    # WooCommerce order payload
    order = {
        "payment_method": "cod",
        "set_paid": False,
        "billing": {
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        },
        "line_items": line_items
    }

    # Send order to WooCommerce
    response = requests.post(WC_API_URL, auth=(WC_KEY, WC_SECRET), json=order)

    if response.status_code == 201:
        order_data = response.json()
        checkout_url = f"https://floatthefox.com/checkout/order-pay/{order_data['id']}?pay_for_order=true"
        return jsonify({"message": "Booking created!", "checkout_url": checkout_url})

    return jsonify({"error": "Failed to create booking", "details": response.text}), response.status_code

if __name__ == "__main__":
    application.run()
