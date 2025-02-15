class ExpenseTrackerError(Exception):
    """Base exception for expense tracker errors"""
    pass


class ValidationError(ExpenseTrackerError):
    """Raised when input validation fails"""
    pass


class BudgetError(ExpenseTrackerError):
    """Raised when budget-related operations fail"""
    pass


class StorageError(ExpenseTrackerError):
    """Raised when storage operations fail"""
    pass
