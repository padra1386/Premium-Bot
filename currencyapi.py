from utilities.utils import round_up_to_thousands
from db.dbconn import conn, cur
from config import (
    THREE_M_USD_PRICE,
    NINE_M_USD_PRICE,
    TWELVE_M_USD_PRICE,
    FEE_AMOUNT,
    PROFIT_AMOUNT,
    FIFTY_STARS_PRICE,
    SEVENTY_FIVE_STARS_PRICE,
    HUNDRED_STARS_PRICE,
    STARS_PROFIT,
    STARS_FEE
)
import requests

import sys


# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, 'D:\Telegram bots\Premium Bot')


response = requests.get("https://api.wallex.ir/v1/markets")
data = response.json()
last_price = data["result"]["symbols"]["USDTTMN"]["stats"]["lastPrice"]


premium_services_data = [
    ("three_m", float(THREE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
    ("nine_m", float(NINE_M_USD_PRICE), float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
    ("twelve_m", float(TWELVE_M_USD_PRICE),
     float(FEE_AMOUNT), float(PROFIT_AMOUNT)),
]

stars_services_data = [
    ("50", float(FIFTY_STARS_PRICE), float(STARS_FEE), float(STARS_PROFIT)),
    ("75", float(SEVENTY_FIVE_STARS_PRICE), float(STARS_FEE), float(STARS_PROFIT)),
    ("100", float(HUNDRED_STARS_PRICE),
     float(STARS_FEE), float(STARS_PROFIT)),
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
    for service_name, price, fee, profit in premium_services_data:
        cur.execute(
            """
            INSERT INTO services (service_name, price, fee, profit) VALUES (?, ?, ?, ?)
            """,
            (service_name, price, fee, profit),
        )
        conn.commit()


def stars_check_rows_count():
    cur.execute("SELECT COUNT(*) FROM stars_services")
    count = cur.fetchone()[0]
    return count


def stars_insert_data_if_empty():
    count = stars_check_rows_count()
    if count == 0:
        stars_insert_data()
    else:
        print("Table 'stars_services' is not empty. Skipping insertion.")


def stars_insert_data():
    for service_name, price, fee, profit in stars_services_data:
        cur.execute(
            """
            INSERT INTO stars_services (service_name, price, fee, profit) VALUES (?, ?, ?, ?)
            """,
            (service_name, price, fee, profit),
        )
        conn.commit()


# 'conn' and 'cur' are already defined elsewhere and connected to database

# Usage:
insert_data_if_empty()
stars_insert_data_if_empty()


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


cur.execute(
    """SELECT service_name, price, fee, profit
    FROM stars_services
    WHERE service_name IN ('50', '75', '100');"""
)
stars_data = cur.fetchall()

stars_fee_amount = round_up_to_thousands(float(STARS_FEE) * float(last_price))
stars_profit_amount = round_up_to_thousands(
    float(STARS_PROFIT) * float(last_price))
# Assign values to the respective variables
for service in stars_data:
    service_name, price, fee, profit = service
    if service_name == "50":
        fifty_price = round_up_to_thousands(price * float(last_price))
        # fee_amount = round_up_to_thousands(fee * float(last_price))
        # profit_amount = round_up_to_thousands(profit * float(last_price))
    elif service_name == "75":
        seventy_five_price = round_up_to_thousands(price * float(last_price))
        # fee_amount = round_up_to_thousands(fee * float(last_price))
        # profit_amount = round_up_to_thousands(profit * float(last_price))
    elif service_name == "100":
        hundred_price = round_up_to_thousands(price * float(last_price))
        # fee_amount = round_up_to_thousands(fee * float(last_price))
        # profit_amount = round_up_to_thousands(profit * float(last_price))
