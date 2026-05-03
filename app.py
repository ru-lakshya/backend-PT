import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv

# Env setup
load_dotenv()

# App init
app = Flask(__name__)
CORS(app)

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Default image
NO_IMAGE_URL = "https://development-and-testing-bucket-abcdxyz1234.s3.ap-south-1.amazonaws.com/no-pictures.png"


# Health check
@app.route("/", methods=["GET"])
def base_app():
    return jsonify({"status": "App is running..."}), 200


# GET products
@app.route("/products", methods=["GET"])
def get_products():
    try:
        res = supabase.table("products").select("*").execute()
        return jsonify({"products": res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# POST product
@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400
    if not data.get("price") or float(data.get("price")) <= 0:
        return jsonify({"error": "price must be a positive number"}), 400
    if not data.get("rating"):
        return jsonify({"error": "rating is required"}), 400

    new_product = {
        "title": data["title"],
        "price": float(data["price"]),
        "rating": float(data["rating"]),
        "thumbnail": data.get("thumbnail", NO_IMAGE_URL)
    }

    try:
        res = supabase.table("products").insert(new_product).execute()
        return jsonify({"product": res.data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# DELETE product
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        check = supabase.table("products").select("*").eq("id", product_id).execute()
        if not check.data:
            return jsonify({"error": "Product not found"}), 404

        res = supabase.table("products").delete().eq("id", product_id).execute()
        return jsonify({"message": "Product deleted successfully", "data": res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# PATCH product
@app.route("/products/<int:product_id>", methods=["PATCH"])
def update_product(product_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    try:
        check = supabase.table("products").select("*").eq("id", product_id).execute()
        if not check.data:
            return jsonify({"error": "Product not found"}), 404

        update_data = {}
        if "title" in data:
            update_data["title"] = data["title"]
        if "price" in data:
            if float(data["price"]) <= 0:
                return jsonify({"error": "price must be a positive number"}), 400
            update_data["price"] = float(data["price"])
        if "rating" in data:
            update_data["rating"] = float(data["rating"])
        if "thumbnail" in data:
            update_data["thumbnail"] = data["thumbnail"]

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        res = supabase.table("products").update(update_data).eq("id", product_id).execute()
        return jsonify({"message": "Product updated successfully", "data": res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# POST checkout
@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json()

    if not data or not data.get("name") or not data.get("room_no") or not data.get("building_number") or not data.get("order"):
        return jsonify({"error": "Missing required checkout fields"}), 400

    order_record = {
        "name": data.get("name"),
        "room_no": data.get("room_no"),
        "building_number": data.get("building_number"),
        "order_items": data.get("order"),
        "payable_amount": data.get("payable_amount") or 0
    }

    try:
        res = supabase.table("order_table").insert(order_record).execute()
        return jsonify({"message": "Order saved successfully", "data": res.data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run server
if __name__ == "__main__":
    app.run(port=5001, debug=True)
