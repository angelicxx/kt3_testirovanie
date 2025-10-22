import os
import requests
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound, ServiceUnavailable

app = Flask(__name__)

# In-memory "database"
_orders = {}
_next_id = 1

def _create_order_id():
    global _next_id
    oid = _next_id
    _next_id += 1
    return oid

def get_user_service_base_url():
    # Allow request-level override via header for test scenarios (e.g., simulate downtime)
    hdr_url = request.headers.get("X-User-Service-Url")
    if hdr_url:
        return hdr_url.rstrip("/")
    return os.getenv("USER_SERVICE_URL", "http://127.0.0.1:5001").rstrip("/")

@app.get("/health")
def health():
    return {"status": "ok"}, 200

@app.post("/orders")
def create_order():
    if not request.is_json:
        raise BadRequest("Expected application/json body")
    data = request.get_json() or {}
    user_id = data.get("user_id")
    item = data.get("item")
    price = data.get("price")

    if not isinstance(user_id, int):
        raise BadRequest("'user_id' (int) is required")
    if not item:
        raise BadRequest("'item' is required")
    if price is None:
        raise BadRequest("'price' is required")

    # Fetch user details from user-service
    base = get_user_service_base_url()
    url = f"{base}/users/{user_id}"
    try:
        r = requests.get(url, timeout=2.0)
    except requests.exceptions.RequestException as e:
        # user-service is unavailable or timed out
        raise ServiceUnavailable(f"user-service unavailable: {e}")

    if r.status_code == 404:
        raise BadRequest(f"user {user_id} not found in user-service")
    if r.status_code >= 500:
        raise ServiceUnavailable("user-service error")

    user_data = r.json()

    oid = _create_order_id()
    order = {
        "id": oid,
        "user_id": user_id,
        "item": item,
        "price": price,
        "user_name": user_data.get("name"),
        "user_email": user_data.get("email"),
    }
    _orders[oid] = order
    return order, 201

@app.get("/orders/<int:order_id>")
def get_order(order_id: int):
    order = _orders.get(order_id)
    if not order:
        raise NotFound(f"Order {order_id} not found")
    return order, 200

if __name__ == "__main__":
    # Default to port 5002 to avoid clashing with the user-service
    app.run(host="127.0.0.1", port=5002, debug=True)
