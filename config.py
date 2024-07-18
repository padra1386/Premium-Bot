import os
from dotenv import load_dotenv

load_dotenv(override=True)

TOKEN = os.getenv("TOKEN")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_PORT = os.getenv("POSTGRES_PORT")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
THREE_M_USD_PRICE = os.getenv("THREE_M_USD_PRICE")
NINE_M_USD_PRICE = os.getenv("NINE_M_USD_PRICE")
TWELVE_M_USD_PRICE = os.getenv("TWELVE_M_USD_PRICE")
FEE_AMOUNT = os.getenv("FEE_AMOUNT")
PROFIT_AMOUNT = os.getenv("PROFIT_AMOUNT")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
CHANELL_ID = os.getenv("CHANELL_ID")
WEBSITE_ADDRESS = os.getenv("WEBSITE_ADDRESS")
