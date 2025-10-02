from flask import Flask, jsonify, request

app = Flask(__name__)

items = [
  {"id":1, "name": "Laptop", "quantity": 10},
  {"id":2, "name": "Mouse", "quantity": 25},
  {"id":3, "name": "Keyboard", "quantity": 15}
]

@app.route('/')
def home():
    return "Welcome to Inventory Tracker!"

@app.route('/items')
def get_items():
  return jsonify(items)

@app.route('/items', methods=['POST'])
def add_item():
  data = request.get_json()
  new_item = {
    "id": len(items) + 1,
    "name": data["name"],
    "quantity": data["quantity"]
  }
  items.append(new_item)
  return jsonify(new_item), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    for item in items:
        if item["id"] == item_id:
            item["quantity"] = data.get("quantity", item["quantity"])
            return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404

# DELETE - remove an item by id
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    for item in items:
        if item["id"] == item_id:
            items.remove(item)
            return jsonify({"message": f"Item with id {item_id} deleted successfully!"}), 200
    return jsonify({"error": "Item not found"}), 404
 
if __name__ == '__main__':
    app.run(debug=True)
