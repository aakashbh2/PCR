from flask import Flask, render_template
from datetime import datetime
import requests
import schedule

# Initialize an empty dictionary to store data points
bnf_data = []
nf_data = []
fin_data = []

app = Flask(__name__)

def fetch_and_save_data(symbol, storage):
    # Make an HTTP GET request to the NSE API
    url = f'https://www.nseindia.com/api/option-chain-indices?symbol={symbol}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    try:
        data = response.json()
        option_chain_data = data.get('filtered', {})
        fetched_underlyingValue = data.get('records', {}).get('underlyingValue', 0)

        # Extract relevant data points
        underlying_value = fetched_underlyingValue
        ce_oi = option_chain_data['CE']['totOI']
        pe_oi = option_chain_data['PE']['totOI']
        oi_difference = pe_oi - ce_oi
        pe_ce_ratio = pe_oi / ce_oi
        recommendation = 'BUY' if pe_ce_ratio > 1 else 'SELL'

       # Create a new data point dictionary
        new_data_point = {
            'time': datetime.now().strftime("%I:%M %p"),
            'underlying_value': underlying_value,
            'ce_oi': ce_oi,
            'pe_oi': pe_oi,
            'oi_difference': oi_difference,
            'pe_ce_ratio': pe_ce_ratio,
            'recommendation': recommendation
        }

        # Add the new data point to the historical data (at the beginning)
        storage.insert(0, new_data_point)

        print("Data points saved successfully.", new_data_point)
    except ValueError:
        print("Error fetching data or invalid JSON response.")

# Schedule data fetch every 15 minutes
schedule.every(15).minutes.do(fetch_and_save_data)

@app.route('/')
def index():
     # Call the fetch_and_save_data() function to update data points
    fetch_and_save_data("BANKNIFTY", bnf_data)
    fetch_and_save_data("NIFTY", nf_data)
    fetch_and_save_data("FINNIFTY", fin_data)
    # Render the data in an HTML table
    return render_template('index.html', bnf_data_points=bnf_data, nf_data_points=nf_data, fin_data_points=fin_data)

if __name__ == '__main__':
    app.run(debug=True)
