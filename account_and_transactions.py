from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from datetime import datetime
import os

# ---------- Imports ----------
from models import db, Account, Transaction  # import models and db

# ---------- Config ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "banking.sqlite")
DATABASE_URI = f"sqlite:///{DB_PATH}"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)  # initialize db with Flask app

# ---------- Helpers ----------
def parse_amount(value):
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError("Invalid amount format.")
    d = d.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    if d < 0:
        raise ValueError("Amount must be non-negative.")
    return d


# ---------- Routes ----------
@app.route("/accounts", methods=["POST"])
def create_account():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    name = data.get("name")
    email = data.get("email")
    contact = data.get("contact")
    initial = data.get("initial_balance", "0.00")

    if not name or not email:
        return jsonify({"error": "Both 'name' and 'email' are required"}), 400

    try:
        initial_balance = parse_amount(initial)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    acct = Account(name=name, email=email, contact=contact, balance=initial_balance)
    db.session.add(acct)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already in use"}), 409

    if initial_balance > 0:
        tx = Transaction(account_id=acct.id, amount=initial_balance, type="deposit", description="Initial balance")
        db.session.add(tx)
        db.session.commit()

    return jsonify(acct.to_dict()), 201


@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    include_tx = request.args.get("transactions", "false").lower() in ("1", "true", "yes")
    tx_limit = min(int(request.args.get("tx_limit", 20)), 200)
    tx_offset = int(request.args.get("tx_offset", 0))
    acct = Account.query.get(account_id)
    if not acct:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(acct.to_dict(include_transactions=include_tx, tx_limit=tx_limit, tx_offset=tx_offset)), 200

# (All your other routes go here — same as before — no need to change them)

# ---------- Bootstrap ----------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
