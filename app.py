# 1.0 Data Download and Initial Inspection
# 1.1 Import the packages required for database connection and data manipulation.
import wrds
import pandas as pd
import streamlit as st
from IPython.display import display

st.set_page_config(page_title="Financial Statement Analysis Tool", layout="wide")

# 1.2 Define the function to download, process financial data, and calculate KPIs.
def condensed_year_end_analysis(username, company, start_year):
   
    # 1.3 Establish a connection to the WRDS database using the provided username.
    db = wrds.Connection(wrds_username=username)
   
    # 1.4 Define the SQL query to retrieve annual financial statement data
    #     from the Compustat Fundamentals Annual database (comp.funda).
    #     The selected variables cover income statement, balance sheet,
    #     and debt-related information required for KPI calculations.
    sql = f"""
    SELECT
        fyear AS FiscalYear,
        tic,
        conm AS CompanyName,
        at AS TotalAssets,
        lt AS TotalLiabilities,
        act AS CurrentAssets,
        lct AS CurrentLiabilities,
        che AS CashAndEquivalents,
        invt AS Inventory,
        rect AS AccountsReceivable,
        dlc AS ShortTermDebt,
        dltt AS LongTermDebt,
        ap AS AccountsPayable,
        seq AS ShareholdersEquity,
        ceq AS CommonEquity,
        sale AS Revenue,
        cogs AS CostOfGoodsSold,
        oiadp AS OperatingIncomeAfterDepreciation,
        ni AS NetIncome
    FROM comp.funda
    WHERE tic = '{company}'
    """

    # 1.5 Execute the SQL query and load the data into a pandas DataFrame.
    data = db.raw_sql(sql)

    # 1.6 Filter the data to include only fiscal years from one year before
    #     the selected start year onward.
    #     The additional year is required to calculate growth rates correctly.
    data = data.loc[data["fiscalyear"] >= int(start_year - 1)].copy()

    # 1.7 Remove rows with missing values to ensure clean KPI calculations.
    data = data.dropna()

    # 2.0 Define and calculate Key Performance Indicators (KPIs)

    # 2.1 Growth KPIs
    #     Measure year-over-year changes in revenue and net income.
    data["Revenue_Growth"] = data["revenue"].pct_change()
    data["Net_Income_Growth"] = data["netincome"].pct_change()

    # 2.2 Profitability KPIs
    #     Measure profitability at different levels of the income statement.
    data["Gross_Profit"] = data["revenue"] - data["costofgoodssold"]
    data["Gross_Margin"] = data["Gross_Profit"] / data["revenue"]
    data["Operating_Margin"] = data["operatingincomeafterdepreciation"] / data["revenue"]
    data["Net_Margin"] = data["netincome"] / data["revenue"]
    data["ROA"] = data["netincome"] / data["totalassets"]
    data["ROE"] = data["netincome"] / data["shareholdersequity"]

    # 2.3 Liquidity KPIs
    #     Measure the company's ability to meet short-term obligations.
    data["Current_Ratio"] = data["currentassets"] / data["currentliabilities"]
    data["Quick_Ratio"] = (data["currentassets"] - data["inventory"]) / data["currentliabilities"]
    data["Cash_Ratio"] = data["cashandequivalents"] / data["currentliabilities"]

    # 2.4 Leverage KPIs
    #     Measure the extent of debt financing relative to assets and equity.
    data["Total_Debt"] = data["shorttermdebt"] + data["longtermdebt"]
    data["Debt_Ratio"] = data["Total_Debt"] / data["totalassets"]
    data["Debt_To_Equity"] = data["Total_Debt"] / data["shareholdersequity"]

    # 2.5 Efficiency KPIs
    #     Measure how efficiently the company uses its assets and working capital.
    data["Asset_Turnover"] = data["revenue"] / data["totalassets"]
    data["Inventory_Turnover"] = data["costofgoodssold"] / data["inventory"]
    data["Receivables_Turnover"] = data["revenue"] / data["accountsreceivable"]
    data["Payables_Turnover"] = data["costofgoodssold"] / data["accountspayable"]

    # 2.6 Prepare selected absolute financial values for reporting purposes.
    data["Net_Income"] = data["netincome"]
    data["Revenue"] = data["revenue"]

    # 3.0 Close the WRDS database connection after data retrieval and processing.
    db.close()

    # 4.0 Create a condensed KPI table containing all relevant variables.
    kpi_df = data[
        [
            "fiscalyear",
            "Revenue_Growth",
            "Net_Income_Growth",
            "Gross_Margin",
            "Operating_Margin",
            "Net_Margin",
            "ROA",
            "ROE",
            "Current_Ratio",
            "Quick_Ratio",
            "Cash_Ratio",
            "Debt_Ratio",
            "Debt_To_Equity",
            "Asset_Turnover",
            "Inventory_Turnover",
            "Receivables_Turnover",
            "Payables_Turnover",
            "Revenue",
            "Gross_Profit",
            "Net_Income",
            "Total_Debt"
        ]
    ].copy()
    
    # 4.1 Define column groups for different formatting styles.
    percent_cols = [c for c in [
        "Revenue_Growth",
        "Net_Income_Growth",
        "Gross_Margin",
        "Operating_Margin",
        "Net_Margin",
        "ROA",
        "ROE"
    ] if c in kpi_df.columns]

    ratio_cols = [c for c in [
        "Current_Ratio",
        "Quick_Ratio",
        "Cash_Ratio",
        "Debt_Ratio",
        "Debt_To_Equity",
        "Asset_Turnover",
        "Inventory_Turnover",
        "Receivables_Turnover",
        "Payables_Turnover"
    ] if c in kpi_df.columns]

    abs_cols = [c for c in [
        "Revenue",
        "Gross_Profit", 
        "Net_Income", 
        "Total_Debt"
    ] if c in kpi_df.columns]

    # 4.2 Create a formatted copy of the KPI table for user-facing output.
    formatted = kpi_df.copy()

    # 4.3 Format percentage-based KPIs.
    for c in percent_cols:
        formatted[c] = formatted[c].apply(
            lambda x: f"{x*100:.1f}%" if pd.notnull(x) else "N/A"
        )

    # 4.4 Format ratio-based KPIs.
    for c in ratio_cols:
        formatted[c] = formatted[c].apply(
            lambda x: f"{x:.1f}" if pd.notnull(x) else "N/A"
        )

    # 4.5 Format absolute values in USD millions.
    for c in abs_cols:
        if c in formatted.columns:
            formatted[c] = formatted[c].apply(
                lambda x: f"${x:,.0f}M" if pd.notnull(x) else "N/A"
            )
        else:
            formatted[c] = data[c].apply(
                lambda x: f"${x:,.0f}M" if pd.notnull(x) else "N/A"
            )

    # 5.0 Transform tables: KPIs as rows, fiscal years as columns.
    report_numeric = kpi_df.set_index("fiscalyear").transpose()
    report_formatted = formatted.set_index("fiscalyear").transpose()

    report_numeric.index = report_numeric.index.astype(str).str.replace("_", " ", regex=False)
    report_formatted.index = report_formatted.index.astype(str).str.replace("_", " ", regex=False)

    if report_numeric.shape[1] > 0:
        report_numeric = report_numeric.iloc[:, 1:]
    if report_formatted.shape[1] > 0:
        report_formatted = report_formatted.iloc[:, 1:]

    return {"numeric": report_numeric, "formatted": report_formatted}


# --------------------------------------------------
# 2. Page title
# --------------------------------------------------
st.title("Financial Statement Analysis Tool")
st.write("Analyze annual financial KPIs from WRDS / Compustat.")


# --------------------------------------------------
# 3. Layout: left input, right report
# --------------------------------------------------
left_col, right_col = st.columns([1, 3])

with left_col:
    st.subheader("Input")

    username = st.text_input("WRDS Username", value="")
    company = st.text_input("Ticker", value="")
    start_year = st.number_input("Start Year", min_value=2000, max_value=2030, value=2018, step=1)

    run = st.button("Run Analysis", use_container_width=True)

with right_col:
    st.subheader("Report")

    if run:
        if not username.strip():
            st.warning("Please enter your WRDS username.")
        elif not company.strip():
            st.warning("Please enter a ticker.")
        else:
            with st.spinner("Loading data and calculating KPIs..."):
                result = condensed_year_end_analysis(
                    username=username,
                    company=company,
                    start_year=start_year
                )

            st.success(f"Analysis completed for {company.upper()}")

            tab1 = st.tabs(["Formatted Report"])[0]

            with tab1:
                st.dataframe(result["formatted"], use_container_width=True)

    else:
        st.info("Enter the inputs on the left and click 'Run Analysis'.")
