import requests
from config.config import (
    THREE_M_USD_PRICE,
    NINE_M_USD_PRICE,
    TWELVE_M_USD_PRICE,
    FEE_AMOUNT,
    PROFIT_AMOUNT,
)
from db.dbconn import conn, cur
from utilities.utils import round_up_to_thousands

response = requests.get("https://api.wallex.ir/v1/markets")
data = response.json()
last_price = data["result"]["symbols"]["USDTTMN"]["stats"]["lastPrice"]


services_data = [
    ("three_m", float(THREE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
    ("nine_m", float(NINE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
    ("twelve_m", float(TWELVE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
]


def insert_data():
    for service_name, price, fee, profit in services_data:
        cur.execute(
            """
                INSERT INTO services (service_name, price, fee, profit) VALUES (%s, %s, %s, %s)
            """,
            (service_name, price, fee, profit),
        )

        conn.commit()


def main():
    insert_data()


if __name__ == "__main__":
    main()

cur.execute(
    """SELECT service_name, price, fee, profit
    FROM services
    WHERE service_name IN ('three_m', 'nine_m', 'twelve_m');"""
)
data = cur.fetchall()
three_m_price = three_m_fee = three_m_profit = None
six_m_price = six_m_fee = six_m_profit = None
twelve_m_price = twelve_m_fee = twelve_m_profit = None

# Assign values to the respective variables
for service in data:
    service_name, price, fee, profit = service
    if service_name == "three_m":
        three_m_price = round_up_to_thousands(price * float(last_price))
        three_m_fee = fee * float(last_price)
        three_m_profit = profit * float(last_price)
    elif service_name == "nine_m":
        six_m_price = round_up_to_thousands(price * float(last_price))
        six_m_fee = fee * float(last_price)
        six_m_profit = profit * float(last_price)
    elif service_name == "twelve_m":
        twelve_m_price = round_up_to_thousands(price * float(last_price))
        twelve_m_fee = fee * float(last_price)
        twelve_m_profit = profit * float(last_price)
