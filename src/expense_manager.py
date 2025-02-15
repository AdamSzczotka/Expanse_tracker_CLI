from datetime import datetime
from typing import Optional, Dict, Tuple
from decimal import Decimal
import csv
from pathlib import Path
from .expense import Expense
from .budget import Budget
from .storage_handler import StorageHandler
from .exceptions import StorageError


class ExpenseManager:
    def __init__(self, storage: StorageHandler):
        self.storage = storage

    def add_expense(self, description: str,
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

    def get_monthly_summary(self, month: int,
                            year: Optional[int] = None) -> Decimal:
        if year is None:
            year = datetime.now().year

        expenses = self.storage.get_all_expenses()
        monthly_expenses = [
            exp for exp in expenses
            if exp.date.month == month and exp.date.year == year
        ]
        return sum((exp.amount for exp in monthly_expenses), Decimal('0'))

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

    def set_budget(self, month: int, year: int, amount: float,
                   category_limits: Optional[Dict[str, float]] = None) -> None:
        budget = Budget(
            month=month,
            year=year,
            amount=Decimal(str(amount)),
            category_limits={
                k: Decimal(str(v)) for k, v in (category_limits or {}).items()
                }
        )
        budget.validate()
        self.storage.set_budget(budget)

    def get_category_summary(self, category: str, month: Optional[int] = None,
                             year: Optional[int] = None) -> Decimal:
        expenses = self.storage.get_all_expenses()
        filtered_expenses = [
            exp for exp in expenses
            if exp.category == category
            and (month is None or exp.date.month == month)
            and (year is None or exp.date.year == year)
        ]
        return sum((exp.amount for exp in filtered_expenses), Decimal('0'))

    def export_to_csv(self, filepath: str) -> None:
        expenses = self.storage.get_all_expenses()
        filepath = Path(filepath)

        try:
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    ['ID', 'Date', 'Description', 'Amount', 'Category'])
                for expense in expenses:
                    writer.writerow([
                        expense.id,
                        expense.date.strftime('%Y-%m-%d'),
                        expense.description,
                        float(expense.amount),
                        expense.category
                    ])
        except Exception as e:
            raise StorageError(f"Failed to export to CSV: {str(e)}")
