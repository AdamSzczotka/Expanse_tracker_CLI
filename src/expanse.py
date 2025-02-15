from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from .exceptions import ValidationError


@dataclass
class Expane:
    description: str
    amount: Decimal
    date: datetime
    category: str
    id: Optional[int] = None

    def __post_init__(self):
        self.validiate()

    def validiate(self):
        if not self.description or len(self.description.strip()) == 0:
            raise ValidationError("Description cannot be empty")
        if len(self.description) > 100:
            raise ValidationError(
                "Description must be less than 100 characters"
            )
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than 0")
        if not self.category:
            raise ValidationError("Category is required")
