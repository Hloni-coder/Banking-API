from flask import Flask, render_template, request, jsonify, redirect, url_for
from decimal import Decimal, InvalidOperation
from sqlalchemy.exc import IntegrityError

# Import database and models
from database import db
from models import Account, Transaction
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///banking.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# --------------------------------------------------------
# Utility function
# --------------------------------------------------------
def parse_amount(value):
    try:
        amount = Decimal(value)
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        return amount
    except (InvalidOperation, TypeError):
        raise ValueError("Invalid amount format")


# --------------------------------------------------------
# Routes
# --------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create_account")
def create_account_page():
    return render_template("create_account.html")


@app.route("/accounts", methods=["POST"])
def create_account():
    data = request.get_json(force=True, silent=True) or request.form.to_dict()

    name = data.get("name")
    email = data.get("email")
    contact = data.get("contact")
    initial = data.get("initial_balance", "0.00")

    if not name or not email:
        return jsonify({"error": "Both name and email are required"}), 400

    try:
        initial_balance = parse_amount(initial)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    account = Account(name=name, email=email, contact=contact, balance=initial_balance)
    db.session.add(account)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409

    if initial_balance > 0:
        tx = Transaction(
            account_id=account.id,
            amount=initial_balance,
            type="deposit",
            description="Initial deposit",
        )
        db.session.add(tx)
        db.session.commit()

    if request.content_type == "application/json":
        return jsonify(account.to_dict()), 201
    else:
        return redirect(url_for("home"))


@app.route("/accounts_list")
def list_accounts():
    accounts = Account.query.all()
    return render_template("accounts_list.html", accounts=accounts)


@app.route("/accounts/<int:account_id>")
def get_account(account_id):
    account = Account.query.get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(account.to_dict())


# --------------------------------------------------------
# Initialize DB and run app
# --------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
