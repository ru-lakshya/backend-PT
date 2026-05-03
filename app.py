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

# delete product

# update product

# checkout


if __name__ == "__main__":
    app.run(port=5005, debug=True)
