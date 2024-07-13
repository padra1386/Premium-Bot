import os
from dotenv import load_dotenv

load_dotenv(override=True)

TOKEN = os.getenv("token")
DB_HOST = os.getenv("db_host")
DB_NAME = os.getenv("db_name")
DB_USER = os.getenv("db_user")
DB_PASSWORD = os.getenv("db_password")
DB_PORT = os.getenv("db_port")
ADMIN_CHAT_ID = os.getenv("admin_chat_id")
THREE_M_USD_PRICE = os.getenv("three_m_usd_price")
NINE_M_USD_PRICE = os.getenv("nine_m_usd_price")
TWELVE_M_USD_PRICE = os.getenv("twelve_m_usd_price")
FEE_AMOUNT = os.getenv("fee_amount")
PROFIT_AMOUNT = os.getenv("profit_amount")
