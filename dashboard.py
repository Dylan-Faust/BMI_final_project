import matplotlib.pyplot as plt

def show_risk_dashboard(portfolio_companies):
    print("\n" + "="*50)
    print("   RISK ASSESSMENT & COVENANT HEADROOM DASHBOARD")
    print("="*50)

    if not portfolio_companies:
        print("\n>> Portfolio is empty. Please add companies via Option 1.")
        return
    tickers = []
    net_debts = []
    covenant_limits = []
    bar_colors = []


    for ticker, details in portfolio_companies.items():
        ebitda = details['ttm_ebitda']
        funded_debt = details['funded_debt']
        total_cash = details['total_cash']
        max_leverage = details['max_leverage']

        # Calculate exact covenant limits and current standing
        net_debt = max(0, funded_debt - total_cash)
        covenant_limit = ebitda * max_leverage
        headroom = covenant_limit - net_debt

        # Calculate percentage of the limit still available
        headroom_pct = (headroom / covenant_limit) * 100 if covenant_limit > 0 else 0

        # Save data for the chart
        tickers.append(ticker)
        net_debts.append(net_debt)
        covenant_limits.append(covenant_limit)

        print(f"\n--- {ticker} Risk Profile ---")
        print(f"  Covenant Debt Limit:  ${covenant_limit:,.0f}")
        print(f"  Current Net Debt:     ${net_debt:,.0f}")
        if headroom > 0:
            print(f"  Available Headroom:   ${headroom:,.0f} ({headroom_pct:.1f}% buffer)")
            
            # Dynamic Risk Scoring & Chart Colors
            if headroom_pct < 15:
                print("  STATUS: 🔴 HIGH RISK (Approaching covenant limit)")
                bar_colors.append('darkorange')
            elif headroom_pct < 35:
                print("  STATUS: 🟡 MODERATE RISK")
                bar_colors.append('gold')
            else:
                print("  STATUS: 🟢 LOW RISK (Healthy liquidity buffer)")
                bar_colors.append('forestgreen')
        else:
            print(f"  Available Headroom:   $0 (Breached by ${abs(headroom):,.0f})")
            print("  STATUS: 💀 CRITICAL (Currently in Default)")
            bar_colors.append('firebrick')
    print("\n" + "="*50)
    
    # --- MATPLOTLIB VISUALIZATION ---
    print("\n>> Generating visual dashboard...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the maximum covenant limit as a light gray background bar
    ax.barh(tickers, covenant_limits, color='whitesmoke', edgecolor='silver', 
            height=0.6, label='Max Debt Limit')
    
    # Plot the actual Net Debt on top with dynamic risk colors
    ax.barh(tickers, net_debts, color=bar_colors, height=0.6, label='Current Net Debt')
    
    # Formatting the chart
    ax.set_xlabel('Debt Amount ($)', fontsize=12)
    ax.set_title('Live Covenant Headroom Visualization', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    
    # Format the x-axis to show readable numbers (e.g., billions/millions) instead of scientific notation
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    plt.tight_layout()
    plt.show()