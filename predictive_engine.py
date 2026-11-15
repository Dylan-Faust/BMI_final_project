from xml.parsers.expat import model

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from xgboost import XGBRegressor

def fit_sarimax_baseline(historical_capex, exog_data=None):# I was struggling on figuring out how to implement
    """ 
    Processes the time-series data pulled from the API to establish 
    the target company's seasonal CapEx trends and baseline spending trajectory.
    """
    #the architecture of this code is mostly AI designed as this is my first time using Sarimax.
    print("\n>> Fitting SARIMAX baseline model...")

    try:
        #  Convert historical CapEx list into a Pandas Series (endogenous variable)
        capex_series = pd.Series(historical_capex)
        if exog_data is not None:
            aligned_exog = exog_data.tail(len(capex_series)).reset_index(drop=True)
        else:
            aligned_exog = None
            
        # order=(1,1,1) handles Autoregression, Differencing, and Moving Average
        model = SARIMAX(endog=capex_series, 
                        exog=aligned_exog, 
                        order=(1, 1, 1), 
                        enforce_stationarity=False, 
                        enforce_invertibility=False)
        
        results = model.fit(disp=False)
        
        #  Forecast Future CapEx (Next 4 Periods)
        # To forecast, the model needs future macro conditions. For this baseline, 
        # we assume the most recent macro environment holds steady over the next 4 periods.
        future_steps = 4
        
        if aligned_exog is not None:
            last_macro = aligned_exog.iloc[-1:]
            future_exog = pd.concat([last_macro] * future_steps, ignore_index=True)
            baseline_forecast = results.forecast(steps=future_steps, exog=future_exog)
        else:
            baseline_forecast = results.forecast(steps=future_steps)
            
        print(">> Baseline CapEx spending trajectory established.")
        print("\n--- CapEx Forecast (Next 4 Periods) ---")
        for i, val in enumerate(baseline_forecast, 1):
            print(f"  Period +{i}: ${val:,.2f}M")
            
        return baseline_forecast
        
    except Exception as e:
        print(f">> Error fitting SARIMAX model: {e}")
        return None

def predict_covenant_breach(portfolio_companies, macro_training_data):
   """
    Wraps the trained XGBoost regressor inside the Monte Carlo loop to simulate 
    10,000 macroeconomic shock scenarios against the SARIMAX baseline, flagging 
    any iterations that push financials below covenant limits.
    """
   print("\n>> Initializing Monte Carlo Simulation (10,000 iterations)...")
   print(">> Training XGBoost model on macroeconomic data...")

    # 1. Setup Data for XGBoost
    # We use the FRED data as our features (X)
   X_train = macro_training_data[['SOFR_Rate', 'Material_PPI']]
    
    # MOCK TARGET: Creating a synthetic historical "Cash Drain" target (y).
    # In production, this will be replaced by the company's actual historical CapEx deviations.
   y_train = (X_train['SOFR_Rate'] * 50000) + (X_train['Material_PPI'] * 10000)
    
    # 2. Train the XGBoost Model
   xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
   xgb_model.fit(X_train, y_train)

    # Calculate historical market parameters for the Monte Carlo shocks
   sofr_mean = X_train['SOFR_Rate'].mean()
   sofr_std = X_train['SOFR_Rate'].std()
   ppi_mean = X_train['Material_PPI'].mean()
   ppi_std = X_train['Material_PPI'].std()

   for ticker, details in portfolio_companies.items():
        print(f"\n--- Simulating Scenarios for {ticker} ---")
        breach_count = 0
        ebitda = details['ttm_ebitda']
        funded_debt = details['funded_debt']
        total_cash = details['total_cash']
        max_leverage = details['max_leverage']
       
        for i in range(10000):
            # 3. Generate a dynamic macro environment
            # We randomly shock interest rates and inflation based on their real historical volatility
            simulated_sofr = np.random.normal(sofr_mean, sofr_std * 1.5) # 1.5x stress factor
            simulated_ppi = np.random.normal(ppi_mean, ppi_std * 1.5)

            # Format as DataFrame for XGBoost prediction
            shocked_macro_df = pd.DataFrame({
                'SOFR_Rate': [simulated_sofr],
                'Material_PPI': [simulated_ppi]
            })

            # 4. XGBoost predicts the resulting cash drain from this specific macro environment
            predicted_cash_drain = xgb_model.predict(shocked_macro_df)[0]
            
            # Ensure drain isn't negative (macro shocks shouldn't magically generate cash)
            actual_drain = max(0, predicted_cash_drain)

            # Apply the data-driven shock to the company's financials
            shocked_cash = total_cash - actual_drain
            net_debt = max(0, funded_debt - shocked_cash)
            
            # Flag if the new net debt breaches the EBITDA max leverage covenant
            if net_debt > (ebitda * max_leverage):
                breach_count += 1
    
        # Calculate probability
        breach_probability = (breach_count / 10000) * 100
        print(f"  Probability of Covenant Breach: {breach_probability:.2f}%")

   print("\n>> Simulation complete.")
   return None