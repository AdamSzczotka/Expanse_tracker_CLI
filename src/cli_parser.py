import argparse


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Expense Tracker CLI')
    subparsers = parser.add_subparsers(dest='command',
                                       help='Available commands')

    # Add expense
    add_parser = subparsers.add_parser('add', help='Add a new expense')
    add_parser.add_argument('--description', required=True,
                            help='Expense description')
    add_parser.add_argument('--amount', required=True, type=float,
                            help='Expense amount')
    add_parser.add_argument('--category', required=True,
                            help='Expense category')

    # Set budget
    budget_parser = subparsers.add_parser('set-budget',
                                          help='Set monthly budget')
    budget_parser.add_argument('--month', required=True, type=int,
                               help='Month (1-12)')
    budget_parser.add_argument('--year', required=True, type=int, help='Year')
    budget_parser.add_argument('--amount', required=True, type=float,
                               help='Budget amount')
    budget_parser.add_argument('--category-limits', type=str,
                               help='Category limits in format'
                               '"category1:amount1,category2:amount2"')

    # Category summary
    category_parser = subparsers.add_parser('category-summary',
                                            help='Show category summary')
    category_parser.add_argument('--category', required=True,
                                 help='Category name')
    category_parser.add_argument('--month', type=int, help='Month (1-12)')
    category_parser.add_argument('--year', type=int, help='Year')

    # Export
    export_parser = subparsers.add_parser('export',
                                          help='Export expenses to CSV')
    export_parser.add_argument('--output', required=True,
                               help='Output file path')

    return parser
