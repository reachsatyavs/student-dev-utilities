from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from extensions import db
from models import CartItem, OrderItem, Product, User
from services.product_api import sync_products_from_api
from utils.decorators import admin_required


def register_routes(app):
    @app.route("/admin")
    @login_required
    @admin_required
    def admin_home():
        return redirect(url_for("admin_users"))

    @app.route("/admin/users")
    @login_required
    @admin_required
    def admin_users():
        all_users = User.query.order_by(User.created_at.desc()).all()
        return render_template("admin/users.html", users=all_users)

    @app.route("/admin/users/<int:user_id>/reset-password", methods=["POST"])
    @login_required
    @admin_required
    def admin_reset_user_password(user_id):
        user = User.query.get_or_404(user_id)
        new_password = request.form.get("new_password", "")

        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("admin_users"))

        user.set_password(new_password)
        user.register_successful_login()  # clear any lockout too
        db.session.commit()
        flash(f"Password reset for {user.username}.", "success")
        return redirect(url_for("admin_users"))

    @app.route("/admin/products")
    @login_required
    @admin_required
    def admin_products():
        all_products = Product.query.order_by(Product.created_at.desc()).all()
        return render_template("admin/products.html", products=all_products)

    @app.route("/admin/products/add", methods=["POST"])
    @login_required
    @admin_required
    def admin_add_product():
        title = request.form.get("title", "").strip()
        price = request.form.get("price", type=float)
        stock = request.form.get("stock", type=int) or 0
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        thumbnail_url = request.form.get("thumbnail_url", "").strip()

        if not title or price is None:
            flash("Title and price are required.", "danger")
            return redirect(url_for("admin_products"))

        product = Product(
            title=title,
            price=price,
            stock=stock,
            category=category,
            description=description,
            thumbnail_url=thumbnail_url,
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{title}" added.', "success")
        return redirect(url_for("admin_products"))

    @app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
    @login_required
    @admin_required
    def admin_delete_product(product_id):
        product = Product.query.get_or_404(product_id)

        if OrderItem.query.filter_by(product_id=product.id).first():
            flash(f'"{product.title}" is part of a past order and cannot be removed.', "danger")
            return redirect(url_for("admin_products"))

        CartItem.query.filter_by(product_id=product.id).delete()
        db.session.delete(product)
        db.session.commit()
        flash(f'Product "{product.title}" removed.', "success")
        return redirect(url_for("admin_products"))

    @app.route("/admin/products/sync", methods=["POST"])
    @login_required
    @admin_required
    def admin_sync_products():
        created = sync_products_from_api()
        flash(f"Synced {created} new product(s) from the API.", "success")
        return redirect(url_for("admin_products"))
