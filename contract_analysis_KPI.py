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

api_key_to_field_mapping = {
"AccountId": "Account Name",
"Sold_To_Account_ID__c": "Sold To Account ID",
"BUs_included_in_Contract_copy__c": "BUs included in Contract copy",
"Buying_Group__c": "Buying Group",
"Sold_To_Id__c": "Sold To Id",
"ContractNumber": "Contract Number",
"Name": "Contract Name",
"EMEA_Type_of_contract__c": "Type of Contract",
"MainBU__c": "MainBU",
"AdditionalBu__c": "AdditionalBu",
"BUSinglePicklistValue__c": "BUSinglePicklistValue",
"BUs_included_in_Contract__c": "BUs included in Contract",
"Sub_BUs__c": "Sub BUs",
"ContractRegion__c": "Contract Region",
"ContractCountry__c": "Contract Country",
"Old_contract_number__c": "Old contract number",
"SAP_Deal_Number__c": "SAP Deal Number",
"Parent_contract__c": "Parent Contract",
"Contract_Description__c": "Contract Description",
"Document_Link__c": "Document Link",
"Billing_City__c": "Billing City",
"EMEA_Bonus_contract__c": "Bonus Contract",
"Band__c": "Band",
"EMEA_Condition_type__c": "Condition Type",
"Price_Conditions__c": "Price Conditions",
"Terms_of_Payment__c": "Terms of Payment",
"CustomerSignedDate": "Customer Signed Date",
"Status": "Status",
"Canceled_Date__c": "Canceled Date",
"EMEA_Notification_Date__c": "Notification Date",
"StartDate": "Contract Start Date",
"Contract_End_Date__c": "Contract End Date",
"Contract_Original_End_Date__c": "Contract Original End Date",
"Automatic_extension__c": "Automatic Extension",
"Zeitpunkt_der_Erinnerung__c": "Internal Notice Period",
"Erinnerung_senden_an__c": "Person in Charge",
"CustomerSignedId": "Customer Signed By",
"Price_Increase_Opportunity_Date__c": "Price Increase Opportunity Date",
"Price_Regulations_Notes__c": "Price Regulations Notes",
"Notice_Period__c": "Notice Period",
"EMEA_Bonus_type__c": "Bonus Type",
"EMEA_Expected_Sales__c": "Expected Sales",
"ExpectedPayoutPercentage__c": "Expected Payout Percentage",
"EMEA_Payout_period__c": "Payout Period",
"EMEA_Bonus_beneficiary__c": "Bonus Beneficiary",
"EMEA_Bonus_conditions__c": "Bonus Description",
"EMEA_Booking_Type__c": "Booking Type",
"Rebate_Conditions__c": "Rebate Conditions",
"SpecificServiceLevels__c": "Specific Service Levels",
"CapitalValue__c": "Capital Value",
"CapitalValueDescription__c": "Capital Value Description",
"ConsignmentValue__c": "Consignment Value",
"ConsignmentValueDescription__c": "Consignment Value Description",
"AnnualSalesValue__c": "Annual Sales Value",
"MarketShare__c": "Market Share %",
"TotalProcedureCommitments__c": "Total Procedure Commitments",
"QuantityAgreed__c": "Quantity Agreed",
"HipProceduresCommitment__c": "Hip Procedures Commitment",
"KneeProceduresCommitment__c": "Knee Procedures Commitment",
"Kits__c": "Kits",
"Canister__c": "Canister",
"EMEA_Volume_annually__c": "Volume annually",
"Inkludierte_Gerte__c": "Inkludierte Geräte",
"Ambulante_Erstattung__c": "Ambulante Erstattung",
"Therapy_days__c": "Therapy days",
"Costs_per_Therapy_day__c": "Costs per Therapy day",
"Flat_rate_month__c": "Flat rate (month)",
"More_included_items__c": "More included items",
# System Information
"ActivatedById": "Activated By",
"CreatedById": "Created By",
"CurrencyIsoCode": "Contract Currency",
"ActivatedDate": "Activated Date",
"LastModifiedById": "Last Modified By",
"OwnerId": "Contract Owner"

} 

def rename_columns(df, mapping):
# Create a new dictionary for renaming columns
    rename_dict = {col: mapping.get(col, col) for col in df.columns}

# Rename the columns using the dictionary
    df.rename(columns=rename_dict, inplace=True)

def rename_kpi_columns(kpi_columns, mapping):
# Rename the KPI columns using the mapping
    renamed_kpi_columns = [mapping.get(col, col) for col in kpi_columns]
    return renamed_kpi_columns

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
        date_columns = ['CustomerSignedDate', 'Canceled_Date__c', 'Notification Date', 
                       'StartDate', 'Contract_End_Date__c', 'Contract_Original_End_Date__c',
                       'Price Increase Opportunity Date', 'LastEvaluationDate__c', 
                       'Activated Date']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Rename the columns in the DataFrame
        rename_columns(df, api_key_to_field_mapping)

        # Process AnnualSalesValue__c to extract numeric values and currency
        if 'Annual Sales Value' in df.columns:
            try:
                # Create new columns for numeric value and currency
                df['AnnualSalesValue_Numeric'] = np.nan
                df['AnnualSalesValue_Currency'] = 'USD'
                
                # Process each row
                for idx, value in df['Annual Sales Value'].items():
                    try:
                        result = extract_numeric_value(value)
                        if isinstance(result, tuple):
                            df.at[idx, 'AnnualSalesValue_Numeric'] = result[0]
                            df.at[idx, 'AnnualSalesValue_Currency'] = result[1]
                        else:
                            df.at[idx, 'AnnualSalesValue_Numeric'] = result
                    except:
                        pass
            except:
                df['AnnualSalesValue_Numeric'] = df['Annual Sales Value']
                if 'Annual Sales Value Currency' in df.columns:
                    df['AnnualSalesValue_Currency'] = df['Annual Sales Value Currency']
                else:
                    df['AnnualSalesValue_Currency'] = 'USD'
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
    try:
        contract_types = st.sidebar.multiselect(
            "Select Contract Types",
            options=df['Type of Contract'].dropna().unique(),
            default=[]
        )
    except:
        contract_types = []

    try:
        bus_included = st.sidebar.multiselect(
            "Select BUs included in Contract",
            options=df['BUs included in Contract'].dropna().unique(),
            default=[]
        )
    except:
        bus_included = []

    try:
        regions = st.sidebar.multiselect(
            "Select Contract Clusters",
            options=df['Contract Region'].dropna().unique(),
            default=[]
        )
    except:
        regions = [] 

    try:   
        countries = st.sidebar.multiselect(
            "Select Contract Countries",
            options=df['Contract Country'].dropna().unique(),
            default=[]
        )
    except:
        countries = []

    try:
        statuses = st.sidebar.multiselect(
            "Select Contract Status",
            options=df['Status'].dropna().unique(),
            default=[]
        )
    except:
        statuses = []

    volume_agreement = st.sidebar.multiselect(
        "Volume Based Agreement - Active",
        options=['Yes','No'],
        default=['No']
    )
    # KPI relevant columns
    kpi_columns_default = ['Status', 'Contract Start Date', 'Contract End Date', 'Annual Sales Value', 
                  'Activated Date', 'Price Increase Opportunity Date', 'Notification Date',
                  'Consignment Value','Capital Value', 'Total Procedure Commitments','SAP Deal Number'
                  ]
    
    try:
        kpi_columns = st.sidebar.multiselect(
            "Select KPI columns",
            options=df.columns,
            default=kpi_columns_default
        )
    except:
        kpi_columns = st.sidebar.multiselect(
        "Select KPI columns",
        options=df.columns,
        default=df.columns
    )
    
            # Rename the KPI columns
    kpi_columns = rename_kpi_columns(kpi_columns, api_key_to_field_mapping)

    # Apply filters
    filtered_df = df.copy()
    
    if contract_types:
        filtered_df = filtered_df[filtered_df['Type of Contract'].isin(contract_types)]
    
    if bus_included:
        filtered_df = filtered_df[filtered_df['BUs included in Contract'].isin(bus_included)]
    
    if regions:
        filtered_df = filtered_df[filtered_df['Contract Region'].isin(regions)]
    
    if countries:
        filtered_df = filtered_df[filtered_df['Contract Country'].isin(countries)]
    
    if statuses:
        filtered_df = filtered_df[filtered_df['Status'].isin(statuses)]
    try:
        if 'Yes' in volume_agreement:
            filtered_df = filtered_df[(filtered_df['Status'].isin(['Active'])) & (filtered_df['Type of Contract'].isin(['Usage agreement'])) ]
            kpi_columns = [ 'Annual Sales Value',  'Capital Value', 'Capital Value Description', 'Consignment Value', 'Consignment Value Description'
                    , 'Total Procedure Commitments','Quantity Agreed', 'Hip Procedures Commitment', 'Knee Procedures Commitment']
    except:
        pass
    
    # Data Quality Analysis
    st.header("Data Quality Analysis")

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

    try:
        # Calculate missing values by BU
        st.subheader("Missing Data by Clusters")

        # Create a function to calculate missing percentage for each KPI column by BU
        def calculate_missing_by_reg(dataframe, column_list):
            # Get all regions
            regions = dataframe['Contract Region'].dropna().unique()
            
            # Create empty dictionary to store results
            result_data = []
            
            # Loop through each BU and calculate missing values for each KPI column
            for r in regions:
                reg_df = dataframe[dataframe['Contract Region'] == r]
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
        missing_by_reg = calculate_missing_by_reg(filtered_df, kpi_columns)

    # Create a heatmap of missing values by region
        if not missing_by_reg.empty:
            fig = px.bar(
                missing_by_reg,
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
                missing_by_reg.pivot(index='Region', columns='Column', values='Missing Percentage'),
                labels=dict(x="Column", y="Region", color="Missing Percentage"),
                color_continuous_scale='YlOrRd',
                title='Missing Data Heatmap by Cluster'
            )
            st.plotly_chart(fig2)
            

            # Show table of missing values by BU
            with st.expander("View Detailed Missing Data by Cluster"):
                st.dataframe(missing_by_reg.sort_values(['Region', 'Missing Percentage'], ascending=[True, False]))
        else:
            st.warning("No region information available to analyze missing data by BU.")
    except:
        pass

    try:
            
        # Calculate missing values by Country
        st.subheader("Missing Data by Countries")

        def calculate_missing_by_country(dataframe, column_list):
            # Get all regions
            countries = dataframe['Contract Country'].dropna().unique()
            
            # Create empty dictionary to store results
            result_data = []
            
            # Loop through each BU and calculate missing values for each KPI column
            for c in countries:
                country_df = dataframe[dataframe['Contract Country'] == c]
                country_total = len(country_df)
                
                if country_total > 0:  # Avoid division by zero
                    for col in column_list:
                        if col in country_df.columns:
                            missing_count = country_df[col].isna().sum()
                            missing_pct = (missing_count / country_total * 100).round(2)
                            
                            result_data.append({
                                'Country': c,
                                'Column': col,
                                'Missing Percentage': missing_pct,
                                'Total Contracts': country_total
                            })
            
            return pd.DataFrame(result_data)

        # Calculate missing values by BU for KPI columns
        missing_by_country = calculate_missing_by_country(filtered_df, kpi_columns)
        if not missing_by_country.empty:

            fig3 = px.imshow(
                missing_by_country.pivot(index='Column', columns='Country', values='Missing Percentage'),
                labels=dict(x="Country", y="Column", color="Missing Percentage"),
                color_continuous_scale='YlOrRd',
                title='Missing Data Heatmap by Country'
            )
            st.plotly_chart(fig3)
    except:
        pass

        # Calculate missing values by Country
    st.subheader("Missing Data by Business Unit")

    def calculate_missing_by_bu(dataframe, column_list):
        # Get all regions
        bus = dataframe['BUs included in Contract'].dropna().unique()
        
        # Create empty dictionary to store results
        result_data = []
        
        # Loop through each BU and calculate missing values for each KPI column
        for bu in bus:
            bu_df = dataframe[dataframe['BUs included in Contract'] == bu]
            bu_total = len(bu_df)
            
            if bu_total > 0:  # Avoid division by zero
                for col in column_list:
                    if col in bu_df.columns:
                        missing_count = bu_df[col].isna().sum()
                        missing_pct = (missing_count / bu_total * 100).round(2)
                        
                        result_data.append({
                            'BU': bu,
                            'Column': col,
                            'Missing Percentage': missing_pct,
                            'Total Contracts': bu_total
                        })
        
        return pd.DataFrame(result_data)

    # Calculate missing values by BU for KPI columns
    missing_by_bu = calculate_missing_by_bu(filtered_df, kpi_columns)
    if not missing_by_bu.empty:

        fig4 = px.imshow(
            missing_by_bu.pivot(index='Column', columns='BU', values='Missing Percentage'),
            labels=dict(x="BU", y="Column", color="Missing Percentage"),
            color_continuous_scale='YlOrRd',
            title='Missing Data Heatmap by Business Unit',
            width=100000,
            height=800
        )
        st.plotly_chart(fig4)

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
    
    try:
            
        # KPI 2: Top 20 contracts per annual sales value
        
        # Sort by annual sales value and get top 20
        top_contracts = filtered_df.dropna(subset=['AnnualSalesValue_Converted']).sort_values('AnnualSalesValue_Converted', ascending=False).head(20)
        
        # Create a horizontal bar chart for top contracts
        fig = px.bar(
            top_contracts,
            x='Contract Description', 
            y='AnnualSalesValue_Converted',
            title=f'Top 20 Contracts by Annual Sales Value ({target_currency})',
            labels={'Contract Description': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
            hover_data=['Contract Number', 'Contract Country', 'Type of Contract']
        )
        st.plotly_chart(fig)

        # Filter contracts with activation date
        contracts_with_activation = filtered_df.dropna(subset=['Activated Date'])        
        if len(contracts_with_activation)>0:

            # KPI 3: Contracts activated per month
            
            # Extract year and month from activation date
            contracts_with_activation['ActivationMonth'] = contracts_with_activation['Activated Date'].dt.to_period('M')
            
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
            x='Contract Description', 
            y='AnnualSalesValue_Converted',
            title=f'Top 20 Activated Contracts by Annual Sales Value ({target_currency})',
            labels={'Contract Description': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
            hover_data=['Contract Number', 'Contract Country', 'Type of Contract', 'Activated Date']
        )
        st.plotly_chart(fig)
        
        # KPI 4: Contracts sent out but not activated
        st.subheader("Contracts Sent Out but Not Activated")
        
        # Find contracts with notification date but no activation date or with status not activated
        sent_not_activated = filtered_df[
            (filtered_df['Notification Date'].notna()) & 
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
            x='Contract Description',  
            y='AnnualSalesValue_Converted',
            title=f'Top 20 Contracts Sent but Not Activated by Annual Sales Value ({target_currency})',
            labels={'Contract Description': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
            hover_data=['Contract Number', 'Contract Country', 'Type of Contract', 'Notification Date']
        )
        st.plotly_chart(fig)
        
        # KPI 5: Expiring contracts
        st.subheader("Expiring Contracts Analysis")
        
        # Get current date
        today = datetime.now().date()
        
        # Calculate expiration dates
        expiring_this_year = filtered_df[
            (filtered_df['Contract End Date'].dt.year == today.year) & 
            (filtered_df['Contract End Date'].dt.date >= today)
        ]
        
        three_months = today + timedelta(days=90)
        expiring_next_3months = filtered_df[
            (filtered_df['Contract End Date'].dt.date >= today) & 
            (filtered_df['Contract End Date'].dt.date <= three_months)
        ]
        
        six_months = today + timedelta(days=180)
        expiring_next_6months = filtered_df[
            (filtered_df['Contract End Date'].dt.date >= today) & 
            (filtered_df['Contract End Date'].dt.date <= six_months)
        ]
        
        # Define "not followed up" as those without notification date
        not_followed_year = expiring_this_year[expiring_this_year['Notification Date'].isna()]
        not_followed_3m = expiring_next_3months[expiring_next_3months['Notification Date'].isna()]
        not_followed_6m = expiring_next_6months[expiring_next_6months['Notification Date'].isna()]
        
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
            x='Contract Description', 
            y='AnnualSalesValue_Converted',
            title=f'Top 20 Contracts Expiring This Year by Annual Sales Value ({target_currency})',
            labels={'Contract Description': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
            hover_data=['Contract Number', 'Contract Country', 'Contract End Date']
        )
        st.plotly_chart(fig)
        
        # KPI 6: Price Increase Opportunity
        st.subheader("Price Increase Opportunities")

        try:
            # Price increase opportunities in different time frames
            price_increase_year = filtered_df[
                (filtered_df['Price Increase Opportunity Date'].dt.year == today.year) & 
                (filtered_df['Price Increase Opportunity Date'].dt.date >= today)
            ]
            
            price_increase_3m = filtered_df[
                (filtered_df['Price Increase Opportunity Date'].dt.date >= today) & 
                (filtered_df['Price Increase Opportunity Date'].dt.date <= three_months)
            ]
            
            price_increase_6m = filtered_df[
                (filtered_df['Price Increase Opportunity Date'].dt.date >= today) & 
                (filtered_df['Price Increase Opportunity Date'].dt.date <= six_months)
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
                x='Contract Description', 
                y='AnnualSalesValue_Converted',
                title=f'Top 20 Contracts with Price Increase Opportunities This Year ({target_currency})',
                labels={'Contract Description': 'Contract Name', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'},
                hover_data=['Contract Number', 'Contract Country', 'Price Increase Opportunity Date']
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
            sales_by_region = filtered_df.groupby('Contract Region')['AnnualSalesValue_Converted'].sum().reset_index()
            sales_by_region = sales_by_region.sort_values('AnnualSalesValue_Converted', ascending=False)
            
            fig = px.pie(
                sales_by_region,
                values='AnnualSalesValue_Converted',
                names='Contract Region',
                title=f'Annual Sales Value by Cluster ({target_currency})'
            )
            st.plotly_chart(fig)
            
            # Annual sales value by contract type
            sales_by_type = filtered_df.groupby('Type of Contract')['AnnualSalesValue_Converted'].sum().reset_index()
            sales_by_type = sales_by_type.sort_values('AnnualSalesValue_Converted', ascending=False)
            
            fig = px.bar(
                sales_by_type,
                y='AnnualSalesValue_Converted',
                x='Type of Contract',  # Reversed axes for better readability
                title=f'Annual Sales Value by Contract Type ({target_currency})',
                labels={'Type of Contract': 'Contract Type', 'AnnualSalesValue_Converted': f'Annual Sales Value ({target_currency})'}
            )
            st.plotly_chart(fig)
        
        except:
            st.subheader("Not enought data to display the analysis")
        # Data table with key information
        st.subheader("Contract Data Table")

    except:
        pass

    # Select relevant columns for the data table
    fixed_columns = ["Id",'Contract Number', 'Contract Name', 'Contract Region', 'Contract Country']
    table_columns = fixed_columns + kpi_columns
    # "Id",'ContractNumber', 'Name', 'ContractRegion__c', 'ContractCountry__c' + KPI data
#     table_columns = ['ContractNumber', 'Name', 'Status', 'StartDate', 'Contract_End_Date__c', 
#                     'ContractRegion__c', 'ContractCountry__c', 'EMEA_Type_of_contract__c',
#                     'AnnualSalesValue__c', 'AnnualSalesValue_Converted', 'Price_Increase_Opportunity_Date__c',
#                             "Id", 'ConsignmentValue__c','CapitalValue__c', 'TotalProcedureCommitments__c', 
#                             'SAP_Deal_Number__c'
# ]
    
    # Show the data table with the selected columns
    try:
        filtered_df = filtered_df[filtered_df[table_columns].isnull().any(axis=1)]

        if 'StartDate' in table_columns:
            
            st.dataframe(filtered_df[table_columns].sort_values('StartDate', ascending=False))
        else:
            st.dataframe(filtered_df[table_columns].sort_values('Contract Number', ascending=False))

    except:
        st.dataframe(filtered_df.sort_values('Contract Number', ascending=False))

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