from typing import List, Optional

from src.main.api.models.credit_history_response import Credit


def find_credit_by_id(credits: List[Credit], credit_id: int) -> Optional[Credit]:
    return next((c for c in credits if c.creditId == credit_id), None)