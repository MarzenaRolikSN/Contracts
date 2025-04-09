import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Contract Data Analysis", layout="wide")

st.title("Contract Data Analysis Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload Contract Data CSV", type=["csv"])

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
        
        return df
    
    df = load_data(uploaded_file)
    
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
        "Select Contract Regions",
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
                  'ActivatedDate', 'Price_Increase_Opportunity_Date__c', 'EMEA_Notification_Date__c']
    
    # Calculate missing values percentage
    missing_values = pd.DataFrame({
        'Column': df.columns,
        'Missing Values': df.isna().sum(),
        'Missing Percentage': (df.isna().sum() / len(df) * 100).round(2)
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
    
    # Show overall data statistics
    with st.expander("Show Full Data Quality Statistics"):
        st.dataframe(missing_values)
    
    # Define active contracts (Status = 'Active' or similar)
    active_contracts = filtered_df[filtered_df['Status'] == 'Activated']
    
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
    st.subheader("Top 20 Contracts per Annual Sales Value")
    
    # Convert AnnualSalesValue__c to numeric if it's not already
    filtered_df['AnnualSalesValue__c'] = pd.to_numeric(filtered_df['AnnualSalesValue__c'], errors='coerce')
    
    # Sort by annual sales value and get top 20
    top_contracts = filtered_df.sort_values('AnnualSalesValue__c', ascending=False).head(20)
    
    # Create a bar chart for top contracts
    fig = px.bar(
        top_contracts,
        x='ContractNumber',
        y='AnnualSalesValue__c',
        title='Top 20 Contracts by Annual Sales Value',
        labels={'ContractNumber': 'Contract Number', 'AnnualSalesValue__c': 'Annual Sales Value'},
        hover_data=['Name', 'ContractCountry__c', 'EMEA_Type_of_contract__c']
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
    st.subheader("Top 20 Activated Contracts per Annual Sales Value")
    
    top_activated = contracts_with_activation.sort_values('AnnualSalesValue__c', ascending=False).head(20)
    
    fig = px.bar(
        top_activated,
        x='ContractNumber',
        y='AnnualSalesValue__c',
        title='Top 20 Activated Contracts by Annual Sales Value',
        labels={'ContractNumber': 'Contract Number', 'AnnualSalesValue__c': 'Annual Sales Value'},
        hover_data=['Name', 'ContractCountry__c', 'EMEA_Type_of_contract__c', 'ActivatedDate']
    )
    st.plotly_chart(fig)
    
    # KPI 4: Contracts sent out but not activated
    st.subheader("Contracts Sent Out but Not Activated")
    
    # Find contracts with notification date but no activation date or with status not activated
    sent_not_activated = filtered_df[
        (filtered_df['EMEA_Notification_Date__c'].notna()) & 
        ((filtered_df['ActivatedDate'].isna()) | (filtered_df['Status'] != 'Activated'))
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Contracts Sent Not Activated", len(sent_not_activated))
    
    with col2:
        sent_percentage = round((len(sent_not_activated) / len(filtered_df)) * 100, 2) if len(filtered_df) > 0 else 0
        st.metric("Percentage of Total", f"{sent_percentage}%")
    
    # Top 20 sent but not activated contracts per annual sales value
    top_sent_not_activated = sent_not_activated.sort_values('AnnualSalesValue__c', ascending=False).head(20)
    
    fig = px.bar(
        top_sent_not_activated,
        x='ContractNumber',
        y='AnnualSalesValue__c',
        title='Top 20 Contracts Sent but Not Activated by Annual Sales Value',
        labels={'ContractNumber': 'Contract Number', 'AnnualSalesValue__c': 'Annual Sales Value'},
        hover_data=['Name', 'ContractCountry__c', 'EMEA_Type_of_contract__c', 'EMEA_Notification_Date__c']
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
    total_value_year = expiring_this_year['AnnualSalesValue__c'].sum()
    total_value_3m = expiring_next_3months['AnnualSalesValue__c'].sum()
    total_value_6m = expiring_next_6months['AnnualSalesValue__c'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Value Expiring This Year", f"{total_value_year:,.2f}")
    
    with col2:
        st.metric("Total Value Expiring Next 3 Months", f"{total_value_3m:,.2f}")
    
    with col3:
        st.metric("Total Value Expiring Next 6 Months", f"{total_value_6m:,.2f}")
    
    # Top contracts expiring
    with st.expander("Top Contracts Expiring This Year"):
        top_expiring_year = expiring_this_year.sort_values('AnnualSalesValue__c', ascending=False).head(20)
        
        fig = px.bar(
            top_expiring_year,
            x='ContractNumber',
            y='AnnualSalesValue__c',
            title='Top 20 Contracts Expiring This Year by Annual Sales Value',
            labels={'ContractNumber': 'Contract Number', 'AnnualSalesValue__c': 'Annual Sales Value'},
            hover_data=['Name', 'ContractCountry__c', 'Contract_End_Date__c']
        )
        st.plotly_chart(fig)
    
    # KPI 6: Price Increase Opportunity
    st.subheader("Price Increase Opportunities")
    
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
    
    # Create a dataframe for visualization
    price_increase_data = pd.DataFrame({
        'Time Frame': ['This Year', 'Next 3 Months', 'Next 6 Months'],
        'Count': [len(price_increase_year), len(price_increase_3m), len(price_increase_6m)]
    })
    
    # Create a bar chart for price increase opportunities
    fig = px.bar(
        price_increase_data,
        x='Time Frame',
        y='Count',
        title='Price Increase Opportunities',
        color='Count'
    )
    st.plotly_chart(fig)
    
    # Calculate total value eligible for price increase
    total_pi_value_year = price_increase_year['AnnualSalesValue__c'].sum()
    total_pi_value_3m = price_increase_3m['AnnualSalesValue__c'].sum()
    total_pi_value_6m = price_increase_6m['AnnualSalesValue__c'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Value Eligible for Price Increase This Year", f"{total_pi_value_year:,.2f}")
    
    with col2:
        st.metric("Value Eligible for Price Increase Next 3 Months", f"{total_pi_value_3m:,.2f}")
    
    with col3:
        st.metric("Value Eligible for Price Increase Next 6 Months", f"{total_pi_value_6m:,.2f}")
    
    # Top contracts with price increase opportunities
    with st.expander("Top Contracts with Price Increase Opportunities This Year"):
        top_pi_year = price_increase_year.sort_values('AnnualSalesValue__c', ascending=False).head(20)
        
        fig = px.bar(
            top_pi_year,
            x='ContractNumber',
            y='AnnualSalesValue__c',
            title='Top 20 Contracts with Price Increase Opportunities This Year by Annual Sales Value',
            labels={'ContractNumber': 'Contract Number', 'AnnualSalesValue__c': 'Annual Sales Value'},
            hover_data=['Name', 'ContractCountry__c', 'Price_Increase_Opportunity_Date__c']
        )
        st.plotly_chart(fig)
    
    # KPI 7: Annual Sales Value Distribution
    st.subheader("Annual Sales Value Distribution")
    
    # Create histogram of annual sales values
    fig = px.histogram(
        filtered_df.dropna(subset=['AnnualSalesValue__c']),
        x='AnnualSalesValue__c',
        nbins=50,
        title='Distribution of Annual Sales Values',
        labels={'AnnualSalesValue__c': 'Annual Sales Value'},
        marginal='box'
    )
    st.plotly_chart(fig)
    
    # Annual sales value by region
    sales_by_region = filtered_df.groupby('ContractRegion__c')['AnnualSalesValue__c'].sum().reset_index()
    sales_by_region = sales_by_region.sort_values('AnnualSalesValue__c', ascending=False)
    
    fig = px.pie(
        sales_by_region,
        values='AnnualSalesValue__c',
        names='ContractRegion__c',
        title='Annual Sales Value by Region'
    )
    st.plotly_chart(fig)
    
    # Annual sales value by contract type
    sales_by_type = filtered_df.groupby('EMEA_Type_of_contract__c')['AnnualSalesValue__c'].sum().reset_index()
    sales_by_type = sales_by_type.sort_values('AnnualSalesValue__c', ascending=False)
    
    fig = px.bar(
        sales_by_type,
        x='EMEA_Type_of_contract__c',
        y='AnnualSalesValue__c',
        title='Annual Sales Value by Contract Type',
        labels={'EMEA_Type_of_contract__c': 'Contract Type', 'AnnualSalesValue__c': 'Annual Sales Value'}
    )
    st.plotly_chart(fig)
    
    # Data table with key information
    st.subheader("Contract Data Table")
    
    # Select relevant columns for the data table
    table_columns = ['ContractNumber', 'Name', 'Status', 'StartDate', 'Contract_End_Date__c', 
                    'ContractRegion__c', 'ContractCountry__c', 'EMEA_Type_of_contract__c',
                    'AnnualSalesValue__c', 'Price_Increase_Opportunity_Date__c']
    
    # Show the data table with the selected columns
    st.dataframe(filtered_df[table_columns].sort_values('ContractNumber'))

else:
    st.info("Please upload a CSV file to begin the analysis.")
    
    # Example structure display
    st.subheader("Expected CSV Structure")
    st.write("The CSV should contain the following columns (among others):")
    
    example_columns = [
        "AccountId", "Sold_To_Account_ID__c", "Buying_Group__c", "ContractNumber", "Name", 
        "EMEA_Type_of_contract__c", "BUs_included_in_Contract__c", "ContractRegion__c", 
        "ContractCountry__c", "Status", "StartDate", "Contract_End_Date__c", 
        "AnnualSalesValue__c", "ActivatedDate", "Price_Increase_Opportunity_Date__c"
    ]
    
    # Display example structure
    example_df = pd.DataFrame(columns=example_columns)
    st.dataframe(example_df)