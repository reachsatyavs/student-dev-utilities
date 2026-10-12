from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import CartItem, Product


def register_routes(app):
    @app.route("/cart")
    @login_required
    def view_cart():
        items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = sum(item.product.price * item.quantity for item in items)
        return render_template("cart.html", items=items, total=total)

    @app.route("/cart/add/<int:product_id>", methods=["POST"])
    @login_required
    def add_to_cart(product_id):
        product = Product.query.get_or_404(product_id)
        quantity = request.form.get("quantity", 1, type=int) or 1

        item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        if item:
            item.quantity += quantity
        else:
            item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
            db.session.add(item)

        db.session.commit()
        flash(f'Added "{product.title}" to your cart.', "success")
        return redirect(url_for("dashboard"))

    @app.route("/cart/update/<int:item_id>", methods=["POST"])
    @login_required
    def update_quantity(item_id):
        item = CartItem.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            flash("You cannot modify another user's cart.", "danger")
            return redirect(url_for("view_cart"))

        quantity = request.form.get("quantity", 1, type=int) or 1
        if quantity <= 0:
            db.session.delete(item)
        else:
            item.quantity = quantity

        db.session.commit()
        return redirect(url_for("view_cart"))

    @app.route("/cart/remove/<int:item_id>", methods=["POST"])
    @login_required
    def remove_from_cart(item_id):
        item = CartItem.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            flash("You cannot modify another user's cart.", "danger")
            return redirect(url_for("view_cart"))

        db.session.delete(item)
        db.session.commit()
        return redirect(url_for("view_cart"))

    # checkout + order_confirmation land in Day4, once Order/OrderItem exist.
