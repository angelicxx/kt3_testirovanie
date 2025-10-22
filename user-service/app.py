from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound

app = Flask(__name__)

# In-memory "database"
_users = {}
_next_id = 1

def _create_user_id():
    global _next_id
    uid = _next_id
    _next_id += 1
    return uid

@app.get("/health")
def health():
    return {"status": "ok"}, 200

@app.post("/users")
def create_user():
    if not request.is_json:
        raise BadRequest("Expected application/json body")
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    if not name or not email:
        raise BadRequest("Fields 'name' and 'email' are required")
    uid = _create_user_id()
    user = {"id": uid, "name": name, "email": email}
    _users[uid] = user
    return user, 201

@app.get("/users/<int:user_id>")
def get_user(user_id: int):
    user = _users.get(user_id)
    if not user:
        raise NotFound(f"User {user_id} not found")
    return user, 200

if __name__ == "__main__":
    # Default to port 5001 to avoid clashing with the order-service
    app.run(host="127.0.0.1", port=5001, debug=True)
