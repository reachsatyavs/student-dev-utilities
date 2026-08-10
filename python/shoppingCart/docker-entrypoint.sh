#!/bin/sh
set -e

python init_db.py --sync-products

exec python -m flask --app app run --host=0.0.0.0 --port=5000
