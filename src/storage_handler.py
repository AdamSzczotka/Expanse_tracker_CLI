import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from decimal import Decimal
from .expense import Expense
from .budget import Budget
from .exceptions import StorageError


class StorageHandler:
    def __init__(self,
                 storage_path: str = 'data/expanses.json',
                 budget_path: str = 'data/budgets.json'):
        self.storage_path = Path(storage_path)
        self.budget_path = Path(budget_path)
        self._init_storage()

    def _init_storage(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.storage_path.exists():
                self._save_expanses([])
            if not self.budget_path.exists():
                self._save_budgets([])
        except Exception as e:
            raise StorageError(f"Failed to initalize storage: {str(e)}")

    def _load_expenses(self) -> List[Dict]:
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to load expenses: {str(e)}")

    def _save_expenses(self, expenses: List[Dict]) -> None:
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(expenses, f, indent=2, default=str)
        except Exception as e:
            raise StorageError(f"Failed to save expenses: {str(e)}")

    def _load_budgets(self) -> List[Dict]:
        try:
            with open(self.budget_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to load budgets: {str(e)}")

    def _save_budgets(self, budgets: List[Dict]) -> None:
        try:
            with open(self.budget_path, 'w') as f:
                json.dump(budgets, f, indent=2, default=str)
        except Exception as e:
            raise StorageError(f"Failed to save budgets: {str(e)}")

    def add_expense(self, expense: Expense) -> int:
        expenses = self._load_expenses()
        new_id = max([exp['id'] for exp in expenses], default=0) + 1
        expense_dict = {
            'id': new_id,
            'date': expense.date.isoformat(),
            'description': expense.description,
            'amount': str(expense.amount),
            'category': expense.category
        }
        expenses.append(expense_dict)
        self._save_expenses(expenses)
        return new_id

    def set_budget(self, budget: Budget) -> None:
        budgets = self._load_budgets()
        budget_dict = {
            'month': budget.month,
            'year': budget.year,
            'amount': str(budget.amount),
            'category_limits': {
                k: str(v) for k, v in (budget.category_limits or {}).items()
            }
        }

        # Remove existing budget for month/year if exists
        budget = [b for b in budgets if not (
            b['month'] == budget.month and b['year'] == budget.year)]
        budgets.append(budget_dict)
        self._save_budgets(budgets)

    def get_budget(self, month: int, year: int) -> Optional[Budget]:
        budgets = self._load_budgets()
        budget_dict = next(
            (b for b in budgets if b['month'] == month and b['year'] == year),
            None
        )

        if budget_dict:
            return Budget(
                month=budget_dict['month'],
                year=budget_dict['year'],
                amount=Decimal(budget_dict['amount']),
                category_limits={
                    k: Decimal(v) for k, v in
                    budget_dict['category_limits'].items()
                    }
                if budget_dict.get('category_limits') else None
            )
        return None
