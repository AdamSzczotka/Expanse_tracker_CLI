class ExpanseTrackerError(Exception):
    """Base exception for expanse tracker errors"""
    pass


class ValidationError(ExpanseTrackerError):
    """Raised when input validation fails"""
    pass


class BudgetError(ExpanseTrackerError):
    """Raised when budget-related operations fail"""
    pass


class StorageError(ExpanseTrackerError):
    """Raised when storage operations fail"""
    pass
