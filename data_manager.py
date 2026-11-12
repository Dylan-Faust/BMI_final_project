import csv
import os

CSV_FILE = 'portfolio_companies.csv'

def load_data():
    portfolio_companies = {}
    if not os.path.exists(CSV_FILE):
        print(f">> No '{CSV_FILE}' found. Generating new database with default portfolio...")
        portfolio_companies = {
            "CAT": {"ttm_ebitda": 8500000, "total_cash": 6500000, "book_value": 90000000, "funded_debt": 25000000, "max_leverage": 4.0, "revolver_limit": 9000000},
            "DE": {"ttm_ebitda": 12000000, "total_cash": 8000000, "book_value": 120000000, "funded_debt": 30000000, "max_leverage": 3.5, "revolver_limit": 12000000},
            "URI": {"ttm_ebitda": 5000000, "total_cash": 1500000, "book_value": 50000000, "funded_debt": 10000000, "max_leverage": 4.5, "revolver_limit": 5000000}
        }
        save_data(portfolio_companies)
    else:
        with open(CSV_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                ticker = row['Ticker']
                portfolio_companies[ticker] = {
                    "ttm_ebitda": int(float(row['ttm_ebitda'])) if row['ttm_ebitda'] else 0,
                    "total_cash": int(float(row['total_cash'])) if row['total_cash'] else 0,
                    "book_value": int(float(row['book_value'])) if row['book_value'] else 0,
                    "funded_debt": int(float(row['funded_debt'])) if row['funded_debt'] else 0,
                    "max_leverage": float(row['max_leverage']) if row['max_leverage'] else 0.0,
                    "revolver_limit": float(row['revolver_limit']) if row['revolver_limit'] else 0.0
                }
    return portfolio_companies

def save_data(portfolio_companies):
    with open(CSV_FILE, mode='w', newline='') as file:
        fieldnames = ['Ticker', 'ttm_ebitda', 'total_cash', 'book_value', 'funded_debt', 'max_leverage', 'revolver_limit']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for ticker, details in portfolio_companies.items():
            row = {'Ticker': ticker}
            row.update(details)
            writer.writerow(row)