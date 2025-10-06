from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint
from . import db


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    contact = db.Column(db.String(80), nullable=True)
    balance = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("balance >= 0", name="balance_non_negative"),
    )

    def to_dict(self, include_transactions=False, tx_limit=20, tx_offset=0):
        from .transaction import Transaction  # local import to avoid circular dependency
        base = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "contact": self.contact,
            "balance": str(self.balance.quantize(Decimal("0.01"))),
            "created_at": self.created_at.isoformat(),
        }
        if include_transactions:
            txs = (
                Transaction.query.filter_by(account_id=self.id)
                .order_by(Transaction.timestamp.desc())
                .offset(tx_offset)
                .limit(tx_limit)
                .all()
            )
            base["transactions"] = [t.to_dict() for t in txs]
        return base
