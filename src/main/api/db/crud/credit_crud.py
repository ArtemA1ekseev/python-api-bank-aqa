from typing import Union, List

from sqlalchemy.orm import Session

from src.main.api.db.models.credit_table import Credit


class CreditCrudDb:
    @staticmethod
    def get_credit_by_id(db: Session, credit_id: int) -> Union[Credit, None]:
        return db.query(Credit).filter_by(id=credit_id).first()

    @staticmethod
    def get_credits_by_account_id(db: Session, account_id: int) -> list[type[Credit]]:
        return db.query(Credit).filter_by(account_id=account_id).all()