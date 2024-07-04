import requests
from config import (
    THREE_M_USD_PRICE,
    NINE_M_USD_PRICE,
    TWELVE_M_USD_PRICE,
    FEE_AMOUNT,
    PROFIT_AMOUNT,
)
from dbconn import conn, cur

response = requests.get("https://api.wallex.ir/v1/markets")
data = response.json()
last_price = data["result"]["symbols"]["USDTTMN"]["stats"]["lastPrice"]


services_data = [
    ("three_m", float(THREE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
    ("nine_m", float(NINE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
    ("twelve_m", float(TWELVE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
]


def update_data():
    for service_name, price, fee, profit in services_data:
        cur.execute(
            """
                UPDATE services
                SET price = %s, fee = %s, profit = %s
                WHERE service_name = %s
                """,
            (price, fee, profit, service_name),
        )

        conn.commit()


three_month_price = 12
six_month_price = 13
twelve_month_price = 15
