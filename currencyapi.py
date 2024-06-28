import requests

response = requests.get("https://api.wallex.ir/v1/markets")
data = response.json()

usdt_tmn = data["result"]["symbols"]["USDTTMN"]
last_price = usdt_tmn["stats"]["lastPrice"]
formatted_price = str(last_price).rstrip("0").rstrip(".")

buy_self_text = f"قیمت فعلی تتر به تومان: {formatted_price} تومان"
