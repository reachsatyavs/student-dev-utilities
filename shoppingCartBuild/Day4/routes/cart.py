from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import CartItem, Order, OrderItem, Product


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

    @app.route("/checkout", methods=["POST"])
    @login_required
    def checkout():
        items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for("view_cart"))

        total = sum(item.product.price * item.quantity for item in items)
        order = Order(user_id=current_user.id, total_amount=total, status="placed")
        db.session.add(order)
        db.session.flush()  # get order.id before commit

        for item in items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price,
                )
            )
            db.session.delete(item)

        db.session.commit()
        flash(f"Order #{order.id} placed successfully!", "success")
        return redirect(url_for("order_confirmation", order_id=order.id))

    @app.route("/orders/<int:order_id>")
    @login_required
    def order_confirmation(order_id):
        order = Order.query.get_or_404(order_id)
        if order.user_id != current_user.id:
            flash("You cannot view another user's order.", "danger")
            return redirect(url_for("dashboard"))
        return render_template("order_confirmation.html", order=order)
