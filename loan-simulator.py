import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import io

# Define translations
translations = {
    'en': {
        'title': 'Loan Simulator',
        'other_simulators': 'Other Simulators',
        'savings_simulator': 'Savings Simulator',
        'sidebar_title': 'Simulation Parameters',
        'loan_amount': 'Loan Amount',
        'duration': 'Duration (years)',
        'interest_rate': 'Annual Interest Rate (%)',
        'insurance_rate': 'Insurance Rate (%)',
        'monthly_payment': 'Monthly Payment: {payment}',
        'capital_avg': 'Average Capital: {capital_avg}',
        'interest_avg': 'Average Interest: {interest_avg}',
        'insurance_avg': 'Average Insurance: {insurance_avg}',
        'total_cost': 'Total Cost: {total_cost}',
        'interest_cost': 'Interest Cost: {interest_cost}',
        'insurance_cost': 'Insurance Cost: {insurance_cost}',
        'table_title': 'Loan Amortization Schedule',
        'download_csv': 'Download CSV'
    },
    'fr': {
        'title': 'Simulateur d\'Emprunt',
        'other_simulators': 'Autres Simulateurs',
        'savings_simulator': 'Simulateur d\'Épargne',
        'sidebar_title': 'Paramètres de Simulation',
        'loan_amount': 'Montant de l\'Emprunt',
        'duration': 'Durée (années)',
        'interest_rate': 'Taux d\'Intérêt Annuel (%)',
        'insurance_rate': 'Taux d\'Assurance (%)',
        'monthly_payment': 'Mensualités: {payment}',
        'capital_avg': 'Capital Moyen: {capital_avg}',
        'interest_avg': 'Intérêts Moyens: {interest_avg}',
        'insurance_avg': 'Assurance Moyenne: {insurance_avg}',
        'total_cost': 'Coût Total: {total_cost}',
        'interest_cost': 'Coût des Intérêts: €{interest_cost}',
        'insurance_cost': 'Coût de l\'Assurance: {insurance_cost}',
        'table_title': 'Tableau d\'Amortissement',
        'download_csv': 'Télécharger CSV'
    }
}

def get_translations(lang):
    return translations.get(lang, translations['en'])

def calculate_loan_schedule(loan_amount, duration, annual_rate, insurance_rate):
    months = duration * 12
    monthly_rate = annual_rate / 12 / 100
    insurance_monthly_rate = insurance_rate / 12 / 100

    # Calculate monthly payment using the formula for annuity
    if monthly_rate > 0:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment = loan_amount / months
    
    insurance_monthly_payment = loan_amount * insurance_monthly_rate

    # Initialize lists for results
    annuities = []
    interests = []
    insurances = []
    remaining_capital = loan_amount

    for month in range(1, months + 1):
        interest_payment = remaining_capital * monthly_rate
        capital_payment = monthly_payment - interest_payment
        
        # If capital_payment is greater than remaining_capital, adjust it
        if capital_payment > remaining_capital:
            capital_payment = remaining_capital
            monthly_payment = interest_payment + capital_payment
        
        remaining_capital -= capital_payment
        # Ensure remaining_capital does not go below zero
        if remaining_capital < 0:
            remaining_capital = 0

        annuities.append(round(monthly_payment, 2))
        interests.append(round(interest_payment, 2))
        insurances.append(round(insurance_monthly_payment, 2))

    # Calculate totals
    total_cost = round(sum(annuities), 2)
    interest_cost = round(sum(interests), 2)
    insurance_cost = round(sum(insurances), 2)

    # Initialize lists for annual data
    years = []
    annual_annuity = []
    annual_interest = []
    annual_insurance = []
    annual_remaining_capital = []

    # Aggregate monthly data into annual data
    remaining_capital = loan_amount  # Reset remaining capital for annual aggregation

    for year in range(duration):
        start_month = year * 12
        end_month = start_month + 12
        if end_month > months:
            end_month = months

        annual_annuity.append(round(sum(annuities[start_month:end_month]), 2))
        annual_interest.append(round(sum(interests[start_month:end_month]), 2))
        annual_insurance.append(round(sum(insurances[start_month:end_month]), 2))
        annual_remaining_capital.append(round(remaining_capital, 2))

        # Calculate the remaining capital at the end of the year
        for month in range(start_month, end_month):
            interest_payment = remaining_capital * monthly_rate
            capital_payment = annuities[month] - interest_payment
            if capital_payment > remaining_capital:
                capital_payment = remaining_capital
            remaining_capital -= capital_payment
            if remaining_capital < 0:
                remaining_capital = 0

        years.append(year + 1)

    # Create a DataFrame for the table
    df = pd.DataFrame({
        'Year': years,
        'Annuity': annual_annuity,
        'Interest': annual_interest,
        'Insurance': annual_insurance,
        'Remaining Capital': annual_remaining_capital
    })

    # Calculate averages
    capital_avg = round((loan_amount - remaining_capital) / duration, 2)
    interest_avg = round(interest_cost / duration, 2)
    insurance_avg = round(insurance_cost / duration, 2)
    
    return monthly_payment, capital_avg, interest_avg, insurance_avg, total_cost, interest_cost, insurance_cost, df


def plot_amortization_schedule(df, colors, currency_symbol):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Annuity'], mode='lines+markers', name='Annuités', line=dict(color=colors['annuity'])))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Interest'], mode='lines+markers', name='Intérêts', line=dict(color=colors['interest'])))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Insurance'], mode='lines+markers', name='Assurance', line=dict(color=colors['insurance'])))
    
    fig.update_layout(
        title=translations[lang]['table_title'],
        xaxis_title='Year',
        yaxis_title=f'Amount ({currency_symbol})',
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            tickvals=df['Year'].tolist(),
            ticktext=[str(int(year)) for year in df['Year'].tolist()]
        ),
        yaxis=dict(
            title=f'Amount ({currency_symbol})',
            gridcolor='rgba(0,0,0,0.1)'
        ),
        margin=dict(l=0, r=0, t=80, b=0),
        legend=dict(
            x=0, 
            y=1.1, 
            orientation='h',
            bordercolor='rgba(0,0,0,0.1)'
        ),
        hovermode='closest'
    )
    
    return fig

def convert_df_to_csv(df):
    """Convert DataFrame to CSV format."""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()

# Streamlit app
st.set_page_config(page_title=translations['en']['title'], layout='wide')

# Language selection
lang = st.sidebar.selectbox('Select Language', options=['en', 'fr'])

# Get translations based on selected language
trans = get_translations(lang)

st.title(trans['title'])

st.markdown(f"""
    <style>
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            border-bottom: 1px solid #ddd;
        }}
        .title {{
            font-size: 2rem;
            margin: 0;
        }}
        .dropdown {{
            position: relative;
            display: inline-block;
        }}
        .dropbtn {{
            background-color:   #0083ff;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }}
        .dropdown-content {{
            display: none;
            position: absolute;
            background-color: #f1f1f1;
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
            border-radius: 4px;
            overflow: hidden;
        }}
        .dropdown-content a {{
            color: black;
            padding: 12px 16px;
            text-decoration: none;
            display: block;
        }}
        .dropdown-content a:hover {{
            background-color: #ddd;
        }}
        .dropdown:hover .dropdown-content {{
            display: block;
        }}
        .dropdown:hover .dropbtn {{
            background-color: #00bcff;
        }}
    </style>
    <div class="header">
        <h2 class="title">{trans['title']}</h2>
        <div class="dropdown">
            <button class="dropbtn">{trans['other_simulators']}</button>
            <div class="dropdown-content">
                <a href="https://savingssimulator.streamlit.app/" target="_blank">{trans['savings_simulator']}</a>
                <!-- You can add more links here -->
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Currency selection
currency_options = {
    '$': 'US Dollar',
    '€': 'Euro',
    '¥': 'Japanese Yen',
    '£': 'British Pound Sterling',
    'AU$': 'Australian Dollar',
    'C$': 'Canadian Dollar',
    'CHF': 'Swiss Franc',
    '¥': 'Chinese Yuan',
    'kr': 'Swedish Krona',
    'NZ$': 'New Zealand Dollar'
}
currency_symbol = st.sidebar.selectbox('Select Currency', options=list(currency_options.keys()))

# Sidebar with input fields and sliders
st.sidebar.header(trans['sidebar_title'])

# Loan Amount
loan_amount = st.sidebar.slider(trans['loan_amount'], min_value=0, max_value=1000000, value=100000, step=1000)
custom_loan_amount = st.sidebar.number_input('Or enter amount manually:', min_value=0, max_value=1000000, value=loan_amount, step=1000)
loan_amount = custom_loan_amount if custom_loan_amount != loan_amount else loan_amount

# Duration
duration = st.sidebar.slider(trans['duration'], min_value=1, max_value=50, value=10)

# Interest Rate
annual_rate = st.sidebar.slider(trans['interest_rate'], min_value=0.0, max_value=20.0, value=3.0, step=0.1)

# Insurance Rate
insurance_rate = st.sidebar.slider(trans['insurance_rate'], min_value=0.0, max_value=5.0, value=1.0, step=0.1)

# Calculate and display results
monthly_payment, capital_avg, interest_avg, insurance_avg, total_cost, interest_cost, insurance_cost, df = calculate_loan_schedule(
    loan_amount, duration, annual_rate, insurance_rate)

st.subheader(trans['monthly_payment'].format(payment=f"{currency_symbol}{monthly_payment:,.2f}"))
st.write(trans['capital_avg'].format(capital_avg=f"{currency_symbol}{capital_avg:,.2f}"))
st.write(trans['interest_avg'].format(interest_avg=f"{currency_symbol}{interest_avg:,.2f}"))
st.write(trans['insurance_avg'].format(insurance_avg=f"{currency_symbol}{insurance_avg:,.2f}"))
st.write(trans['total_cost'].format(total_cost=f"{currency_symbol}{total_cost:,.2f}"))
st.write(f"{trans['interest_cost'].format(interest_cost=f'{currency_symbol}{interest_cost:,.2f}')}")
st.write(f"{trans['insurance_cost'].format(insurance_cost=f'{currency_symbol}{insurance_cost:,.2f}')}")


# Plot and display table
fig = plot_amortization_schedule(df, colors={'annuity': '#1f77b4', 'interest': '#ff7f0e', 'insurance': '#2ca02c'}, currency_symbol=currency_symbol)
st.plotly_chart(fig, use_container_width=True)

# Display table
st.dataframe(df)

# Download CSV
csv = convert_df_to_csv(df)
st.download_button(
    label=trans['download_csv'],
    data=csv,
    file_name='loan_amortization_schedule.csv',
    mime='text/csv'
)

st.markdown("""
    <div style="text-align: center; padding-top: 100px;">
        <a href="https://github.com/czantoine/Savings-Simulator" target="_blank">
            <img src="https://img.shields.io/github/stars/czantoine/Loan-Simulator?style=social" alt="Star on GitHub">
        </a>
    </div>
    <div style="text-align: center; padding-top: 20px;">
        <a href="https://www.linkedin.com/in/antoine-cichowicz-837575b1/" target="_blank" style="margin: 0; padding: 0; display: inline-block;">
            <i class="fab fa-linkedin" style="font-size: 30px; margin: 0 10px; color: #A9A9A9; vertical-align: middle;"></i>
        </a>
        <a href="https://twitter.com/cz_antoine" target="_blank" style="margin: 0; padding: 0; display: inline-block;">
            <i class="fab fa-twitter" style="font-size: 30px; margin: 0 10px; color: #A9A9A9; vertical-align: middle;"></i>
        </a>
        <a href="https://github.com/czantoine" target="_blank" style="margin: 0; padding: 0; display: inline-block;">
            <i class="fab fa-github" style="font-size: 30px; margin: 0 10px; color: #A9A9A9; vertical-align: middle;"></i>
        </a>
    </div>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)
