from flask import render_template, request
from flask_login import login_required

from models import Product


def register_routes(app):
    @app.route("/dashboard")
    @login_required
    def dashboard():
        search = request.args.get("q", "").strip()
        category = request.args.get("category", "").strip()

        query = Product.query
        if search:
            query = query.filter(Product.title.ilike(f"%{search}%"))
        if category:
            query = query.filter_by(category=category)

        products = query.order_by(Product.title).all()
        categories = sorted({p.category for p in Product.query.all() if p.category})

        return render_template(
            "dashboard.html",
            products=products,
            categories=categories,
            search=search,
            selected_category=category,
        )
