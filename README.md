# Corporate DCF Valuation Model

## Overview
Greetings and salutations! This repository shows a Discounted Cash Flow (DCF) model that I built in Python. I designed it to be adaptable across public equities in major sectors. This model projects Unlevered Free Cash Flows (UFCF), calculates the Weighted Average Cost of Capital (WACC) via CAPM, and performs sensitivity analyses to determine Enterprise Value and also implied share prices.

## Operations
Cost of Capital (WACC Calculation): Uses the CAPM model to determine the discount rate, taking into account market risk premiums, the risk-free rate (based on 10-year U.S. Treasury bonds), the cost of debt, and comparable companies' betas.

Cash Flow Projections: Models 5-year unlevered free cash flows by estimating revenue growth, operating margins (EBIT), taxes, Depreciation and Amortization (D&A), Capital Expenditures (CapEx), and Net Working Capital (NWC) changes.

Terminal Value (TV) Calculation: Calculates Terminal Value using the Perpetuity Growth method (Gordon Growth model) and discounts it back to present value.

Sensitivity Analysis Matrices: Generates automated Pandas DataFrames for sensitivity testing of implied stock prices across macroeconomic environments, evaluating WACC margins versus terminal growth rates with Seaborn heatmap visualizations.

## Technology Stack & Dependencies
Language: Python 3.8+

Data Processing & Analytics: Pandas, NumPy

Data Visualization: Matplotlib, Seaborn

## How to set up!

Follow these steps to clone, configure, and execute the model in a local environment.

### 1. Clone and Navigate the Repository
Open your terminal and run:

```bash
git clone https://github.com/bryant-wu/corporate-dcf-valuation.git
cd corporate-dcf-valuation
```

### 2. Install Dependencies
Ensure Python 3.8+ is installed, then install the required financial modeling and visualization packages:

```bash
pip install -r requirements.txt
```

### 3. Modify Assumptions (Optional)
Open dcf_model.py and adjust the baseline dictionary parameters (assumptions) to reflect target company metrics (e.g., revenue base, growth rates, EBIT margins, tax rates, debt-to-equity weighting, and beta).

### 4. Run the Valuation Script
Execute the core script to output the WACC breakdown, 5-year cash flow projections, valuation summary, and sensitivity matrix directly to your console:

```Bash
python dcf_model.py
```

### 5. Review Output
Console Summary: Inspect the printed cost of equity, WACC, Enterprise Value, Equity Value, and Implied Share Price.

Visualization: Locate the generated sensitivity_heatmap.png in the root directory for a visual distribution of the WACC vs. Terminal Growth sensitivity matrix.