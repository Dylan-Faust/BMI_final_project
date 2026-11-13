from m1_menu_funcs import manage_financials_menu
from data_manager import fetch_macro_data
from predictive_engine import fit_sarimax_baseline, predict_covenant_breach


# Function to print all menu options for the risk assessment tool
def show_menu():
    print("\n" + "="*45)
    print("  INSTITUTIONAL RISK & CAPEX FORECASTING")
    print("="*45)
    print("1. Input Company Financials, Covenants, & CapEx Plan")
    print("2. Run Liquidity & Covenant Stress Test")
    print("3. View Risk Assessment & Headroom Dashboards")
    print("4. Export Underwriting Risk Report")
    print("5. Save Session and Exit")
    print("="*45)

# Main function to run the menu loop until the user chooses to exit
def main():
    while True:
        show_menu()
        choice = input("Select a menu option (1-5): ").strip()
        
        if choice == '1':
            manage_financials_menu()
        elif choice == '2':
            print("\n--- Running Liquidity & Covenant Stress Test ---")
            macro_data = fetch_macro_data()
            
            if macro_data is not None:
                # Mock CapEx data until we build the company-specific pull
                mock_historical_capex = [12.5, 14.1, 13.8, 16.2, 18.0, 17.5] 
                
                # Trigger the predictive engine
                fit_sarimax_baseline(mock_historical_capex, exog_data=macro_data)
                
                # We will wire up the predict_covenant_breach(portfolio, macro_data) function here next
            else:
                print(">> Simulation aborted: Could not retrieve macroeconomic baseline data.")
        elif choice == '3':
            print("Coming soon")
        elif choice == '4':
            print("Coming soon")
        elif choice == '5':
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid option. Please choose a number from 1 to 5.")

if __name__ == "__main__":
    main()