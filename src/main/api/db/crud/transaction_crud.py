from typing import Union

from sqlalchemy.orm import Session

from src.main.api.db.models.transaction_table import Transaction


class TransactionCrudDb:
    @staticmethod
    def get_transaction_by_id(db: Session, transaction_id: int) -> Union[Transaction, None]:
        return db.query(Transaction).filter_by(id=transaction_id).first()

    @staticmethod
    def get_transactions_by_account_id(db: Session, account_id: int) -> list[type[Transaction]]:
        return db.query(Transaction).filter(
            (Transaction.to_account_id == account_id) | (Transaction.from_account_id == account_id)
        ).all()