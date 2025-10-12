from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# ---------------- DATABASE CONFIGURATION ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ---------------- MODEL ----------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


# ---------------- CREATE DATABASE ----------------
with app.app_context():
    db.create_all()


# ---------------- VALIDATION FUNCTION ----------------
def validate_item(data):
    """Check if the input data is valid before saving to DB."""
    if not data or "name" not in data or "quantity" not in data:
        return "Name and quantity are required."
    if not data["name"].strip():
        return "Name cannot be empty."
    if not isinstance(data["quantity"], int) or data["quantity"] <= 0:
        return "Quantity must be a positive integer."
    return None


# ---------------- ROUTES ----------------

@app.route("/items", methods=["GET"])
def get_items():
    # ✅ Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search = request.args.get("search", "", type=str).strip()  # changed from 'q' → 'search'
    sort_by = request.args.get("sort_by", "id", type=str)
    sort_order = request.args.get("sort_order", "asc", type=str)

    # ✅ Validate pagination parameters
    if page < 1:
        return jsonify({"error": "Page must be a positive integer"}), 400
    if per_page < 1 or per_page > 100:
        return jsonify({"error": "per_page must be between 1 and 100"}), 400

    # ✅ Build the query
    query = Item.query

    # Filter items if a search term is provided
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))

    # ✅ Handle sorting (by valid fields only)
    valid_sort_fields = ["name", "quantity", "created_at", "updated_at"]
    if sort_by in valid_sort_fields:
        order = getattr(Item, sort_by).asc() if sort_order == "asc" else getattr(Item, sort_by).desc()
        query = query.order_by(order)
    else:
        query = query.order_by(Item.id.asc())

    # ✅ Pagination handling
    try:
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    except Exception as e:
        return jsonify({"error": f"Invalid pagination parameters: {str(e)}"}), 400

    # ✅ Convert to JSON-friendly format
    items = [item.to_dict() for item in pagination.items]
    return jsonify({
        "items": items,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page
    })


@app.route("/items", methods=["POST"])
def add_item():
    data = request.json
    error = validate_item(data)
    if error:
        return jsonify({"error": error}), 400

    new_item = Item(name=data["name"], quantity=data["quantity"])
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201


@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.json
    error = validate_item(data)
    if error:
        return jsonify({"error": error}), 400

    item.name = data["name"]
    item.quantity = data["quantity"]
    db.session.commit()
    return jsonify(item.to_dict())


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted successfully"})


# ---------------- ERROR HANDLING ----------------
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found", "message": "The requested resource was not found."}), 404


@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({"error": "Bad Request", "message": "Invalid request."}), 400


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback any failed transaction
    return jsonify({"error": "Internal Server Error", "message": "Something went wrong on the server."}), 500


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
