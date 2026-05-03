import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase_client = create_client(supabase_url, supabase_key)

# base app

@app.route("/", methods=["GET"])
def base_app():
    return jsonify({"status": "App is running..."}), 200

# get product

@app.route("/products", methods=["GET"])
def get_products():
    try:
        res = supabase_client.table("products").select("*").execute()
        return jsonify({"products": res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# create product
@app.route("/products", methods=["POST"])
def create_product():
    # Extract JSON data from the request body
    data = request.get_json()
    
    # Validation logic
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    if not data.get("price") or float(data.get("price")) <= 0:
        return jsonify({"error": "price must be a positive number"}), 400

    if not data.get("rating"):
        return jsonify({"error": "rating is required"}), 400

    # Prepare product data for insertion
    new_product = {
        "title": data["title"],
        "price": float(data["price"]),
        "rating": float(data["rating"]),
        "thumbnail": data.get("thumbnail", NO_IMAGE_URL)
    }

    try:
        # Insert the new product into Supabase
        res = supabase.table("products").insert(new_product).execute()
        return jsonify({"product": res.data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# update product
@app.route("/products/<int:product_id>", methods=["PATCH"])
def update_product(product_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    try:
        # Check if the product exists
        check = supabase.table("products").select("*").eq("id", product_id).execute()
        if not check.data:
            return jsonify({"error": "Product not found"}), 404

        # Prepare update data by taking only the provided fields
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

        # Only run update query if there are fields to update
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        # Perform the update operation in Supabase
        res = supabase.table("products").update(update_data).eq("id", product_id).execute()
        return jsonify({
            "message": "Product updated successfully",
            "data": res.data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# delete product
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        # Check if the product exists using a select query
        check = supabase.table("products").select("*").eq("id", product_id).execute()
        if not check.data:
            return jsonify({"error": "Product not found"}), 404

        # Delete the product matching the given ID
        res = supabase.table("products").delete().eq("id", product_id).execute()
        return jsonify({
            "message": "Product deleted successfully",
            "data": res.data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5005, debug=True)
