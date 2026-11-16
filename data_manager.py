import csv
import os
import pandas as pd
import pandas_datareader.data as web
from datetime import datetime

CSV_FILE = 'portfolio_companies.csv'

def load_data():
    portfolio_companies = {}
    if not os.path.exists(CSV_FILE):
        print(f">> No '{CSV_FILE}' found. Generating new database with default portfolio...")

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

def fetch_macro_data(start_date='1990-01-01'):
    """
    Pulls historical macroeconomic shocks from the FRED API to use as 
    exogenous training data for the SARIMAX & XGBoost models.
    """
    print("\n>> Fetching macroeconomic training data from FRED...")
    try:
        end_date = datetime.today().strftime('%Y-%m-%d')
        
        # FRED Series IDs: 
        # SOFR = Secured Overnight Financing Rate (Interest rates)
        # WPUSI012011 = Producer Price Index for Construction Materials (Inflation/Supply Chain)
        tickers = ['SOFR', 'WPUSI012011']
        
        macro_df = web.DataReader(tickers, 'fred', start_date, end_date)
        macro_df.columns = ['SOFR_Rate', 'Material_PPI']
        
        # Forward-fill and drop empty rows to align daily/monthly datasets
        macro_df = macro_df.ffill().dropna()
        
        print(f">> Success! Retrieved {len(macro_df)} days of macroeconomic data.")
        return macro_df
        
    except Exception as e:
        print(f">> Error fetching FRED data. Error: {e}")
        return None