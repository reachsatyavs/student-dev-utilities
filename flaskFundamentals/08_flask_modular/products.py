"""
A SECOND feature file, built exactly like auth.py next to it.

Why bother splitting files at all?
---------------------------------
With one small file (like 07_flask_login_page.py) everything is easy. But
a real app keeps growing -- login, products, cart, checkout, admin... Put
all of that in one file and you get a 1000-line monster where finding the
cart code means scrolling past everything else.

So we give each FEATURE its own file:

    auth.py      -> everything about logging in
    products.py  -> everything about products   (this file)
    app.py       -> creates the app, wires the features together

Three things you get from this:

1. You know where to look. Bug in the product list? It's in products.py.
   Nothing else can be hiding it.
2. You can work without stepping on each other. One student edits auth.py
   while another edits products.py -- no conflicts, because the files
   never touch.
3. Adding a feature is cheap. This whole file was added to the app with
   ONE new line in app.py. Nothing in auth.py had to change, so there was
   no way to accidentally break login while building products.

Notice this file never imports app.py, and never creates a Flask app of
its own. It only defines register_routes(app) and waits to be handed an
app. That one-way direction (app.py knows about products.py, but
products.py knows nothing about app.py) is what keeps the pieces
independent -- and it's exactly what the real shoppingCart project does.
"""

# Pretend this came from a database. Later, in the shoppingCart project,
# it will -- but the routes below barely change when that happens.
PRODUCTS = [
    {"id": 1, "title": "Notebook", "price": 3.50},
    {"id": 2, "title": "Pencil", "price": 0.75},
    {"id": 3, "title": "Backpack", "price": 24.00},
]


def register_routes(app):
    @app.route("/products")
    def list_products():
        # Build one <li> per product by looping over the list.
        items = ""
        for product in PRODUCTS:
            items += (
                f'<li><a href="/products/{product["id"]}">{product["title"]}</a>'
                # :.2f prints 3.5 as "3.50" -- prices should show both decimals.
                f' -- ${product["price"]:.2f}</li>'
            )

        return f"""
            <h1>Products</h1>
            <ul>{items}</ul>
            <p><a href="/">Back home</a></p>
        """

    # <int:product_id> captures whatever number is in the URL and passes it
    # to the function below as product_id. Visiting /products/2 means Flask
    # calls product_detail(product_id=2). The "int:" part tells Flask to
    # expect a number, so /products/banana gives a 404 instead of an error.
    @app.route("/products/<int:product_id>")
    def product_detail(product_id):
        for product in PRODUCTS:
            if product["id"] == product_id:
                return f"""
                    <h1>{product["title"]}</h1>
                    <p>Price: ${product["price"]:.2f}</p>
                    <p><a href="/products">Back to products</a></p>
                """

        # No product matched. Returning a second value (404) sets the status
        # code, which is how a server says "that page doesn't exist".
        return "<h1>Not found</h1><p>No product with that id.</p>", 404
