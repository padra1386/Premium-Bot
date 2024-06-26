import requests

response = requests.get("https://api.wallex.ir/v1/markets")
data = response.json()

usdt_tmn = data["result"]["symbols"]["USDTTMN"]
last_price = usdt_tmn["stats"]["lastPrice"]

buy_self_text = f"قیمت فعلی تتر به تومان: {last_price} تومان"
