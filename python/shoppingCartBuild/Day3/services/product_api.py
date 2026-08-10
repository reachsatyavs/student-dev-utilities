import requests
from flask import current_app

from extensions import db
from models import Product


def fetch_products_from_api(limit=30):
    """Session 3: pull a product catalog from https://dummyjson.com/products
    instead of typing sample data by hand.
    """
    url = current_app.config["PRODUCTS_API_URL"]
    response = requests.get(url, params={"limit": limit}, timeout=10)
    response.raise_for_status()
    return response.json().get("products", [])


def sync_products_from_api(limit=30):
    """Insert products from the API that we don't already have (matched by
    external_id), so re-running this is safe.
    """
    existing_external_ids = {p.external_id for p in Product.query.all() if p.external_id}

    created = 0
    for item in fetch_products_from_api(limit=limit):
        if item["id"] in existing_external_ids:
            continue
        product = Product(
            external_id=item["id"],
            title=item["title"],
            description=item.get("description", ""),
            category=item.get("category", ""),
            price=item.get("price", 0),
            stock=item.get("stock", 0),
            thumbnail_url=item.get("thumbnail", ""),
        )
        db.session.add(product)
        created += 1

    db.session.commit()
    return created
