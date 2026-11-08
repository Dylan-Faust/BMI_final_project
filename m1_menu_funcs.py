import yfinance as yf

# Main dictionary holding portfolio companies
portfolio_companies = {
    "CAT": {"ttm_ebitda": 8500000, "revolver_limit": 50000000, "max_leverage": 4.0},
    "DE": {"ttm_ebitda": 12000000, "revolver_limit": 75000000, "max_leverage": 3.5},
    "URI": {"ttm_ebitda": 5000000, "revolver_limit": 25000000, "max_leverage": 4.5}
}

# Function to view all current portfolio companies and their financial constraints
def view_companies():
    print("\n--- Current Portfolio Companies (Live Data) ---")
    for ticker, details in portfolio_companies.items():
        # Fetch live data for each ticker in the dictionary
        stock = yf.Ticker(ticker)
        info_dict = stock.info
        live_ebitda = info_dict.get('ebitda', None)
        
        # Use live data if available, otherwise fallback to the stored static data
        display_ebitda = live_ebitda if live_ebitda else details['ttm_ebitda']
        
        print(f"\nTicker: {ticker}")
        print(f"  TTM EBITDA: ${display_ebitda:,} {'(Live)' if live_ebitda else '(Manual)'}")
        print(f"  Revolver Limit: ${details['revolver_limit']:,}")
        print(f"  Max Leverage Ratio: {details['max_leverage']}x")
    print("\n-----------------------------------")

def add_update_company():
    print("\n--- Add or Update Company Financials ---")
    ticker = input("Enter company ticker symbol (e.g., AAPL): ").strip().upper()
    
    print(f"\n>> Fetching live financial data for {ticker} via Yahoo Finance API...")
    
    stock = yf.Ticker(ticker)
    info_dict = stock.info
    ebitda = info_dict.get('ebitda', None)
        
    if ebitda:
        print(f">> Success! Retrieved TTM EBITDA: ${ebitda:,}")
    else:
        print(">> EBITDA not found on Yahoo Finance. Switching to manual entry.")
        
    if not ebitda:
        while True:
            ebitda_input = input(f"Enter TTM EBITDA for {ticker} (whole number): ").strip()
            if ebitda_input.isdigit():
                ebitda = int(ebitda_input)
                break
            else:
                print("Invalid input. Please enter a numeric value.")
                
    print("\n>> Enter internal banking covenants:")
    while True:
        revolver_input = input(f"Enter Revolver Limit for {ticker} (whole number): ").strip()
        if revolver_input.isdigit():
            revolver = int(revolver_input)
            break
        else:
            print("Invalid input. Please enter a numeric value.")
    
def refresh_live_data():
    print("\n>> Fetching live API data to update dictionary...")
    for ticker in portfolio_companies.keys():
        stock = yf.Ticker(ticker)
        live_ebitda = stock.info.get('ebitda')
        
        # Overwrite the dictionary value if the API returns a valid number
        if live_ebitda:
            portfolio_companies[ticker]['ttm_ebitda'] = live_ebitda
            print(f"Updated {ticker} EBITDA to ${live_ebitda:,}")
        else:
            print(f"No live EBITDA found for {ticker}. Keeping current data.")
            
    print(">> Dictionary update complete.\n")

def manage_financials_menu():
    while True:
        print("\n--- Manage Company Financials ---")
        print("1. View Current Company Financials")
        print("2. Add or Update a Company")
        print("3. Refresh Live API Data")
        print("4. Return to Main Menu")
        print("---------------------------------")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            view_companies()
        elif choice == '2':
            add_update_company()
        elif choice == '3':
            refresh_live_data()
        elif choice == '4':
            break
        else:
            print("Invalid option. Please choose a number from 1 to 4.")