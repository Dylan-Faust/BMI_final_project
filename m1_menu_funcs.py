import yfinance as yf
from data_manager import load_data, save_data

# Execute load_data() immediately and store it in our dictionary
portfolio_companies = load_data()

#allows the user to view portfolio and current fincial information
def view_companies():
    print("\n--- Current Portfolio Companies (Live Data) ---")
    for ticker, details in portfolio_companies.items():
        stock = yf.Ticker(ticker)
        info_dict = stock.info
        live_ebitda = info_dict.get('ebitda', None)
        live_cash = info_dict.get('totalCash', None)

        # Calculate Total Book Value (Book Value Per Share * Shares Outstanding)
        bv_per_share = info_dict.get('bookValue')
        shares_outstanding = info_dict.get('sharesOutstanding')
        total_book_value = bv_per_share * shares_outstanding if bv_per_share and shares_outstanding else None

        display_ebitda = live_ebitda if live_ebitda else details['ttm_ebitda']
        display_cash = live_cash if live_cash else details['total_cash']
        
       # Calculate Net Debt (cannot be less than $0)
        net_debt = max(0, details['funded_debt'] - display_cash)

        # Calculate new capacity using Net Debt instead of Gross Debt
        revolver_capacity = (details['max_leverage'] * display_ebitda) - net_debt
        dynamic_revolver = max(0, revolver_capacity)
        
        print(f"\nTicker: {ticker}")
        print(f"  TTM EBITDA: ${display_ebitda:,.0f} {'(Live)' if live_ebitda else '(Manual)'}")
        print(f"  Total Cash: ${display_cash:,.0f} {'(Live)' if live_cash else '(Manual)'}")
        print(f"  Funded Debt: ${details['funded_debt']:,.0f}")
        print(f"  Net Debt: ${net_debt:,.0f}")
        print(f"  Max Leverage Ratio: {details['max_leverage']}x")
        print(f"  Calculated Revolver Limit: ${dynamic_revolver:,.0f}")
    print("\n-----------------------------------")

def add_update_company():#updates or adds a new company to the portfolio dictionary
    print("\n--- Add or Update Company Financials ---")
    ticker = input("Enter company ticker symbol (e.g., AAPL): ").strip().upper()
    
    print(f"\n>> Fetching live financial data for {ticker} via Yahoo Finance API...")
    
    stock = yf.Ticker(ticker)
    info_dict = stock.info

    ebitda = info_dict.get('ebitda')
    total_cash = info_dict.get('totalCash')
    bv_per_share = info_dict.get('bookValue')
    shares = info_dict.get('sharesOutstanding')    
    book_value = (bv_per_share * shares) if (bv_per_share and shares) else None

    if ebitda and total_cash and book_value:
        print(f"\n>> Successfully retrieved live data for {ticker}:")
        print(f"  TTM EBITDA: ${ebitda:,.0f}")
        print(f"  Total Cash: ${total_cash:,.0f}")
        print(f"  Total Book Value: ${book_value:,.0f}")  
    else:
        print(">> Incomplete data found on Yahoo Finance. Switching to manual entry for missing metrics.")

        #fall back to manual entry for missing metrics
    if not ebitda:
        while True:
            ebitda_input = input(f"Enter TTM EBITDA for {ticker} (whole number): ").strip()
            if ebitda_input.isdigit():
                ebitda = int(ebitda_input)
                break
            else:
                print("Invalid input. Please enter a numeric value.")

    if not book_value:
        while True:
            bv_input = input(f"Enter Total Book Value for {ticker} (whole number): ").strip()
            if bv_input.isdigit():
                book_value = int(bv_input)
                break
            else:
                print("Invalid input.")            

    if not total_cash:
        while True:
            cash_input = input(f"Enter Total Cash for {ticker} (whole number): ").strip()
            if cash_input.isdigit():
                total_cash = int(cash_input)
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
            
   # Calculate Net Debt and Revolver Limit
    net_debt = max(0, funded_debt - total_cash)
    revolver_limit = book_value * 0.10
            
    portfolio_companies[ticker] = {
        "ttm_ebitda": ebitda,
        "funded_debt": funded_debt,
        "total_cash": total_cash,
        "book_value": book_value,
        "max_leverage": leverage,
        "revolver_limit": revolver_limit
    }
    save_data(portfolio_companies)
    print(f"\nSuccess! Financials and covenants for {ticker} have been saved.")
    print(f">> Dynamically Calculated Revolver Capacity: ${revolver_limit:,.0f}")

#updates the dictionary with live data from the API
def refresh_live_data():#fetches live market data 
    print("\n>> Fetching live API data to update dictionary...")
    for ticker, details in portfolio_companies.items():
        stock = yf.Ticker(ticker)

        info_dict = stock.info

        live_ebitda = stock.info.get('ebitda')
        live_cash = stock.info.get('totalCash')

        bv_per_share = info_dict.get('bookValue')
        shares = info_dict.get('sharesOutstanding')
        live_book_value = (bv_per_share * shares) if (bv_per_share and shares) else None
        
        if live_ebitda and live_cash:
            # Update the stored EBITDA and recalculate the stored revolver limit
            portfolio_companies[ticker]['ttm_ebitda'] = live_ebitda
            portfolio_companies[ticker]['total_cash'] = live_cash
            portfolio_companies[ticker]['book_value'] = live_book_value

            # calculate based on live data
            net_debt = max(0, details['funded_debt'] - live_cash)
            revolver_capacity = (details['max_leverage'] * live_ebitda) - net_debt
            portfolio_companies[ticker]['revolver_limit'] = max(0, revolver_capacity)
        
    
        #calculate 10% limit
            portfolio_companies[ticker]['revolver_limit'] = live_book_value * 0.10
            
            print(f"Updated {ticker} EBITDA to ${live_ebitda:,}, Cash to ${live_cash:,}, and Book Value to ${live_book_value:,.0f}")
        else:
            print(f"Incomplete live data for {ticker}. Keeping current data.")
   
    # Save using the external file's function
    save_data(portfolio_companies)
    
    print(">> CSV dictionary update complete.\n")        
   

def manage_financials_menu():#menu function 
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