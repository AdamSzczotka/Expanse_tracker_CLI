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

    def _check_budget_warning(self, expense: Expense) -> Optional[str]:
        current_month = expense.date.month
        current_year = expense.date.year

        budget = self.storage.get_budget(current_month, current_year)
        if not budget:
            return None

        monthly_total = self.get_monthly_summary(current_month, current_year)
        category_total = self.get_category_summary(expense.category,
                                                   current_month, current_year)

        warnings = []

        # Check total budget
        if monthly_total > budget.amount:
            warnings.append(f"Total budget of "
                            f"${float(budget.amount):.2f} exceeded!")

        # Check category budget
        if (budget.category_limits and
                expense.category in budget.category_limits):
            category_limit = budget.category_limits[expense.category]
            if category_total > category_limit:
                warnings.append(
                    f"Category '{expense.category}' budget of "
                    f"${float(category_limit):.2f}"
                )

        return " ".join(warnings) if warnings else None
