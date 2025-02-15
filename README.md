# Expense Tracker CLI

A powerful command-line interface application for managing personal expenses and budgets with support for category-based tracking and budget warnings.

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)

Project inspired by [Roadmap.sh Expense Tracker Project](https://roadmap.sh/projects/expense-tracker)

## Features

- Track expenses with descriptions, amounts, and categories
- Set monthly budgets with category-specific limits
- Get warnings when expenses exceed budget limits
- Generate category-wise expense summaries
- Export expenses to CSV format
- Persistent storage using JSON files
- Robust error handling and input validation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AdamSzczotka/Expanse_tracker_CLI
cd Expanse_tracker_CLI
```

2. Set up a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Adding an Expense
```bash
python -m src.main add --description "Grocery shopping" --amount 50.00 --category groceries
```

### Setting a Monthly Budget
```bash
python -m src.main set-budget --month 1 --year 2024 --amount 1000.00 --category-limits "groceries:500.00,utilities:200.00"
```

### Viewing Category Summary
```bash
python -m src.main category-summary --category groceries --month 1 --year 2024
```

### Exporting Expenses
```bash
python -m src.main export --output expenses.csv
```

## Command Details

### Add Expense
- `--description`: Description of the expense (required)
- `--amount`: Amount spent (required)
- `--category`: Category of expense (required)

### Set Budget
- `--month`: Month number (1-12) (required)
- `--year`: Year (required)
- `--amount`: Total budget amount (required)
- `--category-limits`: Category-wise limits in format "category1:amount1,category2:amount2"

### Category Summary
- `--category`: Category name (required)
- `--month`: Month number (optional)
- `--year`: Year (optional)

### Export
- `--output`: Output file path (required)

## Data Storage

The application stores data in JSON format:
- Expenses: `data/expenses.json`
- Budgets: `data/budgets.json`

## Development

### Running Tests
```bash
pytest tests/
```

### Project Structure
```
EXPENSE_TRACKER_CLI
├── data/
│   ├── budgets.json
│   └── expenses.json
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── budget.py
│   ├── cli_parser.py
│   ├── exceptions.py
│   ├── expense_manager.py
│   ├── expense.py
│   └── storage_handler.py
├── tests/
│   ├── __init__.py
│   └── test_expense_tracker.py
├── data/
│   ├── budgets.json
│   └── expenses.json
├── LICENSE
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Adam Szczotka
