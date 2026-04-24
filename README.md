# Interactive Financial Analysis App

## 1. Problem & User

Financial statement data can be difficult to interpret when it is shown only as raw accounting numbers. This app helps finance students, beginner analysts, and business users quickly analyse a company’s financial performance using key financial ratios.

## 2. Data

**Source:** WRDS / Compustat Fundamentals Annual  
**Access date:** 24.04.2026  
**Tested tickers:** AAPL, TSLA, NVDA  

**Key fields used:**

- Total assets
- Total liabilities
- Current assets
- Current liabilities
- Cash and equivalents
- Inventory
- Accounts receivable
- Short-term debt
- Long-term debt
- Accounts payable
- Shareholders’ equity
- Revenue
- Cost of goods sold
- Operating income
- Net income

A valid WRDS account with Compustat access is required.

## 3. Methods

The app uses Python to:

- Connect to WRDS using the wrds package
- Retrieve annual company financial data from Compustat
- Clean the dataset and remove missing values
- Filter the data by ticker and start year
- Calculate financial KPIs using pandas
- Display the results in an interactive Streamlit app

Main libraries:

- streamlit
- pandas
- wrds

## 4. Key Findings

The app helps users identify and interpret:

- Revenue and net income growth trends over time
- Profitability performance through gross margin, operating margin, net margin, ROA, and ROE
- Liquidity strength using current ratio, quick ratio, and cash ratio
- Leverage position using total debt, debt ratio, and debt-to-equity ratio
- Operating efficiency using asset turnover, inventory turnover, receivables turnover, and payables turnover

## 5. How to Run

Step 1: Install the required packages:

pip install -r your/path/requirements.txt

If needed, use:

pip3 install -r your/path/requirements.txt

Step 2: Run the app:

streamlit run your/path/app.py

If needed, use:

python3 -m streamlit run your/path/app.py

Step 3: Use the app.

Enter:

- WRDS username
- Company ticker, for example AAPL, TSLA, or NVDA
- Start year, for example 2018
- When first using, return to VS Code
- VS Code will require you to enter your username and password into terminal
- Enter your data and confirm your log in with Duo Mobile/phone call

!!! Without login in terminal and confirmation the analysis tool will not load and process data !!!

Then run the analysis and review the KPI table.

## 6. Product Link / Demo

**GitHub repository:** https://github.com/alexejzuyev-maker/financial-statement-analysis-tool/tree/main
**Demo video:** [Insert demo video link here]

The demo video should briefly show:

- The purpose of the app
- The GitHub repository
- How the app is run
- One example analysis using a ticker such as AAPL, TSLA, or NVDA
- A short explanation of the output table

## 7. Limitations & Next Steps

**Limitations:**

- Requires a valid WRDS account with Compustat access
- Analyses one company at a time
- Removes rows with missing values
- Focuses on annual accounting data only
- Does not include stock price or valuation data
- Online deployment may be limited by WRDS authentication

**Next steps:**

- Add KPI charts
- Add multi-company comparison
- Add CSV or Excel download
- Add sample data mode for users without WRDS access
- Improve error handling for invalid tickers or login issues
