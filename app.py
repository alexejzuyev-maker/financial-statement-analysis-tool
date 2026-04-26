# 1.0 Data Download and Initial Inspection
# 1.1 Import the packages required for database connection, data manipulation,
#     and the Streamlit user interface.
import wrds
import pandas as pd
import streamlit as st

# 1.2 Configure the Streamlit page before rendering any interface elements.
#     A wide layout is used so the KPI report has enough horizontal space.
st.set_page_config(page_title="Financial Statement Analysis Tool", layout="wide")


# 1.3 Define the main function used to download, process, and present
#     company-level annual financial statement data.
def condensed_year_end_analysis(username, company, start_year):

    # 1.4 Establish a connection to the WRDS database using the provided username.
    #     The WRDS connection is needed to access Compustat Fundamentals Annual data.
    db = wrds.Connection(wrds_username=username)

    # 1.5 Define the SQL query used to retrieve annual financial statement data
    #     from the Compustat Fundamentals Annual database (comp.funda).
    #     The selected fields cover company identifiers, balance sheet items,
    #     income statement items, and debt-related variables required for KPI calculations.
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

    # 1.6 Execute the SQL query and load the result directly into a pandas DataFrame.
    #     This creates the base dataset for all later filtering and KPI calculations.
    data = db.raw_sql(sql)

    # 1.7 Filter the data to include only fiscal years from one year before the
    #     selected start year onward.
    #     The additional previous year is kept because growth KPIs require a prior-period base.
    data = data.loc[data["fiscalyear"] >= int(start_year - 1)].copy()

    # 1.8 Remove rows with missing values so ratio calculations can be performed
    #     on a clean and complete dataset.
    #     This simplifies the workflow by avoiding partial KPI rows in the final report.
    data = data.dropna()

    # 2.0 Define and calculate Key Performance Indicators (KPIs)

    # 2.1 Growth KPIs
    #     These indicators measure year-over-year changes in revenue and net income.
    #     pct_change() compares each fiscal year with the previous one in the filtered dataset.
    data["Revenue_Growth"] = data["revenue"].pct_change()
    data["Net_Income_Growth"] = data["netincome"].pct_change()

    # 2.2 Profitability KPIs
    #     These indicators measure profitability at different levels of the income statement.
    #     Gross profit is calculated first and then converted into profitability ratios.
    data["Gross_Profit"] = data["revenue"] - data["costofgoodssold"]
    data["Gross_Margin"] = data["Gross_Profit"] / data["revenue"]
    data["Operating_Margin"] = data["operatingincomeafterdepreciation"] / data["revenue"]
    data["Net_Margin"] = data["netincome"] / data["revenue"]
    data["ROA"] = data["netincome"] / data["totalassets"]
    data["ROE"] = data["netincome"] / data["shareholdersequity"]

    # 2.3 Liquidity KPIs
    #     These indicators measure the firm's ability to meet short-term obligations.
    #     The quick ratio excludes inventory, and the cash ratio focuses only on cash resources.
    data["Current_Ratio"] = data["currentassets"] / data["currentliabilities"]
    data["Quick_Ratio"] = (data["currentassets"] - data["inventory"]) / data["currentliabilities"]
    data["Cash_Ratio"] = data["cashandequivalents"] / data["currentliabilities"]

    # 2.4 Leverage KPIs
    #     These indicators measure the degree to which the company relies on debt financing.
    #     Total debt combines short-term and long-term debt before the leverage ratios are calculated.
    data["Total_Debt"] = data["shorttermdebt"] + data["longtermdebt"]
    data["Debt_Ratio"] = data["Total_Debt"] / data["totalassets"]
    data["Debt_To_Equity"] = data["Total_Debt"] / data["shareholdersequity"]

    # 2.5 Efficiency KPIs
    #     These indicators measure how efficiently the company uses assets,
    #     inventory, receivables, and payables in its operations.
    data["Asset_Turnover"] = data["revenue"] / data["totalassets"]
    data["Inventory_Turnover"] = data["costofgoodssold"] / data["inventory"]
    data["Receivables_Turnover"] = data["revenue"] / data["accountsreceivable"]
    data["Payables_Turnover"] = data["costofgoodssold"] / data["accountspayable"]

    # 2.6 Prepare selected absolute financial values for reporting purposes.
    #     These values are included alongside ratios so users can view headline financial amounts.
    data["Net_Income"] = data["netincome"]
    data["Revenue"] = data["revenue"]

    # 3.0 Close the WRDS database connection after data retrieval and processing.
    #     This is good practice because the report no longer requires an active connection.
    db.close()

    # 4.0 Create a condensed KPI table containing only the final variables
    #     required for the numeric and formatted reports.
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

    # 4.1 Define column groups that require different output formats.
    #     Percentage columns, ratio columns, and absolute-value columns
    #     are formatted separately for clearer presentation in Streamlit.
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
    #     The numeric table is kept unchanged, while the formatted table is converted into strings.
    formatted = kpi_df.copy()

    # 4.3 Format percentage-based KPIs so they display with one decimal place
    #     and a percentage sign.
    for c in percent_cols:
        formatted[c] = formatted[c].apply(
            lambda x: f"{x*100:.1f}%" if pd.notnull(x) else "N/A"
        )

    # 4.4 Format ratio-based KPIs so they display as compact one-decimal numbers.
    for c in ratio_cols:
        formatted[c] = formatted[c].apply(
            lambda x: f"{x:.1f}" if pd.notnull(x) else "N/A"
        )

    # 4.5 Format absolute values in USD millions for clearer financial reporting.
    #     The labels are intended to make large values easier to read in the final app output.
    for c in abs_cols:
        if c in formatted.columns:
            formatted[c] = formatted[c].apply(
                lambda x: f"${x:,.0f}M" if pd.notnull(x) else "N/A"
            )
        else:
            formatted[c] = data[c].apply(
                lambda x: f"${x:,.0f}M" if pd.notnull(x) else "N/A"
            )

    # 5.0 Transform the KPI tables so KPIs appear as rows and fiscal years as columns.
    #     This report layout is easier to review in Streamlit than the original row-based structure.
    report_numeric = kpi_df.set_index("fiscalyear").transpose()
    report_formatted = formatted.set_index("fiscalyear").transpose()

    # 5.1 Clean the row labels by replacing underscores with spaces.
    #     This improves readability for the displayed KPI names.
    report_numeric.index = report_numeric.index.astype(str).str.replace("_", " ", regex=False)
    report_formatted.index = report_formatted.index.astype(str).str.replace("_", " ", regex=False)

    # 5.2 Remove the first fiscal year column from the final report if at least one
    #     comparison year exists.
    #     The first year is excluded because growth calculations for that year are based
    #     on the preserved pre-start-year observation and may not be intended for final display.
    if report_numeric.shape[1] > 0:
        report_numeric = report_numeric.iloc[:, 1:]
    if report_formatted.shape[1] > 0:
        report_formatted = report_formatted.iloc[:, 1:]

    # 5.3 Return both the numeric report and the formatted report.
    #     The numeric version is useful for further analysis, while the formatted version
    #     is intended for direct presentation in the Streamlit interface.
    return {"numeric": report_numeric, "formatted": report_formatted}


# 6. Page title
# 6.1 Display the main title and a short description of the app's purpose.
st.title("Financial Statement Analysis Tool")
st.write("Analyze annual financial KPIs from WRDS / Compustat.")

# 7. Layout: left input, right report
# 7.1 Create a two-column layout so user inputs and report output are separated clearly.
left_col, right_col = st.columns([1, 3])

with left_col:
    # 7.2 Build the input panel used to collect the database username,
    #     the ticker symbol, and the start year for the analysis.
    st.subheader("Input")

    username = st.text_input("WRDS Username", value="")
    company = st.text_input("Ticker", value="")
    start_year = st.number_input("Start Year", min_value=2000, max_value=2030, value=2018, step=1)

    # 7.3 Create the button that triggers the data download and KPI generation process.
    run = st.button("Run Analysis", use_container_width=True)

with right_col:
    # 7.4 Build the output panel used to display the generated report or user guidance.
    st.subheader("Report")

    if run:
        # 7.5 Validate the required user inputs before attempting the WRDS connection.
        if not username.strip():
            st.warning("Please enter your WRDS username.")
        elif not company.strip():
            st.warning("Please enter a ticker.")
        else:
            # 7.6 Run the full analysis while showing a loading spinner to indicate progress.
            with st.spinner("Loading data and calculating KPIs..."):
                result = condensed_year_end_analysis(
                    username=username,
                    company=company,
                    start_year=start_year
                )

            # 7.7 Confirm successful completion and display the formatted KPI report.
            st.success(f"Analysis completed for {company.upper()}")

            tab1 = st.tabs(["Formatted Report"])[0]

            with tab1:
                st.dataframe(result["formatted"], use_container_width=True)

    else:
        # 7.8 Display an instructional message before the user runs the app.
        st.info("Enter the inputs on the left and click 'Run Analysis'.")
