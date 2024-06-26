import requests


def get_exchange_rate(api_key):
    url = f"http://api.navasan.tech/latest/?api_key={api_key}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        # Assuming 'usd' is the key for USD to IRR exchange rate in the returned JSON
        rates = data.get("usd")
        if rates:
            return rates.get("value")  # Adjust based on actual JSON structure
        else:
            print("USD to IRR rate not found in response.")
            return None
    else:
        print("Error fetching exchange rate:", data.get("message"))
        return None


def convert_currency(amount, exchange_rate):
    return amount * exchange_rate


# Replace 'شما-API-کلید' with your actual API key
api_key = "freePIdlIEBACw1nXIOpeLK9Px1ldjW7"
amount = 1  # Amount in USD to convert

exchange_rate = get_exchange_rate(api_key)
if exchange_rate:
    amount_in_irr = convert_currency(amount, exchange_rate)
    print(f"{amount} USD is equal to {amount_in_irr} IRR")
else:
    print("Failed to retrieve exchange rate.")
