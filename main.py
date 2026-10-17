
import sqlite3
import csv
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# -------------------- CONFIGURATION --------------------

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "expenses.db"
EXPORT_DIR = BASE_DIR / "exports"

EXPORT_DIR.mkdir(exist_ok=True)

DATE_FORMAT = "%Y-%m-%d"


# -------------------- DATABASE SETUP --------------------

def get_connection():
    return sqlite3.connect(DB_FILE)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                transaction_type TEXT NOT NULL
                    CHECK(transaction_type IN ('Income', 'Expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT DEFAULT ''
            )
        """)
    print("Database initialized successfully.")


# -------------------- INPUT VALIDATION --------------------

def get_valid_date():
    while True:
        date_text = input("Enter date (YYYY-MM-DD): ").strip()

        try:
            parsed_date = datetime.strptime(date_text, DATE_FORMAT)

            if parsed_date.strftime(DATE_FORMAT) != date_text:
                raise ValueError

            return date_text

        except ValueError:
            print("Invalid date. Example: 2026-10-09")


def get_valid_amount():
    while True:
        try:
            amount = float(input("Enter amount (₹): ").strip())

            if amount <= 0:
                print("Amount must be greater than zero.")
                continue

            if not amount < float("inf"):
                print("Enter a valid finite amount.")
                continue

            return round(amount, 2)

        except ValueError:
            print("Enter a valid number, such as 250.50.")


# -------------------- ADD TRANSACTION --------------------

def add_transaction():
    print("\n--- Add Transaction ---")

    date = get_valid_date()

    print("1. Income")
    print("2. Expense")

    while True:
        choice = input("Choose transaction type: ").strip()

        if choice == "1":
            transaction_type = "Income"
            break
        elif choice == "2":
            transaction_type = "Expense"
            break
        else:
            print("Please enter 1 or 2.")

    category = input("Enter category (e.g. Food, Travel, Salary): ").strip()

    if not category:
        print("Category cannot be empty.")
        return

    amount = get_valid_amount()
    description = input("Enter description (optional): ").strip()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO transactions
            (date, transaction_type, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
        """, (date, transaction_type, category, amount, description))

    print("Transaction added successfully!")


# -------------------- READ TRANSACTIONS --------------------

def fetch_transactions():
    with get_connection() as conn:
        df = pd.read_sql_query("""
            SELECT id, date, transaction_type, category,
                   amount, description
            FROM transactions
            ORDER BY date DESC, id DESC
        """, conn)

    return df


def view_transactions():
    print("\n--- All Transactions ---")

    df = fetch_transactions()

    if df.empty:
        print("No transactions found.")
        return

    print(df.to_string(index=False))


# -------------------- MONTHLY SUMMARY --------------------

def get_month():
    while True:
        month = input("Enter month (YYYY-MM): ").strip()

        try:
            parsed = datetime.strptime(month, "%Y-%m")

            if parsed.strftime("%Y-%m") != month:
                raise ValueError

            return month

        except ValueError:
            print("Invalid month. Example: 2026-10")


def monthly_summary():
    print("\n--- Monthly Summary ---")

    month = get_month()
    df = fetch_transactions()

    if df.empty:
        print("No transactions recorded yet.")
        return

    df = df[df["date"].str.startswith(month)]

    if df.empty:
        print(f"No transactions found for {month}.")
        return

    income = df.loc[
        df["transaction_type"] == "Income", "amount"
    ].sum()

    expenses = df.loc[
        df["transaction_type"] == "Expense", "amount"
    ].sum()

    balance = income - expenses

    print(f"\nMonth: {month}")
    print(f"Total Income:   ₹{income:,.2f}")
    print(f"Total Expenses: ₹{expenses:,.2f}")
    print(f"Net Savings:    ₹{balance:,.2f}")

    expense_data = df[df["transaction_type"] == "Expense"]

    if not expense_data.empty:
        print("\nExpenses by Category:")
        category_totals = expense_data.groupby("category")[
            "amount"
        ].sum().sort_values(ascending=False)

        for category, amount in category_totals.items():
            print(f"{category}: ₹{amount:,.2f}")


# -------------------- EXPORT TO CSV --------------------

def export_csv():
    print("\n--- Export Transactions to CSV ---")

    df = fetch_transactions()

    if df.empty:
        print("No transactions to export.")
        return

    filename = EXPORT_DIR / "transactions.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"CSV exported successfully: {filename}")


# -------------------- EXPORT TO EXCEL --------------------

def export_excel():
    print("\n--- Export Reports to Excel ---")

    df = fetch_transactions()

    if df.empty:
        print("No transactions to export.")
        return

    df["date"] = pd.to_datetime(df["date"])

    income = df[df["transaction_type"] == "Income"]
    expenses = df[df["transaction_type"] == "Expense"]

    monthly = df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)

    income_summary = income.assign(
        month=income["date"].dt.to_period("M").astype(str)
    ).groupby("month")["amount"].sum().rename("income")

    expense_summary = expenses.assign(
        month=expenses["date"].dt.to_period("M").astype(str)
    ).groupby("month")["amount"].sum().rename("expenses")

    summary = pd.concat(
        [income_summary, expense_summary], axis=1
    ).fillna(0)

    summary["net_savings"] = summary["income"] - summary["expenses"]
    summary = summary.reset_index()

    filename = EXPORT_DIR / "expense_report.xlsx"

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Transactions", index=False)
        summary.to_excel(writer, sheet_name="Monthly Summary", index=False)

    print(f"Excel report exported successfully: {filename}")


# -------------------- GENERATE EXPENSE CHART --------------------

def generate_chart():
    print("\n--- Generate Expense Chart ---")

    month = get_month()
    df = fetch_transactions()

    if df.empty:
        print("No transactions available.")
        return

    df = df[
        (df["date"].str.startswith(month)) &
        (df["transaction_type"] == "Expense")
    ]

    if df.empty:
        print(f"No expenses found for {month}.")
        return

    category_totals = df.groupby("category")["amount"].sum()
    category_totals = category_totals.sort_values(ascending=False)

    plt.figure(figsize=(9, 5))
    category_totals.plot(kind="bar", edgecolor="black")

    plt.title(f"Expenses by Category - {month}")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()

    filename = EXPORT_DIR / f"expenses_{month}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Chart saved successfully: {filename}")


# -------------------- MAIN MENU --------------------

def main():
    initialize_database()

    while True:
        print("\n" + "=" * 42)
        print("       EXPENSE TRACKER CLI")
        print("=" * 42)
        print("1. Add Income / Expense")
        print("2. View All Transactions")
        print("3. Monthly Summary")
        print("4. Export Transactions to CSV")
        print("5. Export Report to Excel")
        print("6. Generate Expense Chart")
        print("7. Exit")

        choice = input("\nEnter your choice (1-7): ").strip()

        try:
            if choice == "1":
                add_transaction()
            elif choice == "2":
                view_transactions()
            elif choice == "3":
                monthly_summary()
            elif choice == "4":
                export_csv()
            elif choice == "5":
                export_excel()
            elif choice == "6":
                generate_chart()
            elif choice == "7":
                print("Thank you for using Expense Tracker!")
                break
            else:
                print("Invalid choice. Please select 1-7.")

        except (sqlite3.Error, OSError, ValueError, OverflowError) as error:
            print(f"Operation failed: {error}")


if __name__ == "__main__":
    main()
1