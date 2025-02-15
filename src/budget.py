from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
from .exceptions import BudgetError


@dataclass
class Budget:
    month: int
    year: int
    amount: Decimal
    category_limits: Optional[Dict[str, Decimal]] = None

    def validate(self):
        if self.month < 1 or self.month > 12:
            raise BudgetError("Invalid month")
        if self.amount <= 0:
            raise BudgetError("Budget amount must be greater than 0")
        if self.category_limits:
            if sum(self.category_limits.values()) > self.amount:
                raise BudgetError(
                    "Sum of category budgets exceeds total budget")
