from datetime import datetime
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from database import db

class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact = db.Column(db.String(50))
    balance = db.Column(db.Numeric(12, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="account", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "contact": self.contact,
            "balance": str(self.balance),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class Transaction(db.Model):
    __tablename__ = "transaction"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # deposit or withdrawal
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "type": self.type,
            "amount": str(self.amount),
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "description": self.description,
        }
