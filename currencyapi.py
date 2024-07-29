from utilities.utils import round_up_to_thousands
from db.dbconn import conn, cur
from config import (
    THREE_M_USD_PRICE,
    NINE_M_USD_PRICE,
    TWELVE_M_USD_PRICE,
    FEE_AMOUNT,
    PROFIT_AMOUNT,
)
import requests

import sys


# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, 'D:\Telegram bots\Premium Bot')


response = requests.get("https://api.wallex.ir/v1/markets")
data = response.json()
last_price = data["result"]["symbols"]["USDTTMN"]["stats"]["lastPrice"]


services_data = [
    ("three_m", float(THREE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
    ("nine_m", float(NINE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
    ("twelve_m", float(TWELVE_M_USD_PRICE),
     float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
]


def check_rows_count():
    cur.execute("SELECT COUNT(*) FROM services")
    count = cur.fetchone()[0]
    return count


def insert_data_if_empty():
    count = check_rows_count()
    if count == 0:
        insert_data()
    else:
        print("Table 'services' is not empty. Skipping insertion.")


def insert_data():
    for service_name, price, fee, profit in services_data:
        cur.execute(
            """
            INSERT INTO services (service_name, price, fee, profit) VALUES (?, ?, ?, ?)
            """,
            (service_name, price, fee, profit),
        )
        conn.commit()


# 'conn' and 'cur' are already defined elsewhere and connected to database

# Usage:
insert_data_if_empty()


if __name__ == "__main__":
    main()

cur.execute(
    """SELECT service_name, price, fee, profit
    FROM services
    WHERE service_name IN ('three_m', 'nine_m', 'twelve_m');"""
)
data = cur.fetchall()

fee_amount = round_up_to_thousands(int(FEE_AMOUNT) * float(last_price))
profit_amount = round_up_to_thousands(int(PROFIT_AMOUNT) * float(last_price))
# Assign values to the respective variables
for service in data:
    service_name, price, fee, profit = service
    if service_name == "three_m":
        three_m_price = round_up_to_thousands(price * float(last_price))
        # fee_amount = round_up_to_thousands(fee * float(last_price))
        # profit_amount = round_up_to_thousands(profit * float(last_price))
    elif service_name == "nine_m":
        six_m_price = round_up_to_thousands(price * float(last_price))
        # fee_amount = round_up_to_thousands(fee * float(last_price))
        # profit_amount = round_up_to_thousands(profit * float(last_price))
    elif service_name == "twelve_m":
        twelve_m_price = round_up_to_thousands(price * float(last_price))
        # fee_amount = round_up_to_thousands(fee * float(last_price))
        # profit_amount = round_up_to_thousands(profit * float(last_price))
