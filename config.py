import os
from dotenv import load_dotenv

load_dotenv(override=True)

TOKEN = os.getenv("token")
SQLITE_DB_PATH = os.getenv("sqlite_db_path")
ADMIN_CHAT_ID = os.getenv("admin_chat_id")
THREE_M_USD_PRICE = os.getenv("three_m_usd_price")
NINE_M_USD_PRICE = os.getenv("nine_m_usd_price")
TWELVE_M_USD_PRICE = os.getenv("twelve_m_usd_price")
FEE_AMOUNT = os.getenv("fee_amount")
PROFIT_AMOUNT = os.getenv("profit_amount")
ADMIN_USERNAME = os.getenv("admin_username")
CHANELL_ID = os.getenv("chanell_id")
WEBSITE_ADDRESS = os.getenv("website_address")
CREDIT_CARD_NUMBER = os.getenv("credit_card_number")
CREDIT_CARD_OWNER = os.getenv("credit_card_owner")
FIFTY_STARS_PRICE = os.getenv("fifty_stars_price")
SEVENTY_FIVE_STARS_PRICE = os.getenv("seventy_five_stars_price")
HUNDRED_STARS_PRICE = os.getenv("hundred_stars_price")
STARS_FEE = os.getenv("stars_fee")
STARS_PROFIT = os.getenv("stars_profit")
