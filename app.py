from flask import Flask, render_template, redirect, url_for, request, session, flash

app = Flask(__name__)  # ✅ Fixed __name__
app.secret_key = 'your_secret_key'  # Change this to a secure key

# Simulated Database
products = [
    {"id": 1, "name": "Lipstick", "price": 499},
    {"id": 2, "name": "Foundation", "price": 899},
    {"id": 3, "name": "Eyeliner", "price": 299},
]

users = {
    "user@example.com": {
        "password": "password",
        "name": "User"
    }
}

# Initialize cart in session
def get_cart():
    if 'cart' not in session:
        session['cart'] = {
            "items": [], 
            "item_count": 0, 
            "total": 0
        }
    return session['cart']

# Home Page
@app.route('/')
def home():
    return render_template('home.html', products=products)

# Cart Page
@app.route('/cart')
def cart():
    return render_template('cart.html', cart=get_cart())

# Add to Cart
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = get_cart()
    product = next((p for p in products if p["id"] == product_id), None)

    if product:
        for item in cart["items"]:
            if item["id"] == product_id:
                item["quantity"] += 1
                break
        else:
            cart["items"].append({
                "id": product_id, 
                "name": product["name"], 
                "price": product["price"], 
                "quantity": 1
            })

    cart["item_count"] = sum(item["quantity"] for item in cart["items"])
    cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"])
    session.modified = True

    return redirect(url_for('cart'))

# Update Cart
@app.route('/update_cart/<int:item_id>', methods=['POST'])
def update_cart(item_id):
    cart = get_cart()
    quantity = int(request.form.get('quantity', 1))

    for item in cart["items"]:
        if item["id"] == item_id:
            item["quantity"] = quantity
            break

    cart["item_count"] = sum(item["quantity"] for item in cart["items"])
    cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"])
    session.modified = True

    return redirect(url_for('cart'))

# Remove Item from Cart
@app.route('/remove_item/<int:item_id>')
def remove_item(item_id):
    cart = get_cart()
    cart["items"] = [item for item in cart["items"] if item["id"] != item_id]
    cart["item_count"] = sum(item["quantity"] for item in cart["items"])
    cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"])
    session.modified = True

    return redirect(url_for('cart'))

# Checkout
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = get_cart()
    
    if request.method == 'POST':
        form_data = {
            "full_name": request.form.get("full_name"),
            "address": request.form.get("address"),
            "phone": request.form.get("phone"),
            "payment_method": request.form.get("payment_method"),
        }

        if not all(form_data.values()):
            flash("All fields are required.", "error")
            return render_template('checkout.html', cart=cart)

        flash("Order placed successfully!", "success")
        session.pop('cart', None)  # Clear the cart after checkout
        return redirect(url_for('home'))

    return render_template('checkout.html', cart=cart)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = users.get(email)
        if user and user["password"] == password:
            session['user'] = user
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "error")

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# Run the App
if __name__ == '__main__':
    app.run(debug=True)
