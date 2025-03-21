from flask import Flask, request, jsonify
import requests
import os
import logging
import sys

logging.basicConfig(stream=sys.stderr)

application = Flask(__name__)

# Product ID map
PRODUCTS = {
    "float": 2240,
    "speaker": 3353,
    "phone_case": 3350,
    "dry_bag": 3348,
    "paddle": 3345,
    "gift_card": 3473,
    "kayak": 2615
}

@application.route("/")
def home():
    return "Ahoy! Flask is running on Render!"

@application.route("/get_product_info", methods=["GET"])
def get_product_info():
    return jsonify({
        "products": {
            "float": {"id": PRODUCTS["float"], "price": "35.00", "in_stock": True},
            "speaker": {"id": PRODUCTS["speaker"], "price": "20.00", "in_stock": True},
            "phone_case": {"id": PRODUCTS["phone_case"], "price": "15.00", "in_stock": True},
            "dry_bag": {"id": PRODUCTS["dry_bag"], "price": "15.00", "in_stock": True},
            "paddle": {"id": PRODUCTS["paddle"], "price": "5.00", "in_stock": True},
            "gift_card": {"id": PRODUCTS["gift_card"], "price": "10.00-100.00", "in_stock": True},
            "kayak": {"id": PRODUCTS["kayak"], "price": "75.00", "in_stock": True}
        }
    })

@application.route("/create_booking", methods=["POST"])
def create_booking():
    try:
        data = request.json
        wc_api_url = "https://floatthefox.com/wp-json/wc/v3/orders"
        wc_key = os.getenv("WC_API_KEY", "your_consumer_key_here")
        wc_secret = os.getenv("WC_API_SECRET", "your_consumer_secret_here")

        print("Received booking request:", data)

        # Base booking product
        line_items = [{
            "product_id": PRODUCTS["float"],
            "quantity": data["quantity"]
        }]

        # Handle upsells
        extras = data.get("extras", {})
        for item_name, qty in extras.items():
            if item_name in PRODUCTS:
                line_items.append({
                    "product_id": PRODUCTS[item_name],
                    "quantity": qty
                })

        # Create order
        order = {
            "payment_method": "cod",
            "set_paid": False,
            "billing": {
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "email": data["email"]
            },
            "line_items": line_items
        }

        response = requests.post(wc_api_url, auth=(wc_key, wc_secret), json=order)
        print("WooCommerce response:", response.status_code, response.text)

        # Build checkout link
        product_ids = [str(item["product_id"]) for item in line_items]
        quantities = [str(item["quantity"]) for item in line_items]
        checkout_url = f"https://floatthefox.com/checkout?add-to-cart={','.join(product_ids)}&quantity={','.join(quantities)}"

        return jsonify({
            "success": True,
            "order": response.json(),
            "checkout_url": checkout_url
        })

    except Exception as e:
        logging.error("Error in /create_booking: %s", str(e))
        return jsonify({"error": str(e)}), 500
