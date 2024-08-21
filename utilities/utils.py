import re
import math
# Assuming your dbconn is correctly configured for SQLite
from db.dbconn import conn, cur
from convertdate import persian
from telegram import ReplyKeyboardRemove
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import calendar
import jdatetime


def push_menu(context, menu_function):
    if "menu_stack" not in context.user_data:
        context.user_data["menu_stack"] = []
    context.user_data["menu_stack"].append(menu_function)


async def go_back(update, context):
    if "menu_stack" in context.user_data and context.user_data["menu_stack"]:
        menu_function = context.user_data["menu_stack"].pop()
        await menu_function(update, context)
    else:
        await start(update, context)


def is_valid_username(text):
    pattern = r"^[A-Za-z0-9_@]{5,32}$"

    if re.match(pattern, text):
        return True
    else:
        return False


def round_up_to_thousands(number):
    # Divide the number by 1000, round up using math.ceil, then multiply back by 1000
    rounded_number = math.ceil(number / 1000) * 1000
    return rounded_number


def format_with_commas(number):
    # Format the number with commas
    return f"{number:,}"


def get_users():
    cur.execute("SELECT id, username, status FROM users")
    users = cur.fetchall()
    return users


def toggle_user_status(user_id):
    # Retrieve the current status
    cur.execute("SELECT status FROM users WHERE id = ?", (user_id,))
    current_status = cur.fetchone()[0]

    # Toggle the status
    new_status = "inactive" if current_status == "active" else "active"
    cur.execute("UPDATE users SET status = ? WHERE id = ?",
                (new_status, user_id))

    conn.commit()


def gregorian_to_solar(gregorian_date):
    # Extract the date components
    year = gregorian_date.year
    month = gregorian_date.month
    day = gregorian_date.day

    # Convert to Solar Hijri date
    solar_date = persian.from_gregorian(year, month, day)

    # Format the date as a string
    solar_date_str = f"{solar_date[0]:04d}-{solar_date[1]:02d}-{solar_date[2]:02d}"

    return solar_date_str


def solar_to_gregorian(solar_year, solar_month, solar_day):
    return persian.to_gregorian(solar_year, solar_month, solar_day)


def send_reply(context: ContextTypes.DEFAULT_TYPE, chat_id, reply_text):
    reply_keyboard_remove = ReplyKeyboardRemove()
    markup = reply_keyboard_remove
    context.bot.send_message(chat_id, reply_text, markup)


# Function to get the total number of users
def get_total_users():
    cur.execute('SELECT COUNT(*) FROM users')
    return cur.fetchone()[0]


# Function to get the number of new users today
def get_daily_new_users():
    cur.execute('''
    SELECT COUNT(*)
    FROM users
    WHERE DATE(created) = DATE('now', 'localtime')
    ''')
    return cur.fetchone()[0]


# Function to get the number of new users this week
def get_weekly_new_users():
    cur.execute('''
    SELECT COUNT(*)
    FROM users
    WHERE DATE(created) >= DATE('now', '-7 days', 'localtime')
    ''')
    return cur.fetchone()[0]


def get_user_purchased():
    cur.execute("""
    SELECT COUNT(DISTINCT u.id) 
    FROM users u
    JOIN invoice i ON u.id = i.id
    WHERE i.is_paid = 'true';
    """)
    return cur.fetchone()[0]


def sanitize_username(username):
    # Remove '@' if it exists in the username
    return username.replace('@', '')


def get_available_months():
    query = '''
    SELECT DISTINCT 
    strftime('%Y-%m', created) AS year_month
    FROM invoice
    WHERE is_paid = 'true'
    ORDER BY year_month DESC;
    '''
    cur.execute(query)
    results = cur.fetchall()

    # Filter out the current month if it appears
    current_date = datetime.now()
    current_month = current_date.strftime('%Y-%m')

    months = [row[0] for row in results]

    return months


def get_sell_stats(year, month):
    # Convert year and month to the first and last day of the month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])
    # first_day_string = f"{first_day[0]}-{first_day[1]}-{first_day[2]}"
    # last_day_string = f"{last_day[0]}-{last_day[1]}-{last_day[2]}"

    # first_day_dt = datetime(first_day[0], first_day[1], first_day[2])
    # last_day_dt = datetime(last_day[0], last_day[1], last_day[2])

    # first_day_dt = datetime(first_day[0], first_day[1], first_day[2])
    # last_day_dt = datetime(last_day[0], last_day[1], last_day[2])

    # Formatting the datetime objects as strings
    first_day_str = first_day.strftime('%Y-%m-%d 00:00:00')
    last_day_str = last_day.strftime('%Y-%m-%d 23:59:59')

    main_query = '''
    SELECT 
    COUNT(*) AS total_paid_invoices,
    SUM(CAST(price AS DECIMAL)) AS total_price,
    SUM(CAST(profit AS DECIMAL)) AS total_profit,
    SUM(CAST(fee AS DECIMAL)) AS total_fee
    FROM 
    invoice
    WHERE 
    is_paid = 'true'
    AND created >= ?
    AND created <= ?;
    '''
    cur.execute(main_query, (first_day_str, last_day_str))
    result = cur.fetchone()

    return result, first_day, last_day


def format_solar_date(date_str):
    # Split the date string into components
    day, month, year = date_str.split('-')
    # Rearrange into the desired format
    return f"{year}-{month}-{day}"


def generate_inline_keyboard():
    available_months = get_available_months()
    keyboard = []
    for month in available_months:
        year, month_num = map(int, month.split('-'))
        solar_date = gregorian_to_solar(datetime(year, month_num, 1))
        solar_year, solar_month, _ = map(int, solar_date.split('-'))
        solar_month_name = f"ماه {solar_month:02d} {solar_year}"
        keyboard.append([InlineKeyboardButton(
            solar_month_name, callback_data=month)])

    current_solar_date = gregorian_to_solar(datetime.now())
    solar_year, solar_month, _ = map(int, current_solar_date.split('-'))
    current_month_name = f"ماه جاری {solar_year}"
    keyboard.append([InlineKeyboardButton(
        current_month_name, callback_data='current')])

    return InlineKeyboardMarkup(keyboard)


def get_solar_date():
    now = jdatetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')


def extract_number(text):
    """Extracts the first integer from a given text string.

    Args:
      text: The input text string.

    Returns:
      The extracted integer, or None if no integer is found.
    """

    import re

    # Use regular expression to find the first integer in the text
    match = re.search(r'\d+', text)

    if match:
        return int(match.group())
    else:
        return None
