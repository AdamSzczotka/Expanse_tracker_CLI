from typing import Dict
from src.expense_manager import ExpenseManager
from src.storage_handler import StorageHandler
from src.cli_parser import create_parser
from src.exceptions import ValidationError, BudgetError, StorageError


def parse_category_limits(limits_str: str) -> Dict[str, float]:
    if not limits_str:
        return {}
    try:
        return {
            category: float(amount)
            for category, amount in
            (pair.split(':') for pair in limits_str.split(','))
        }
    except Exception:
        raise ValidationError("Invalid category limits format. "
                              "Use 'category1:amount1,category2:amount2'")


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        storage = StorageHandler()
        manager = ExpenseManager(storage)

        if args.command == 'add':
            expense_id, warning = manager.add_expense(
                description=args.description,
                amount=args.amount,
                category=args.category
            )
            print(f"Expense added successfully (ID: {expense_id})")
            if warning:
                print(f"Warning: {warning}")

        elif args.command == 'set-budget':
            category_limits = (
                parse_category_limits(args.category_limits)
                if args.category_limits
                else None
            )
            manager.set_budget(
                month=args.month,
                year=args.year,
                amount=args.amount,
                category_limits=category_limits
            )
            print(f"Budget set successfully for {args.month}/{args.year}")

        elif args.command == 'category-summary':
            total = manager.get_category_summary(
                category=args.category,
                month=args.month,
                year=args.year
            )
            period = (f"for {args.month}/{args.year}"
                      if args.month and args.year
                      else "(all time)")
            print(f"Total expenses for category '{args.category}' "
                  f"{period}: ${float(total):.2f}")

        elif args.command == 'export':
            manager.export_to_csv(args.output)
            print(f"Expenses exported successfully to {args.output}")

    except ValidationError as e:
        print(f"Validation Error: {str(e)}")
        exit(1)
    except BudgetError as e:
        print(f"Budget Error: {str(e)}")
        exit(1)
    except StorageError as e:
        print(f"Storage Error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
