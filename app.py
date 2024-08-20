import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
import urllib3
import altair as alt

# Disable SSL warnings (not recommended for production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
cookies = {
    '_ga': 'GA1.2.540892028.1723112145',
    '_gid': 'GA1.2.2032560936.1723661440',
    'user-country': 'TN',
    '_cfuvid': 'xXUb4iWtsi3_KK1EuBZpq8Rj0.5fHx9B1Y9dYK0LWA8-1723818070216-0.0.1.1-604800000',
    '_ga_5NTCE0KJGV': 'GS1.2.1723890500.19.1.1723890526.34.0.0',
    '_csrf': 'kRWNWftMszSHSmQurHuH3pP9-CQF8Mkb',
}
headers = {
    'Host': 'lotobets365.com',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Accept-Language': 'fr-FR',
    'Sec-Ch-Ua-Mobile': '?0',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MjM4OTA1MTYsImp0aSI6IjVyQytQN1BHb3JwNk9XajlWSUVaOTE4cDhaK05UM1hcL2JzMVhqUUNMdkxJPSIsImlzcyI6InMwMDAxNzUucDItYXBpLXAxMDAuYmlhaG9zdGVkLmNvbSIsIm5iZiI6MTcyMzg5MDUxNiwiZXhwIjoxNzIzODk0MTE2LCJkYXRhIjp7InVzZXJJZCI6MTY1NSwidXNlck5hbWUiOiI1MTQ5NjgwOSJ9fQ.DXibfiAHU6uVS72qvGhReNokWhc_dkX3kci_R40SVskKD57hnkiNBbWVFwmJ5IklWimF2NhCoVYC0Nd271KCLw',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36',
    'Content-Type': 'application/json',
    'User-Country': 'TN',
    'Accept': 'application/json, text/plain, */*',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Origin': 'https://lotobets365.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://lotobets365.com/agent/agent-financial-transactions',
    'Priority': 'u=1, i',
}

@st.cache_data(ttl=300)
def fetch_transactions(date_from, date_to):
    json_data = {
        'userId': 196,
        'dateFrom': date_from,
        'dateTo': date_to
    }
    response = requests.post(
        'https://lotobets365.com/agent-api/transactions/financial',
        cookies=cookies,
        headers=headers,
        json=json_data,
        verify=False,
    )
    return response.json()

def format_transaction(transaction):
    return {
        "Type": transaction["type"],
        "From": transaction["fromUsername"],
        "To": transaction["toUsername"],
        "Amount": float(transaction['amount'])/100,
        "Date & Time": datetime.strptime(transaction["dateTime"], "%Y-%m-%d %H:%M:%S"),
        "Reference ID": transaction["referenceId"]
    }

def calculate_sisou10_totals(transactions):
    total_deposits = sum(t['Amount'] for t in transactions if t['To'] == 'Sisou10')
    total_withdrawals = sum(t['Amount'] for t in transactions if t['From'] == 'Sisou10')
    return total_deposits, total_withdrawals

def main():
    st.set_page_config(page_title="Transaction Monitor", page_icon="💰", layout="wide")
    st.title("🏦 Transaction Monitor")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        date_from = st.date_input("From Date", value=datetime.now().date() - timedelta(days=1))
    with col2:
        date_to = st.date_input("To Date", value=datetime.now().date())

    if st.button("Fetch Transactions"):
        transactions_data = fetch_transactions(date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d"))
        formatted_transactions = [format_transaction(t) for t in transactions_data]
        
        if formatted_transactions:
            df = pd.DataFrame(formatted_transactions)
            
            # Sisou10 Account Statistics
            total_deposits, total_withdrawals = calculate_sisou10_totals(formatted_transactions)
            profit = total_deposits - total_withdrawals
            
            st.subheader("Sisou10 Account Statistics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Deposits", f"{total_deposits:.2f} TND")
            col2.metric("Total Withdrawals", f"{total_withdrawals:.2f} TND")
            col3.metric("Profit", f"{profit:.2f} TND")
            
            # Transactions over time chart
            st.subheader("Transactions Over Time")
            chart = alt.Chart(df).mark_line().encode(
                x='Date & Time:T',
                y='Amount:Q',
                color='Type:N'
            ).properties(
                width=800,
                height=400
            )
            st.altair_chart(chart, use_container_width=True)
            
            # Transactions table
            st.subheader("Transaction Details")
            st.dataframe(df.sort_values("Date & Time", ascending=False), use_container_width=True)
        else:
            st.warning("No transactions found for the selected date range.")

if __name__ == "__main__":
    main()
