import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from decimal import Decimal
import tempfile
import os
import argparse

from src.expense import Expense
from src.budget import Budget
from src.storage_handler import StorageHandler
from src.expense_manager import ExpenseManager
from src.exceptions import ValidationError, BudgetError
from src.cli_parser import create_parser
from src.main import parse_category_limits, main


# Fixtures
@pytest.fixture
def temp_storage():
    """Fixture providing temporary storage paths for testing."""
    temp_dir = tempfile.mkdtemp()
    expenses_path = os.path.join(temp_dir, "expenses.json")
    budgets_path = os.path.join(temp_dir, "budgets.json")
    storage = StorageHandler(
        storage_path=expenses_path,
        budget_path=budgets_path
    )
    yield storage

    # Cleanup
    for file in [expenses_path, budgets_path]:
        if os.path.exists(file):
            os.remove(file)
    os.rmdir(temp_dir)


@pytest.fixture
def mock_storage():
    """Fixture providing a mocked storage handler."""
    return Mock()


@pytest.fixture
def expense_manager(mock_storage):
    """Fixture providing an ExpenseManager with mocked storage."""
    return ExpenseManager(mock_storage)


# Test Classes
class TestExpense:
    """Tests for the Expense class."""

    def test_valid_expense_creation(self):
        """✓ Should create a valid expense with correct attributes."""
        expense = Expense(
            description="Test expense",
            amount=Decimal("50.00"),
            date=datetime.now(),
            category="groceries"
        )
        assert expense.description == "Test expense"
        assert expense.amount == Decimal("50.00")
        assert expense.category == "groceries"

    def test_invalid_expense_empty_description(self):
        """✗ Should raise ValidationError for empty description."""
        with pytest.raises(ValidationError,
                           match="Description cannot be empty"):
            Expense(
                description="",
                amount=Decimal("50.00"),
                date=datetime.now(),
                category="groceries"
            )

    def test_invalid_expense_negative_amount(self):
        """✗ Should raise ValidationError for negative amount."""
        with pytest.raises(ValidationError,
                           match="Amount must be greater than 0"):
            Expense(
                description="Test expense",
                amount=Decimal("-50.00"),
                date=datetime.now(),
                category="groceries"
            )


class TestBudget:
    """Tests for the Budget class."""

    def test_valid_budget_creation(self):
        """✓ Should create a valid budget with category limits."""
        budget = Budget(
            month=1,
            year=2024,
            amount=Decimal("1000.00"),
            category_limits={"groceries": Decimal("500.00")}
        )
        budget.validate()
        assert budget.month == 1
        assert budget.amount == Decimal("1000.00")

    def test_invalid_budget_month(self):
        """✗ Should raise BudgetError for invalid month."""
        with pytest.raises(BudgetError, match="Invalid month"):
            budget = Budget(month=13, year=2024, amount=Decimal("1000.00"))
            budget.validate()

    def test_invalid_category_limits(self):
        """✗ Should raise BudgetError when category limits exceed total budget."""
        with pytest.raises(BudgetError,
                           match="Sum of category budgets exceeds total budget"):
            budget = Budget(
                month=1,
                year=2024,
                amount=Decimal("1000.00"),
                category_limits={"groceries": Decimal("1200.00")}
            )
            budget.validate()


class TestStorageHandler:
    """Tests for the StorageHandler class."""

    def test_add_and_get_expense(self, temp_storage):
        """✓ Should correctly add and retrieve an expense."""
        expense = Expense(
            description="Test expense",
            amount=Decimal("50.00"),
            date=datetime.now(),
            category="groceries"
        )
        expense_id = temp_storage.add_expense(expense)
        expenses = temp_storage.get_all_expenses()

        assert len(expenses) == 1
        assert expenses[0].description == "Test expense"
        assert expenses[0].id == expense_id

    def test_set_and_get_budget(self, temp_storage):
        """✓ Should correctly set and retrieve a budget."""
        budget = Budget(
            month=1,
            year=2024,
            amount=Decimal("1000.00"),
            category_limits={"groceries": Decimal("500.00")}
        )
        temp_storage.set_budget(budget)

        retrieved_budget = temp_storage.get_budget(1, 2024)
        assert retrieved_budget.amount == Decimal("1000.00")
        assert retrieved_budget.category_limits["groceries"] == \
            Decimal("500.00")


class TestExpenseManager:
    """Tests for the ExpenseManager class."""

    def test_add_expense(self, expense_manager, mock_storage):
        """✓ Should add expense without warnings when under budget."""
        mock_storage.add_expense.return_value = 1
        mock_storage.get_budget.return_value = None

        expense_id, warning = expense_manager.add_expense(
            description="Test expense",
            amount=50.00,
            category="groceries"
        )

        assert expense_id == 1
        assert warning is None
        mock_storage.add_expense.assert_called_once()

    def test_budget_warning(self, expense_manager, mock_storage):
        """✓ Should generate warning when expense exceeds budget."""
        mock_storage.add_expense.return_value = 1
        mock_storage.get_budget.return_value = Budget(
            month=datetime.now().month,
            year=datetime.now().year,
            amount=Decimal("100.00"),
            category_limits={"groceries": Decimal("50.00")}
        )
        mock_storage.get_all_expenses.return_value = [
            Expense(
                description="Previous expense",
                amount=Decimal("90.00"),
                date=datetime.now(),
                category="groceries",
                id=1
            )
        ]

        expense_id, warning = expense_manager.add_expense(
            description="Test expense",
            amount=20.00,
            category="groceries"
        )

        assert warning is not None
        assert "budget" in warning.lower()


class TestCategoryLimitsParser:
    """Tests for the category limits parser."""

    def test_valid_category_limits(self):
        """✓ Should correctly parse valid category limits string."""
        limits = parse_category_limits("groceries:500.00,utilities:200.00")
        assert limits["groceries"] == 500.00
        assert limits["utilities"] == 200.00

    def test_invalid_category_limits_format(self):
        """✗ Should raise ValidationError for invalid format."""
        with pytest.raises(ValidationError):
            parse_category_limits("invalid:format:500")

    def test_empty_category_limits(self):
        """✓ Should return empty dict for empty input."""
        limits = parse_category_limits("")
        assert limits == {}


class TestCliParser:
    """Tests for the CLI argument parser."""

    def test_create_parser(self):
        """✓ Should create parser with all required commands."""
        parser = create_parser()

        # Check if all commands are present
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ]
        commands = subparsers_actions[0].choices.keys()

        assert 'add' in commands
        assert 'set-budget' in commands
        assert 'category-summary' in commands
        assert 'export' in commands

    def test_add_expense_command(self):
        """✓ Should correctly parse add expense command."""
        parser = create_parser()
        args = parser.parse_args([
            'add',
            '--description', 'Test expense',
            '--amount', '50.00',
            '--category', 'groceries'
        ])

        assert args.command == 'add'
        assert args.description == 'Test expense'
        assert args.amount == 50.00
        assert args.category == 'groceries'

    def test_set_budget_command(self):
        """✓ Should correctly parse set budget command."""
        parser = create_parser()
        args = parser.parse_args([
            'set-budget',
            '--month', '1',
            '--year', '2024',
            '--amount', '1000.00',
            '--category-limits', 'groceries:500.00,utilities:200.00'
        ])

        assert args.command == 'set-budget'
        assert args.month == 1
        assert args.year == 2024
        assert args.amount == 1000.00
        assert args.category_limits == 'groceries:500.00,utilities:200.00'

    def test_category_summary_command(self):
        """✓ Should correctly parse category summary command."""
        parser = create_parser()
        args = parser.parse_args([
            'category-summary',
            '--category', 'groceries',
            '--month', '1',
            '--year', '2024'
        ])

        assert args.command == 'category-summary'
        assert args.category == 'groceries'
        assert args.month == 1
        assert args.year == 2024

    def test_export_command(self):
        """✓ Should correctly parse export command."""
        parser = create_parser()
        args = parser.parse_args([
            'export',
            '--output', 'expenses.csv'
        ])

        assert args.command == 'export'
        assert args.output == 'expenses.csv'

    def test_invalid_command(self):
        """✗ Should exit on invalid command."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(['invalid-command'])


class TestMain:
    """Tests for the main program functionality."""

    @patch('src.main.StorageHandler')
    @patch('src.main.ExpenseManager')
    def test_add_expense_success(self, mock_manager_class, mock_storage_class):
        """✓ Should successfully add expense."""
        # Setup mocks
        mock_storage = Mock()
        mock_manager = Mock()
        mock_storage_class.return_value = mock_storage
        mock_manager_class.return_value = mock_manager
        mock_manager.add_expense.return_value = (1, None)

        # Run with test arguments
        with patch('sys.argv', [
            'main.py',
            'add',
            '--description', 'Test expense',
            '--amount', '50.00',
            '--category', 'groceries'
        ]):
            with patch('builtins.print') as mock_print:
                main()

        # Verify
        mock_manager.add_expense.assert_called_once_with(
            description='Test expense',
            amount=50.00,
            category='groceries'
        )
        mock_print.assert_called_with("Expense added successfully (ID: 1)")

    @patch('src.main.StorageHandler')
    @patch('src.main.ExpenseManager')
    def test_set_budget_success(self, mock_manager_class, mock_storage_class):
        """✓ Should successfully set budget."""
        # Setup mocks
        mock_storage = Mock()
        mock_manager = Mock()
        mock_storage_class.return_value = mock_storage
        mock_manager_class.return_value = mock_manager

        # Run with test arguments
        with patch('sys.argv', [
            'main.py',
            'set-budget',
            '--month', '1',
            '--year', '2024',
            '--amount', '1000.00',
            '--category-limits', 'groceries:500.00'
        ]):
            with patch('builtins.print') as mock_print:
                main()

        # Verify
        mock_manager.set_budget.assert_called_once()
        mock_print.assert_called_with("Budget set successfully for 1/2024")

    @patch('src.main.StorageHandler')
    @patch('src.main.ExpenseManager')
    def test_category_summary_success(self, mock_manager_class,
                                      mock_storage_class):
        """✓ Should successfully show category summary."""
        # Setup mocks
        mock_storage = Mock()
        mock_manager = Mock()
        mock_storage_class.return_value = mock_storage
        mock_manager_class.return_value = mock_manager
        mock_manager.get_category_summary.return_value = Decimal('150.00')

        # Run with test arguments
        with patch('sys.argv', [
            'main.py',
            'category-summary',
            '--category', 'groceries',
            '--month', '1',
            '--year', '2024'
        ]):
            with patch('builtins.print') as mock_print:
                main()

        # Verify
        mock_manager.get_category_summary.assert_called_once()
        mock_print.assert_called_once()

    def test_parse_category_limits_valid(self):
        """✓ Should correctly parse valid category limits."""
        result = parse_category_limits("groceries:500.00,utilities:200.00")
        assert result == {'groceries': 500.00, 'utilities': 200.00}

    def test_parse_category_limits_invalid(self):
        """✗ Should raise ValidationError for invalid format."""
        with pytest.raises(ValidationError):
            parse_category_limits("invalid:format:500")

    @patch('src.main.StorageHandler')
    @patch('src.main.ExpenseManager')
    def test_validation_error_handling(self, mock_manager_class,
                                       mock_storage_class):
        """✓ Should handle ValidationError appropriately."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.add_expense.side_effect = ValidationError("Test error")

        with patch('sys.argv', [
            'main.py',
            'add',
            '--description', 'Test',
            '--amount', '50.00',
            '--category', 'groceries'
        ]):
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
            mock_print.assert_called_with("Validation Error: Test error")

    @patch('src.main.StorageHandler')
    @patch('src.main.ExpenseManager')
    def test_budget_error_handling(self, mock_manager_class,
                                   mock_storage_class):
        """✓ Should handle BudgetError appropriately."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.set_budget.side_effect = BudgetError("Test error")

        with patch('sys.argv', [
            'main.py',
            'set-budget',
            '--month', '1',
            '--year', '2024',
            '--amount', '1000.00'
        ]):
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
            mock_print.assert_called_with("Budget Error: Test error")
