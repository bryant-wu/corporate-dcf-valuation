import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class DCFModel:
    def __init__(self, assumptions):
        self.assumptions = assumptions
        self.years = len(assumptions['rev_growth_rates'])
        
    def calculate_wacc(self):
        """Calculates Weighted Average Cost of Capital using CAPM."""
        cost_of_equity = self.assumptions['risk_free_rate'] + self.assumptions['beta'] * (self.assumptions['market_return'] - self.assumptions['risk_free_rate'])
        cost_of_debt_after_tax = self.assumptions['cost_of_debt'] * (1 - self.assumptions['tax_rate'])
        
        wacc = (self.assumptions['weight_equity'] * cost_of_equity) + (self.assumptions['weight_debt'] * cost_of_debt_after_tax)
        return wacc, cost_of_equity

    def project_cash_flows(self):
        """Projects 5-year Unlevered Free Cash Flows (UFCF)."""
        financials = pd.DataFrame(index=['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'])
        
        # Revenue Projections
        revenues = []
        current_rev = self.assumptions['revenue_base']
        for g in self.assumptions['rev_growth_rates']:
            current_rev *= (1 + g)
            revenues.append(current_rev)
            
        financials['Revenue'] = revenues
        financials['EBIT'] = financials['Revenue'] * self.assumptions['ebit_margin']
        financials['Taxes'] = financials['EBIT'] * self.assumptions['tax_rate']
        financials['NOPAT'] = financials['EBIT'] - financials['Taxes']
        
        financials['D&A'] = financials['Revenue'] * self.assumptions['dna_margin']
        financials['CapEx'] = financials['Revenue'] * self.assumptions['capex_margin']
        
        # Change in Net Working Capital
        financials['NWC'] = financials['Revenue'] * self.assumptions['nwc_margin']
        financials['Change in NWC'] = financials['NWC'].diff().fillna(financials['NWC'].iloc[0] - (self.assumptions['revenue_base'] * self.assumptions['nwc_margin']))
        
        # Unlevered Free Cash Flow (UFCF)
        financials['UFCF'] = financials['NOPAT'] + financials['D&A'] - financials['CapEx'] - financials['Change in NWC']
        
        return financials

    def calculate_valuation(self, financials, wacc):
        """Calculates Enterprise Value, Equity Value, and Implied Share Price."""
        # Discount UFCF
        discount_factors = [(1 + wacc) ** i for i in range(1, self.years + 1)]
        financials['PV of UFCF'] = financials['UFCF'] / discount_factors
        
        pv_of_ufcf_sum = financials['PV of UFCF'].sum()
        
        # Terminal Value (Gordon Growth Method)
        final_year_ufcf = financials['UFCF'].iloc[-1]
        terminal_value = (final_year_ufcf * (1 + self.assumptions['terminal_growth_rate'])) / (wacc - self.assumptions['terminal_growth_rate'])
        pv_of_terminal_value = terminal_value / ((1 + wacc) ** self.years)
        
        enterprise_value = pv_of_ufcf_sum + pv_of_terminal_value
        equity_value = enterprise_value + self.assumptions['cash'] - self.assumptions['total_debt']
        implied_share_price = equity_value / self.assumptions['shares_outstanding']
        
        return enterprise_value, equity_value, implied_share_price

    def generate_sensitivity_matrix(self, base_wacc):
        """Generates a sensitivity matrix of Implied Share Price (WACC vs. Terminal Growth)."""
        wacc_range = np.linspace(base_wacc - 0.02, base_wacc + 0.02, 5)
        tg_range = np.linspace(self.assumptions['terminal_growth_rate'] - 0.01, self.assumptions['terminal_growth_rate'] + 0.01, 5)
        
        matrix = pd.DataFrame(index=[f"{w*100:.1f}%" for w in wacc_range], columns=[f"{t*100:.1f}%" for t in tg_range])
        
        for i, w in enumerate(wacc_range):
            for j, t in enumerate(tg_range):
                temp_assumptions = self.assumptions.copy()
                temp_assumptions['terminal_growth_rate'] = t
                
                # Recalculate with temporary variables
                financials = self.project_cash_flows()
                final_year_ufcf = financials['UFCF'].iloc[-1]
                
                pv_of_ufcf_sum = sum([financials['UFCF'].iloc[k] / ((1 + w) ** (k + 1)) for k in range(self.years)])
                tv = (final_year_ufcf * (1 + t)) / (w - t)
                pv_tv = tv / ((1 + w) ** self.years)
                
                ev = pv_of_ufcf_sum + pv_tv
                eq_val = ev + temp_assumptions['cash'] - temp_assumptions['total_debt']
                price = eq_val / temp_assumptions['shares_outstanding']
                
                matrix.iloc[i, j] = round(price, 2)
                
        matrix.index.name = "WACC"
        matrix.columns.name = "Terminal Growth"
        return matrix.astype(float)

if __name__ == "__main__":
    # Baseline Corporate Assumptions (in millions where applicable)
    assumptions = {
        # Operations
        'revenue_base': 1000,
        'rev_growth_rates': [0.10, 0.08, 0.06, 0.05, 0.04], # 5-year projections
        'ebit_margin': 0.18,
        'tax_rate': 0.21,
        'dna_margin': 0.04,
        'capex_margin': 0.05,
        'nwc_margin': 0.10,
        
        # Capital Structure & CAPM
        'risk_free_rate': 0.042,     # e.g., 10-year Treasury
        'market_return': 0.10,       # Expected market return
        'beta': 1.15,                # Industry levered beta
        'cost_of_debt': 0.055,
        'weight_equity': 0.75,
        'weight_debt': 0.25,
        
        # Valuation Elements
        'terminal_growth_rate': 0.025, # 2.5% perpetuity growth
        'shares_outstanding': 100,     # millions
        'cash': 150,
        'total_debt': 300
    }

    model = DCFModel(assumptions)
    
    # 1. wacc
    wacc, cost_of_equity = model.calculate_wacc()
    print(f"--- Cost of Capital ---")
    print(f"Cost of Equity (CAPM): {cost_of_equity*100:.2f}%")
    print(f"WACC: {wacc*100:.2f}%\n")
    
    # 2. project cfs
    financials = model.project_cash_flows()
    print("--- 5-Year UFCF Projections ---")
    print(financials[['Revenue', 'EBIT', 'UFCF']].round(2))
    print("\n")
    
    # 3. valuation
    ev, equity_value, share_price = model.calculate_valuation(financials, wacc)
    print(f"--- Valuation Summary ---")
    print(f"Enterprise Value: ${ev:,.2f}M")
    print(f"Equity Value: ${equity_value:,.2f}M")
    print(f"Implied Share Price: ${share_price:.2f}\n")
    
    # 4. sensitivity
    print("--- Sensitivity Analysis: Implied Share Price ---")
    matrix = model.generate_sensitivity_matrix(wacc)
    print(matrix)

    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt=".2f", cmap="RdYlGn")
    plt.title("Implied Share Price Sensitivity: WACC vs Terminal Growth")
    plt.xlabel("Terminal Growth Rate")
    plt.ylabel("Weighted Average Cost of Capital (WACC)")
    plt.tight_layout()
    plt.savefig("sensitivity_heatmap.png")
    print("\nHeatmap saved as 'sensitivity_heatmap.png'")