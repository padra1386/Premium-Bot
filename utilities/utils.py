import re
import math
from db.dbconn import conn, cur
from convertdate import persian
from telegram import  ReplyKeyboardRemove
from telegram.ext import  ContextTypes


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
    cur.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))

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
    WHERE DATE(created) = CURRENT_DATE
    ''')
    return cur.fetchone()[0]

# Function to get the number of new users this week
def get_weekly_new_users():
    cur.execute('''
    SELECT COUNT(*)
    FROM users
    WHERE DATE(created) >= CURRENT_DATE - INTERVAL '7 days'
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
