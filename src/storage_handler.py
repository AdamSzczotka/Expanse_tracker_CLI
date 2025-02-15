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
