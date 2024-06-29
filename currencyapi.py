import requests

response = requests.get("https://api.wallex.ir/v1/markets")
data = response.json()

usdt_tmn = data["result"]["symbols"]["USDTTMN"]
last_price = usdt_tmn["stats"]["lastPrice"]
formatted_price = str(last_price).rstrip("0").rstrip(".")

three_month_price = float(formatted_price) * 12.99
six_month_price = float(formatted_price) * 16.99
twelve_month_price = float(formatted_price) * 129.99
