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

if __name__ == '__main__':
    app.run(debug=True)
