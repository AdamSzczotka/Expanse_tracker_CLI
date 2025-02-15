from datetime import datetime
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
import csv
from pathlib import Path
from .expense import Expense
from .budget import Budget
from .storage_handler import StorageHandler
from .exceptions import ValidationError, BudgetError


class ExpenseManager:
    def __init__(self, storage: StorageHandler):
        self.storage = storage

    def add_expanse(self, description: str,
                    amount: float, category: str) -> Tuple[int, Optional[str]]:
        expense = Expense(
            description=description,
            amount=Decimal(str(amount)),
            date=datetime.now(),
            category=category
        )

        expense_id = self.storage.add_expense(expense)

        # Check budget warning
        warning = self._check_budget_warning(expense)

        return expense_id, warning
