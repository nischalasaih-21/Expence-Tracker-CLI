# Expense Tracker CLI

A command-line expense tracking application built using Python to manage income and expenses, generate monthly financial summaries, and export reports.

## Features

- Add income and expense transactions.
- Record dates, categories, amounts, and descriptions.
- Store transaction data persistently using SQLite.
- View all recorded transactions.
- Generate monthly income, expense, and net savings summaries.
- Analyze expenses by category.
- Export transaction data to CSV.
- Export transactions and monthly summaries to Excel.
- Generate expense visualization charts using Matplotlib.
- Validate dates and transaction amounts.

## Technologies Used

- Python
- SQLite
- Pandas
- OpenPyXL
- Matplotlib

## Project Structure

expense-tracker-cli/
├── main.py
├── requirements.txt
├── README.md
├── expenses.db
└── exports/

## Installation

1. Clone this repository or download the project files.
2. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python main.py
   ```

## How It Works

Users interact with the application through a menu-driven CLI. Transactions are saved in an SQLite database, allowing data to persist between sessions. Pandas processes transaction data and creates summaries, while OpenPyXL and Matplotlib support Excel exports and chart generation.

## Learning Outcomes

This project demonstrates file handling, database operations, date validation, data aggregation, exception handling, CSV and Excel exports, and basic data visualization.

## Future Improvements

- Add transaction editing and deletion.
- Add category budgets and spending limits.
- Generate PDF financial reports.
- Add password protection and user accounts.

## Author

Developed as a Python programming project.

