import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import re

st.set_page_config(page_title="Contract Data Analysis", layout="wide")

st.title("Contract Data Analysis Dashboard")

# Move file uploader to sidebar
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Contract Data CSV", type=["csv"])

# Currency conversion function with hardcoded exchange rates
def convert_currency(value, from_currency, to_currency):
    # Define exchange rates (hardcoded)
    exchange_rates = {
        'USD': 1.0,  # Base currency
        'EUR': 0.92,  # 1 USD = 0.92 EUR
        'GBP': 0.77,  # 1 USD = 0.77 GBP
        'CHF': 0.87,  # 1 USD = 0.87 CHF
        'DKK': 6.75,  # 1 USD = 6.75 DKK
        'NOK': 10.18, # 1 USD = 10.18 NOK
        'SEK': 10.06, # 1 USD = 10.06 SEK
    }
    
    # First convert to USD if not already
    if from_currency != 'USD':
        usd_value = value / exchange_rates[from_currency]
    else:
        usd_value = value
    
    # Then convert USD to target currency
    if to_currency != 'USD':
        return usd_value * exchange_rates[to_currency]
    else:
        return usd_value

# Function to clean currency string and extract numeric value
def extract_numeric_value(value):
    if pd.isna(value):
        return np.nan
    
    if isinstance(value, (int, float)):
        return value
    
    # Extract currency code and numeric value
    try:
        # Extract currency code
        currency_match = re.search(r'([A-Z]{3})', str(value))
        currency = currency_match.group(1) if currency_match else 'USD'
        
        # Extract numeric value, removing commas and other non-numeric characters
        numeric_str = re.sub(r'[^0-9.]', '', str(value))
        numeric_value = float(numeric_str) if numeric_str else np.nan
        
        return numeric_value, currency
    except:
        return np.nan, 'USD'

if uploaded_file is not None:
    # Load data
    @st.cache_data
    def load_data(file):
        df = pd.read_csv(file)
        # Convert date columns to datetime
        date_columns = ['CustomerSignedDate', 'Canceled_Date__c', 'EMEA_Notification_Date__c', 
                       'StartDate', 'Contract_End_Date__c', 'Contract_Original_End_Date__c',
                       'Price_Increase_Opportunity_Date__c', 'LastEvaluationDate__c', 
                       'ActivatedDate']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Process AnnualSalesValue__c to extract numeric values and currency
        if 'AnnualSalesValue__c' in df.columns:
            # Create new columns for numeric value and currency
            df['AnnualSalesValue_Numeric'] = np.nan
            df['AnnualSalesValue_Currency'] = 'USD'
            
            # Process each row
            for idx, value in df['AnnualSalesValue__c'].items():
                try:
                    result = extract_numeric_value(value)
                    if isinstance(result, tuple):
                        df.at[idx, 'AnnualSalesValue_Numeric'] = result[0]
                        df.at[idx, 'AnnualSalesValue_Currency'] = result[1]
                    else:
                        df.at[idx, 'AnnualSalesValue_Numeric'] = result
                except:
                    pass
        
        return df
    
    df = load_data(uploaded_file)
    
    # Sidebar for currency selection
    st.sidebar.header("Settings")
    target_currency = st.sidebar.selectbox(
        "Select Display Currency",
        options=['USD', 'EUR', 'GBP', 'CHF', 'DKK', 'NOK', 'SEK'],
        index=0  # Default to USD
    )
    
    # Convert all sales values to selected currency
    df['AnnualSalesValue_Converted'] = df.apply(
        lambda x: convert_currency(
            x['AnnualSalesValue_Numeric'],
            x['AnnualSalesValue_Currency'],
            target_currency
        ) if pd.notna(x['AnnualSalesValue_Numeric']) else np.nan,
        axis=1
    )
    
    # Sidebar for filters
    st.sidebar.header("Filters")
    
    # Create filters for the specified columns
    contract_types = st.sidebar.multiselect(
        "Select Contract Types",
        options=df['EMEA_Type_of_contract__c'].dropna().unique(),
        default=[]
    )
    
    bus_included = st.sidebar.multiselect(
        "Select BUs included in Contract",
        options=df['BUs_included_in_Contract__c'].dropna().unique(),
        default=[]
    )
    
    regions = st.sidebar.multiselect(
        "Select Contract Clusters",
        options=df['ContractRegion__c'].dropna().unique(),
        default=[]
    )
    
    countries = st.sidebar.multiselect(
        "Select Contract Countries",
        options=df['ContractCountry__c'].dropna().unique(),
        default=[]
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if contract_types:
        filtered_df = filtered_df[filtered_df['EMEA_Type_of_contract__c'].isin(contract_types)]
    
    if bus_included:
        filtered_df = filtered_df[filtered_df['BUs_included_in_Contract__c'].isin(bus_included)]
    
    if regions:
        filtered_df = filtered_df[filtered_df['ContractRegion__c'].isin(regions)]
    
    if countries:
        filtered_df = filtered_df[filtered_df['ContractCountry__c'].isin(countries)]
    
    # Data Quality Analysis
    st.header("Data Quality Analysis")
    
    # KPI relevant columns
    kpi_columns = ['Status', 'StartDate', 'Contract_End_Date__c', 'AnnualSalesValue__c', 
                  'ActivatedDate', 'Price_Increase_Opportunity_Date__c', 'EMEA_Notification_Date__c',
                  'ConsignmentValue__c','CapitalValue__c', 'TotalProcedureCommitments__c'
                  ]
    
    # Calculate missing values percentage
    missing_values = pd.DataFrame({
        'Column': filtered_df.columns,
        'Missing Values': filtered_df.isna().sum(),
        'Missing Percentage': (filtered_df.isna().sum() / len(filtered_df) * 100).round(2)
    }).sort_values('Missing Percentage', ascending=False)
    
    # Highlight KPI relevant columns
    missing_values['KPI Relevant'] = missing_values['Column'].isin(kpi_columns)
    
    # Show missing values for KPI relevant columns
    kpi_missing = missing_values[missing_values['KPI Relevant']]
    

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Missing Values in KPI Relevant Columns")
        st.dataframe(kpi_missing)
    
    with col2:
        # Create a bar chart for missing values in KPI relevant columns
        fig = px.bar(
            kpi_missing,
            x='Column',
            y='Missing Percentage',
            title='Missing Data Percentage in KPI Relevant Columns',
            color='Missing Percentage',
            color_continuous_scale='YlOrRd'
        )
        st.plotly_chart(fig)

    # Calculate missing values by BU
    st.subheader("Missing Data by Clusters - no filters applied")

    # Create a function to calculate missing percentage for each KPI column by BU
    def calculate_missing_by_reg(dataframe, column_list):
        # Get all regions
        regions = dataframe['ContractRegion__c'].dropna().unique()
        
        # Create empty dictionary to store results
        result_data = []
        
        # Loop through each BU and calculate missing values for each KPI column
        for r in regions:
            reg_df = dataframe[dataframe['ContractRegion__c'] == r]
            region_total = len(reg_df)
            
            if region_total > 0:  # Avoid division by zero
                for col in column_list:
                    if col in reg_df.columns:
                        missing_count = reg_df[col].isna().sum()
                        missing_pct = (missing_count / region_total * 100).round(2)
                        
                        result_data.append({
                            'Region': r,
                            'Column': col,
                            'Missing Percentage': missing_pct,
                            'Total Contracts': region_total
                        })
        
        return pd.DataFrame(result_data)

    # Calculate missing values by BU for KPI columns
    missing_by_bu = calculate_missing_by_reg(df, kpi_columns)

    # Create a heatmap of missing values by BU
    if not missing_by_bu.empty:
        fig = px.bar(
            missing_by_bu,
            x='Column',
            y='Missing Percentage',
            color='Missing Percentage',
            facet_col='Region',
            facet_col_wrap=4,  # Adjust based on number of BUs
            title='Missing Data Percentage in KPI Relevant Columns by Cluster',
            color_continuous_scale='YlOrRd',
            labels={'Missing Percentage': '% Missing'},
            height=800  # Adjust based on number of BUs
        )
        st.plotly_chart(fig)
        
        # Alternative view: heatmap
        fig2 = px.imshow(
            missing_by_bu.pivot(index='Region', columns='Column', values='Missing Percentage'),
            labels=dict(x="Column", y="Region", color="Missing Percentage"),
            color_continuous_scale='YlOrRd',
            title='Missing Data Heatmap by Cluster'
        )
        st.plotly_chart(fig2)
        
        # Show table of missing values by BU
        with st.expander("View Detailed Missing Data by Cluster"):
            st.dataframe(missing_by_bu.sort_values(['Region', 'Missing Percentage'], ascending=[True, False]))
    else:
        st.warning("No region information available to analyze missing data by BU.")


    # Show overall data statistics
    with st.expander("Show Full Data Quality Statistics"):
        st.dataframe(missing_values)
    
    # Define active contracts 
    active_contracts = filtered_df[filtered_df['Status'] == 'Active']
    
    # KPI 1: How many active contracts
    st.header("KPI Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Contracts", len(filtered_df))
    
    with col2:
        st.metric("Active Contracts", len(active_contracts))
    
    with col3:
        active_percentage = round((len(active_contracts) / len(filtered_df)) * 100, 2) if len(filtered_df) > 0 else 0
        st.metric("Active Contract Percentage", f"{active_percentage}%")
    
    # KPI 2: Top 20 contracts per annual sales value
    st.subheader(f"Top 20 Contracts per Annual Sales Value ({target_currency})")
    
    # Sort by annual sales value and get top 20
    top_contracts = filtered_df.dropna(subset=['AnnualSalesValue_Converted']).sort_values('AnnualSalesValue_Converted', ascending=False).head(20)
    
    # Create a horizontal bar chart for top contracts
    fig = px.bar(
        top_contracts,
        x='Contract_Description__c', 
        y='AnnualSalesValue_Converted',
        title=f'Top 20 Contracts by Annual Sales Value ({target_currency})',
        labels={'Contract_Description__c': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
        hover_data=['ContractNumber', 'ContractCountry__c', 'EMEA_Type_of_contract__c']
    )
    st.plotly_chart(fig)
    
    # KPI 3: Contracts activated per month
    st.subheader("Contracts Activated per Month")
    
    # Filter contracts with activation date
    contracts_with_activation = filtered_df.dropna(subset=['ActivatedDate'])
    
    # Extract year and month from activation date
    contracts_with_activation['ActivationMonth'] = contracts_with_activation['ActivatedDate'].dt.to_period('M')
    
    # Count contracts activated per month
    activations_per_month = contracts_with_activation.groupby('ActivationMonth').size().reset_index(name='Count')
    activations_per_month['ActivationMonth'] = activations_per_month['ActivationMonth'].astype(str)
    
    # Create a line chart for activations per month
    fig = px.line(
        activations_per_month,
        x='ActivationMonth',
        y='Count',
        title='Contracts Activated per Month',
        markers=True
    )
    st.plotly_chart(fig)
    
    # Top 20 activated contracts per annual sales value
    st.subheader(f"Top 20 Activated Contracts per Annual Sales Value ({target_currency})")
    
    top_activated = active_contracts.sort_values('AnnualSalesValue_Converted', ascending=False).head(20)#contracts_with_activation.dropna(subset=['AnnualSalesValue_Converted']).sort_values('AnnualSalesValue_Converted', ascending=False).head(20)
    
    fig = px.bar(
        top_activated,
        x='Contract_Description__c', 
        y='AnnualSalesValue_Converted',
        title=f'Top 20 Activated Contracts by Annual Sales Value ({target_currency})',
        labels={'Contract_Description__c': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
        hover_data=['ContractNumber', 'ContractCountry__c', 'EMEA_Type_of_contract__c', 'ActivatedDate']
    )
    st.plotly_chart(fig)
    
    # KPI 4: Contracts sent out but not activated
    st.subheader("Contracts Sent Out but Not Activated")
    
    # Find contracts with notification date but no activation date or with status not activated
    sent_not_activated = filtered_df[
        (filtered_df['EMEA_Notification_Date__c'].notna()) & 
        ( (filtered_df['Status'] != 'Active'))
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Contracts Sent Not Activated", len(sent_not_activated))
    
    with col2:
        sent_percentage = round((len(sent_not_activated) / len(filtered_df)) * 100, 2) if len(filtered_df) > 0 else 0
        st.metric("Percentage of Total", f"{sent_percentage}%")
    
    # Top 20 sent but not activated contracts per annual sales value
    top_sent_not_activated = sent_not_activated.dropna(subset=['AnnualSalesValue_Converted']).sort_values('AnnualSalesValue_Converted', ascending=False).head(20)
    
    fig = px.bar(
        top_sent_not_activated,
        x='Contract_Description__c',  
        y='AnnualSalesValue_Converted',
        title=f'Top 20 Contracts Sent but Not Activated by Annual Sales Value ({target_currency})',
        labels={'Contract_Description__c': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
        hover_data=['ContractNumber', 'ContractCountry__c', 'EMEA_Type_of_contract__c', 'EMEA_Notification_Date__c']
    )
    st.plotly_chart(fig)
    
    # KPI 5: Expiring contracts
    st.subheader("Expiring Contracts Analysis")
    
    # Get current date
    today = datetime.now().date()
    
    # Calculate expiration dates
    expiring_this_year = filtered_df[
        (filtered_df['Contract_End_Date__c'].dt.year == today.year) & 
        (filtered_df['Contract_End_Date__c'].dt.date >= today)
    ]
    
    three_months = today + timedelta(days=90)
    expiring_next_3months = filtered_df[
        (filtered_df['Contract_End_Date__c'].dt.date >= today) & 
        (filtered_df['Contract_End_Date__c'].dt.date <= three_months)
    ]
    
    six_months = today + timedelta(days=180)
    expiring_next_6months = filtered_df[
        (filtered_df['Contract_End_Date__c'].dt.date >= today) & 
        (filtered_df['Contract_End_Date__c'].dt.date <= six_months)
    ]
    
    # Define "not followed up" as those without notification date
    not_followed_year = expiring_this_year[expiring_this_year['EMEA_Notification_Date__c'].isna()]
    not_followed_3m = expiring_next_3months[expiring_next_3months['EMEA_Notification_Date__c'].isna()]
    not_followed_6m = expiring_next_6months[expiring_next_6months['EMEA_Notification_Date__c'].isna()]
    
    # Create a dataframe for visualization
    expiry_data = pd.DataFrame({
        'Time Frame': ['This Year', 'Next 3 Months', 'Next 6 Months'],
        'Total Expiring': [len(expiring_this_year), len(expiring_next_3months), len(expiring_next_6months)],
        'Not Followed Up': [len(not_followed_year), len(not_followed_3m), len(not_followed_6m)]
    })
    
    # Create a bar chart for expiring contracts
    fig = px.bar(
        expiry_data,
        x='Time Frame',
        y=['Total Expiring', 'Not Followed Up'],
        title='Expiring Contracts Analysis',
        barmode='group'
    )
    st.plotly_chart(fig)
    
    # Calculate total value of expiring contracts
    total_value_year = expiring_this_year['AnnualSalesValue_Converted'].sum()
    total_value_3m = expiring_next_3months['AnnualSalesValue_Converted'].sum()
    total_value_6m = expiring_next_6months['AnnualSalesValue_Converted'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(f"Total Value Expiring This Year ({target_currency})", f"{total_value_year:,.2f}")
    
    with col2:
        st.metric(f"Total Value Expiring Next 3 Months ({target_currency})", f"{total_value_3m:,.2f}")
    
    with col3:
        st.metric(f"Total Value Expiring Next 6 Months ({target_currency})", f"{total_value_6m:,.2f}")
    
    # Top contracts expiring
    # with st.expander(f"Top Contracts Expiring This Year ({target_currency})"):
    top_expiring_year = expiring_this_year.dropna(subset=['AnnualSalesValue_Converted']).sort_values('AnnualSalesValue_Converted', ascending=False).head(20)
    
    fig = px.bar(
        top_expiring_year,
        x='Contract_Description__c', 
        y='AnnualSalesValue_Converted',
        title=f'Top 20 Contracts Expiring This Year by Annual Sales Value ({target_currency})',
        labels={'Contract_Description__c': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
        hover_data=['ContractNumber', 'ContractCountry__c', 'Contract_End_Date__c']
    )
    st.plotly_chart(fig)
    
    # KPI 6: Price Increase Opportunity
    st.subheader("Price Increase Opportunities")

    try:
        # Price increase opportunities in different time frames
        price_increase_year = filtered_df[
            (filtered_df['Price_Increase_Opportunity_Date__c'].dt.year == today.year) & 
            (filtered_df['Price_Increase_Opportunity_Date__c'].dt.date >= today)
        ]
        
        price_increase_3m = filtered_df[
            (filtered_df['Price_Increase_Opportunity_Date__c'].dt.date >= today) & 
            (filtered_df['Price_Increase_Opportunity_Date__c'].dt.date <= three_months)
        ]
        
        price_increase_6m = filtered_df[
            (filtered_df['Price_Increase_Opportunity_Date__c'].dt.date >= today) & 
            (filtered_df['Price_Increase_Opportunity_Date__c'].dt.date <= six_months)
        ]
        
        # Calculate sum of annual sales value for each time frame
        pi_value_year = price_increase_year['AnnualSalesValue_Converted'].sum()
        pi_value_3m = price_increase_3m['AnnualSalesValue_Converted'].sum()
        pi_value_6m = price_increase_6m['AnnualSalesValue_Converted'].sum()
        
        # Create a dataframe for visualization
        price_increase_data = pd.DataFrame({
            'Time Frame': ['This Year', 'Next 3 Months', 'Next 6 Months'],
            'Total Value': [pi_value_year, pi_value_3m, pi_value_6m],
            'Count': [len(price_increase_year), len(price_increase_3m), len(price_increase_6m)]
        })
        
        # Create a bar chart for price increase opportunities (showing value instead of count)
        fig = px.bar(
            price_increase_data,
            y='Time Frame',
            x='Total Value',
            title=f'Price Increase Opportunities - Total Value ({target_currency})',
            color='Total Value',
            text='Count'  # Show count as text on bars
        )
        fig.update_traces(texttemplate='%{text} contracts', textposition='outside')
        st.plotly_chart(fig)
    except:
        st.subheader("Not enought data to display the analysis")

    try:

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(f"Value Eligible for Price Increase This Year ({target_currency})", f"{pi_value_year:,.2f}")
        
        with col2:
            st.metric(f"Value Eligible for Price Increase Next 3 Months ({target_currency})", f"{pi_value_3m:,.2f}")
        
        with col3:
            st.metric(f"Value Eligible for Price Increase Next 6 Months ({target_currency})", f"{pi_value_6m:,.2f}")
        
        # Top contracts with price increase opportunities
        # with st.expander(f"Top Contracts with Price Increase Opportunities This Year ({target_currency})"):
        top_pi_year = price_increase_year.dropna(subset=['AnnualSalesValue_Converted']).sort_values('AnnualSalesValue_Converted', ascending=False).head(20)
        
        fig = px.bar(
            top_pi_year,
            x='Contract_Description__c', 
            y='AnnualSalesValue_Converted',
            title=f'Top 20 Contracts with Price Increase Opportunities This Year ({target_currency})',
            labels={'Contract_Description__c': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
            hover_data=['ContractNumber', 'ContractCountry__c', 'Price_Increase_Opportunity_Date__c']
        )
        st.plotly_chart(fig)
        
        # KPI 7: Annual Sales Value Distribution
        # st.subheader(f"Annual Sales Value Distribution ({target_currency})")
        
        # # Create histogram of annual sales values
        # fig = px.histogram(
        #     filtered_df.dropna(subset=['AnnualSalesValue_Converted']),
        #     x='AnnualSalesValue_Converted',
        #     nbins=50,
        #     title=f'Distribution of Annual Sales Values ({target_currency})',
        #     labels={'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
        #     marginal='box'
        # )
        # st.plotly_chart(fig)
        
        # Annual sales value by region
        sales_by_region = filtered_df.groupby('ContractRegion__c')['AnnualSalesValue_Converted'].sum().reset_index()
        sales_by_region = sales_by_region.sort_values('AnnualSalesValue_Converted', ascending=False)
        
        fig = px.pie(
            sales_by_region,
            values='AnnualSalesValue_Converted',
            names='ContractRegion__c',
            title=f'Annual Sales Value by Cluster ({target_currency})'
        )
        st.plotly_chart(fig)
        
        # Annual sales value by contract type
        sales_by_type = filtered_df.groupby('EMEA_Type_of_contract__c')['AnnualSalesValue_Converted'].sum().reset_index()
        sales_by_type = sales_by_type.sort_values('AnnualSalesValue_Converted', ascending=False)
        
        fig = px.bar(
            sales_by_type,
            y='AnnualSalesValue_Converted',
            x='EMEA_Type_of_contract__c',  # Reversed axes for better readability
            title=f'Annual Sales Value by Contract Type ({target_currency})',
            labels={'EMEA_Type_of_contract__c': 'Contract Type', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'}
        )
        st.plotly_chart(fig)
    
    except:
        st.subheader("Not enought data to display the analysis")
    # Data table with key information
    st.subheader("Contract Data Table")
    
    # Select relevant columns for the data table
    table_columns = ['ContractNumber', 'Name', 'Status', 'StartDate', 'Contract_End_Date__c', 
                    'ContractRegion__c', 'ContractCountry__c', 'EMEA_Type_of_contract__c',
                    'AnnualSalesValue__c', 'AnnualSalesValue_Converted', 'Price_Increase_Opportunity_Date__c',
                            "Id", 'ConsignmentValue__c','CapitalValue__c', 'TotalProcedureCommitments__c'
]
    
    # Show the data table with the selected columns
    st.dataframe(filtered_df[table_columns].sort_values('StartDate', ascending=False))

else:
    st.info("Please upload a CSV file to begin the analysis.")
    
    # Example structure display
    st.subheader("Expected CSV Structure")
    st.write("The CSV should contain the following columns (among others):")
    
    example_columns = [
        "AccountId", "Sold_To_Account_ID__c", "Buying_Group__c", "ContractNumber", "Name", 
        "EMEA_Type_of_contract__c", "BUs_included_in_Contract__c", "ContractRegion__c", 
        "ContractCountry__c", "Status", "StartDate", "Contract_End_Date__c", 
        "AnnualSalesValue__c", "ActivatedDate", "Price_Increase_Opportunity_Date__c", 
        "ExternalContractID__c",  "Id", 'ConsignmentValue__c','CapitalValue__c', 'TotalProcedureCommitments__c'
    ]
    
    # Display example structure
    example_df = pd.DataFrame(columns=example_columns)
    st.dataframe(example_df)