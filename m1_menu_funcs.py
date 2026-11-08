import yfinance as yf

# Main dictionary representing portfolio... will be represented in a csv file in the future
portfolio_companies = {
    "CAT": {"ttm_ebitda": 8500000, "funded_debt": 25000000, "max_leverage": 4.0, "revolver_limit": 9000000},
    "DE": {"ttm_ebitda": 12000000, "funded_debt": 30000000, "max_leverage": 3.5, "revolver_limit": 12000000},
    "URI": {"ttm_ebitda": 5000000, "funded_debt": 10000000, "max_leverage": 4.5, "revolver_limit": 12500000}
}
#allows the user to view portfolio and current fincial information
def view_companies():
    print("\n--- Current Portfolio Companies (Live Data) ---")
    for ticker, details in portfolio_companies.items():
        stock = yf.Ticker(ticker)
        info_dict = stock.info
        live_ebitda = info_dict.get('ebitda', None)
        
        display_ebitda = live_ebitda if live_ebitda else details['ttm_ebitda']
        
        # Dynamically recalculate the revolver limit in case the live EBITDA changed
        revolver_capacity = (details['max_leverage'] * display_ebitda) - details['funded_debt']
        dynamic_revolver = max(0, revolver_capacity)
        
        print(f"\nTicker: {ticker}")
        print(f"  TTM EBITDA: ${display_ebitda:,.0f} {'(Live)' if live_ebitda else '(Manual)'}")
        print(f"  Funded Debt: ${details['funded_debt']:,.0f}")
        print(f"  Max Leverage Ratio: {details['max_leverage']}x")
        print(f"  Calculated Revolver Limit: ${dynamic_revolver:,.0f}")
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
                
    print("\n>> Enter internal banking covenants & debt:")
    while True:
        debt_input = input(f"Enter Current Funded Debt for {ticker} (whole number): ").strip()
        if debt_input.isdigit():
            funded_debt = int(debt_input)
            break
        else:
            print("Invalid input. Please enter a numeric value.")
            
    while True:
        leverage_input = input(f"Enter Max Leverage Ratio for {ticker} (e.g., 4.0): ").strip()
        if leverage_input.replace('.', '', 1).isdigit():
            leverage = float(leverage_input)
            break
        else:
            print("Invalid input. Please enter a decimal or whole number.")
            
    # Calculate the revolver limit mathematically based on inputs
    revolver_capacity = (leverage * ebitda) - funded_debt
    revolver_limit = max(0, revolver_capacity)
            
    portfolio_companies[ticker] = {
        "ttm_ebitda": ebitda,
        "funded_debt": funded_debt,
        "max_leverage": leverage,
        "revolver_limit": revolver_limit
    }
    print(f"\nSuccess! Financials and covenants for {ticker} have been saved.")
    print(f">> Dynamically Calculated Revolver Capacity: ${revolver_limit:,.0f}")

def refresh_live_data():
    print("\n>> Fetching live API data to update dictionary...")
    for ticker, details in portfolio_companies.items():
        stock = yf.Ticker(ticker)
        live_ebitda = stock.info.get('ebitda')
        
        if live_ebitda:
            # Update the stored EBITDA and recalculate the stored revolver limit
            portfolio_companies[ticker]['ttm_ebitda'] = live_ebitda
            revolver_capacity = (details['max_leverage'] * live_ebitda) - details['funded_debt']
            portfolio_companies[ticker]['revolver_limit'] = max(0, revolver_capacity)
            
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