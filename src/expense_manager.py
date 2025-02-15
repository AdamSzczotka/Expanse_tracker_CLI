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
