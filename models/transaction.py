from datetime import datetime
from decimal import Decimal
from . import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)

    account = db.relationship("Account", backref="all_transactions")

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "amount": str(self.amount.quantize(Decimal("0.01"))),
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
        }
