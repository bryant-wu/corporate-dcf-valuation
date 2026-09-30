import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class ValuationEngine:
    def __init__(self, params):
        self.p = params
        self.horizon = len(params['growth_schedule'])
        
    def get_wacc(self):
        # Determine cost of capital via CAPM framework and after-tax cost of debt
        ke = self.p['rf'] + self.p['beta'] * (self.p['mrp'])
        kd_after = self.p['cost_of_debt'] * (1 - self.p['tax_rate'])
        
        wacc = (self.p['we'] * ke) + (self.p['wd'] * kd_after)
        return wacc, ke

    def build_schedule(self):
        # Project 5-year operating metrics and unlevered free cash flows
        df = pd.DataFrame(index=[f"Year {i}" for i in range(1, self.horizon + 1)])
        
        rev_list = []
        rev_tracking = self.p['base_revenue']
        for g in self.p['growth_schedule']:
            rev_tracking *= (1 + g)
            rev_list.append(rev_tracking)
            
        df['Revenue'] = rev_list
        df['EBIT'] = df['Revenue'] * self.p['operating_margin']
        df['Tax'] = df['EBIT'] * self.p['tax_rate']
        df['NOPAT'] = df['EBIT'] - df['Tax']
        
        df['DA'] = df['Revenue'] * self.p['da_pct']
        df['CapEx'] = df['Revenue'] * self.p['capex_pct']
        
        # Working capital adjustments
        df['NWC'] = df['Revenue'] * self.p['nwc_pct']
        df['Delta_NWC'] = df['NWC'].diff().fillna(df['NWC'].iloc[0] - (self.p['base_revenue'] * self.p['nwc_pct']))
        
        # Free cash flow generation
        df['UFCF'] = df['NOPAT'] + df['DA'] - df['CapEx'] - df['Delta_NWC']
        return df

    def compute_valuation(self, df, hurdle_rate):
        # Discount future flows and calculate Enterprise to Equity bridge
        discount_vec = [(1 + hurdle_rate) ** i for i in range(1, self.horizon + 1)]
        df['PV_UFCF'] = df['UFCF'] / discount_vec
        
        sum_pv_ufcf = df['PV_UFCF'].sum()
        
        # Terminal value via Gordon Growth
        terminal_flow = df['UFCF'].iloc[-1]
        terminal_val = (terminal_flow * (1 + self.p['perp_growth'])) / (hurdle_rate - self.p['perp_growth'])
        pv_terminal = terminal_val / ((1 + hurdle_rate) ** self.horizon)
        
        enterprise_val = sum_pv_ufcf + pv_terminal
        equity_val = enterprise_val + self.p['cash_equivalents'] - self.p['total_debt']
        share_price = equity_val / self.p['shares_out']
        
        return enterprise_val, equity_val, share_price

    def sensitivity_grid(self, baseline_wacc):
        # Stress test share price against varying WACC and terminal growth rates
        wacc_spread = np.linspace(baseline_wacc - 0.02, baseline_wacc + 0.02, 5)
        tg_spread = np.linspace(self.p['perp_growth'] - 0.01, self.p['perp_growth'] + 0.01, 5)
        
        grid = pd.DataFrame(index=[f"{w*100:.1f}%" for w in wacc_spread], columns=[f"{t*100:.1f}%" for t in tg_spread])
        
        for idx, w in enumerate(wacc_spread):
            for col, t in enumerate(tg_spread):
                df_temp = self.build_schedule()
                last_ufcf = df_temp['UFCF'].iloc[-1]
                
                pv_sum = sum([df_temp['UFCF'].iloc[k] / ((1 + w) ** (k + 1)) for k in range(self.horizon)])
                tv = (last_ufcf * (1 + t)) / (w - t)
                pv_tv = tv / ((1 + w) ** self.horizon)
                
                ev = pv_sum + pv_tv
                eq = ev + self.p['cash_equivalents'] - self.p['total_debt']
                px = eq / self.p['shares_out']
                
                grid.iloc[idx, col] = round(px, 2)
                
        grid.index.name = "WACC"
        grid.columns.name = "Terminal Growth"
        return grid.astype(float)

if __name__ == "__main__":
    assumptions = {
        'base_revenue': 1200,
        'growth_schedule': [0.12, 0.09, 0.07, 0.05, 0.04],
        'operating_margin': 0.20,
        'tax_rate': 0.21,
        'da_pct': 0.035,
        'capex_pct': 0.045,
        'nwc_pct': 0.08,
        'rf': 0.042,
        'mrp': 0.055,
        'beta': 1.10,
        'cost_of_debt': 0.06,
        'we': 0.80,
        'wd': 0.20,
        'perp_growth': 0.025,
        'shares_out': 120,
        'cash_equivalents': 180,
        'total_debt': 350
    }

    engine = ValuationEngine(assumptions)
    
    wacc, cost_equity = engine.get_wacc()
    print("=== COST OF CAPITAL ===")
    print(f"Cost of Equity: {cost_equity*100:.2f}%")
    print(f"WACC: {wacc*100:.2f}%\n")
    
    financial_schedule = engine.build_schedule()
    print("=== PROJECTIONS ===")
    print(financial_schedule[['Revenue', 'EBIT', 'UFCF']].round(2))
    print("\n")
    
    ev, eq_val, target_price = engine.compute_valuation(financial_schedule, wacc)
    print("=== VALUATION OUTPUT ===")
    print(f"Enterprise Value: ${ev:,.2f}M")
    print(f"Equity Value: ${eq_val:,.2f}M")
    print(f"Implied Price per Share: ${target_price:.2f}\n")
    
    sens_matrix = engine.sensitivity_grid(wacc)
    print("=== SENSITIVITY TABLE ===")
    print(sens_matrix)

    plt.figure(figsize=(8, 6))
    sns.heatmap(sens_matrix, annot=True, fmt=".2f", cmap="Blues")
    plt.title("Valuation Sensitivity: WACC vs Terminal Growth Rate")
    plt.xlabel("Terminal Growth Rate")
    plt.ylabel("WACC")
    plt.tight_layout()
    plt.savefig("sensitivity_heatmap.png")
    print("\nSaved output plot as sensitivity_heatmap.png")