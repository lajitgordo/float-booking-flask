from flask import Flask, request, jsonify
import requests
import os

application = Flask(__name__)

# WooCommerce API credentials (from environment or fallback)
WC_API_URL = "https://floatthefox.com/wp-json/wc/v3/orders"
WC_KEY = os.getenv("WC_API_KEY", "your_consumer_key_here")
WC_SECRET = os.getenv("WC_API_SECRET", "your_consumer_secret_here")

@application.route("/")
def home():
    return "Ahoy! Flask is running on Render!"

@application.route("/create_booking", methods=["POST"])
def create_booking():
    data = request.json

    # Required fields
    first_name = data.get("first_name", "Guest")
    last_name = data.get("last_name", "User")
    email = data.get("email", "no-email@example.com")
    product_id = data.get("product_id", 2240)
    quantity = data.get("quantity", 1)

    # Booking date/time (defaults to June 1, 2025)
    booking_date = data.get("booking_date", "June 1")
    booking_time = data.get("booking_time", "12:00 PM")
    full_booking_date = f"{booking_date}, 2025"

    # Optional upsell items
    extras = {
        "Waterproof Bluetooth Speaker": {"id": 3353, "quantity": data.get("extra_speaker", 0)},
        "Waterproof Phone Case": {"id": 3350, "quantity": data.get("extra_phone_case", 0)},
        "Dry Bag": {"id": 3348, "quantity": data.get("extra_dry_bag", 0)},
        "River Tube Paddle": {"id": 3345, "quantity": data.get("extra_paddle", 0)},
        "Kayak Rental": {"id": 2615, "quantity": data.get("extra_kayak", 0)}
    }

    # Line items
    line_items = [{"product_id": product_id, "quantity": quantity}]
    for item in extras.values():
        if item["quantity"] > 0:
            line_items.append({
                "product_id": item["id"],
                "quantity": item["quantity"]
            })

    # WooCommerce order payload
    order = {
        "payment_method": "paypal",
        "set_paid": False,
        "billing": {
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        },
        "line_items": line_items,
        "meta_data": [
            {"key": "Booking Date", "value": full_booking_date},
            {"key": "Booking Time", "value": booking_time}
        ]
    }

    try:
        # Step 1: Create the order
        response = requests.post(WC_API_URL, auth=(WC_KEY, WC_SECRET), json=order)

        if response.status_code == 201:
            order_data = response.json()
            order_id = order_data.get("id")

            # Step 2: Send the invoice email
            invoice_url = f"https://floatthefox.com/wp-json/wc/v3/orders/{order_id}/send_email"
            invoice_payload = {"email": "customer_invoice"}
            email_response = requests.post(invoice_url, auth=(WC_KEY, WC_SECRET), json=invoice_payload)

            # Log response for debugging
            print(f"Email status: {email_response.status_code}")
            print(f"Email response: {email_response.text}")

            # Step 3: Send checkout link
            checkout_url = f"https://floatthefox.com/checkout/order-pay/{order_id}?pay_for_order=true"
            return jsonify({
                "message": "Booking created!",
                "checkout_url": checkout_url,
                "order_id": order_id
            })

        # If failed
        return jsonify({
            "error": "Failed to create booking",
            "details": response.text
        }), response.status_code

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@application.route("/get_product_info", methods=["GET"])
def get_product_info():
    return jsonify({
        "products": {
            "River Tubing": {"id": 2240, "price": "35.00", "in_stock": True},
            "Waterproof Bluetooth Speaker": {"id": 3353, "price": "20.00", "in_stock": True},
            "Waterproof Phone Case": {"id": 3350, "price": "15.00", "in_stock": True},
            "Dry Bag": {"id": 3348, "price": "15.00", "in_stock": True},
            "River Tube Paddle": {"id": 3345, "price": "5.00", "in_stock": True},
            "Kayak Rental": {"id": 2615, "price": "75.00", "in_stock": True}
        }
    })

if __name__ == "__main__":
    application.run()
