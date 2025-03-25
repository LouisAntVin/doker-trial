from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a strong secret key
inventory_file = "inventory.csv"

# Dummy user credentials (replace with a proper authentication system)
USERS = {"admin": "password123"}

def load_inventory():
    try:
        return pd.read_csv(inventory_file, dtype={"Product ID": str})
    except FileNotFoundError:
        return pd.DataFrame(columns=["Product ID", "Product Name", "Category", "Price", "Stock", "Total Sales"])

def save_inventory(inventory):
    inventory.to_csv(inventory_file, index=False)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    inventory = load_inventory()
    low_stock_items = []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            product_id = request.form["product_id"]
            product_name = request.form["product_name"]
            category = request.form["category"]
            price = request.form["price"]
            stock = request.form["stock"]

            new_product = pd.DataFrame({
                "Product ID": [product_id],
                "Product Name": [product_name],
                "Category": [category],
                "Price": [price],
                "Stock": [stock],
                "Total Sales": [0]
            })

            inventory = pd.concat([inventory, new_product], ignore_index=True)
            save_inventory(inventory)

        elif action == "delete":
            product_id = str(request.form["delete_id"])
            inventory = inventory[inventory["Product ID"] != product_id]
            save_inventory(inventory)

        elif action == "update":
            product_id = str(request.form["update_id"])
            field = request.form["field"]
            new_value = request.form["new_value"]

            if field in ["Price", "Stock"]:
                try:
                    new_value = float(new_value) if field == "Price" else int(new_value)
                except ValueError:
                    return redirect("/")

            inventory.loc[inventory["Product ID"] == product_id, field] = new_value
            save_inventory(inventory)

        elif action == "record_sale":
            product_id = str(request.form["sale_id"])
            try:
                quantity_sold = int(request.form["quantity_sold"])
            except ValueError:
                return redirect("/")

            if product_id in inventory["Product ID"].values:
                product_index = inventory[inventory["Product ID"] == product_id].index[0]
                stock = int(inventory.loc[product_index, "Stock"])

                if stock >= quantity_sold:
                    inventory.loc[product_index, "Stock"] = stock - quantity_sold
                    inventory.loc[product_index, "Total Sales"] += quantity_sold
                    save_inventory(inventory)

        elif action == "restock":
            threshold = int(request.form["threshold"])
            low_stock_items = inventory[inventory["Stock"].astype(int) < threshold].to_dict(orient="records")

    return render_template("index.html", inventory=inventory.to_dict(orient="records"), low_stock_items=low_stock_items)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
