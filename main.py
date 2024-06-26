from telegram import ReplyKeyboardRemove, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from decouple import config
import psycopg2
import datetime
import requests  # Add this line to import the requests library

TOKEN = config("token")

# Define constants for the texts
BUY_PREMIUM_TEXT = "🛍️ خرید پرمیوم تلگرام"
BUY_FOR_SELF_TEXT = "🙋‍♂️ خرید برای خودم"
BUY_FOR_FRIENDS_TEXT = "🙋‍♂️🙋‍♂️🙋‍♂️ خرید برای دوستان"
BUY_SUCCESS = "✅ خرید با موفقیت انجام شد"
LOREM = "لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ، و با استفاده از طراحان گرافیک است، چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است، و برای شرایط فعلی تکنولوژی مورد نیاز، و کاربردهای متنوع با هدف بهبود ابزارهای کاربردی می باشد، کتابهای زیادی در شصت و سه درصد گذشته حال و آینده، شناخت فراوان جامعه و متخصصان را می طلبد، تا با نرم افزارها شناخت بیشتری را برای طراحان رایانه ای علی الخصوص طراحان خلاقی، و فرهنگ پیشرو در زبان فارسی ایجاد کرد، در این صورت می توان امید داشت که تمام و دشواری موجود در ارائه راهکارها، و شرایط سخت تایپ به پایان رسد و زمان مورد نیاز شامل حروفچینی دستاوردهای اصلی، و جوابگوی سوالات پیوسته اهل دنیای موجود طراحی اساسا مورد استفاده قرار گیرد."
FAQ_TEXT = "❓ سوالات پر تکرار"
MY_PURCHASES_TEXT = "❇️ درخواست های من"
GO_BACK_TEXT = "🔙 بازگشت"

# Connect To The DataBase
conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="ra6656634ra",
    port="5432",
)

cur = conn.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS users (
        id TEXT,
        username VARCHAR(255),
        sub VARCHAR(255),
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
)

conn.commit()


# Helper function to push the current menu to the stack
def push_menu(context: ContextTypes.DEFAULT_TYPE, menu_function):
    if "menu_stack" not in context.user_data:
        context.user_data["menu_stack"] = []
    context.user_data["menu_stack"].append(menu_function)


# Helper function to pop the previous menu from the stack and call it
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "menu_stack" in context.user_data and context.user_data["menu_stack"]:
        menu_function = context.user_data["menu_stack"].pop()
        await menu_function(update, context)
    else:
        await start(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, start)
    start_keys = [
        [
            KeyboardButton(text=BUY_PREMIUM_TEXT),
            KeyboardButton(text=MY_PURCHASES_TEXT),
        ],
        [
            KeyboardButton(text=FAQ_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(start_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="This is a test", reply_markup=markup
    )


async def buy_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, start)

    buy_keys = [
        [
            KeyboardButton(text=BUY_FOR_SELF_TEXT),
        ],
        [
            KeyboardButton(text=BUY_FOR_FRIENDS_TEXT),
        ],
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(buy_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="انتخاب کنید :", reply_markup=markup
    )


async def buy_for_self(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, buy_sub)

    # Fetch the latest price from the API
    response = requests.get("https://api.wallex.ir/v1/markets")
    data = response.json()

    # Extract the USDTTMN symbol data
    usdt_tmn = data["result"]["symbols"]["USDTTMN"]
    last_price = usdt_tmn["stats"]["lastPrice"]

    buy_self_text = f"قیمت فعلی تتر به تومان: {last_price} تومان"

    buy_self_keys = [
        [
            KeyboardButton(text=buy_self_text),
        ],
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(buy_self_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="انتخاب کنید :", reply_markup=markup
    )


async def buy_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text

    user_data = update.message.from_user
    user_id = user_data["id"]
    user_username = user_data["username"]
    user_sub = (
        text  # Assuming the text contains the subscription type selected by the user
    )

    if user_username:
        cur.execute(
            "INSERT INTO users (id, username, sub) VALUES (%s, %s, %s)",
            (user_id, user_username, user_sub),
        )
        conn.commit()
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفا برای حساب خود یوزرنیم انتخاب کنید",
        )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=BUY_SUCCESS)


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, start)

    faq_keys = [
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(faq_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=LOREM, reply_markup=markup
    )


async def my_subs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, start)

    user_data = update.message.from_user
    user_id = user_data["id"]

    cur.execute(
        "SELECT username, sub, created FROM users WHERE id = %s", (str(user_id),)
    )
    user_data = cur.fetchall()

    if user_data:
        subs_list = "\n".join(
            [
                f"- @{username}: {sub} Premium (Created on: {created.strftime('%Y-%m-%d %H:%M:%S')})"
                for username, sub, created in user_data
            ]
        )
        response_message = f"اشتراک‌های شما:\n{subs_list}"
    else:
        response_message = "شما اشتراکی ندارید."

    my_subs_keys = [
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(my_subs_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=response_message, reply_markup=markup
    )


def main():
    app = Application.builder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    buy_sub_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{BUY_PREMIUM_TEXT}$"), buy_sub
    )
    buy_self_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{BUY_FOR_SELF_TEXT}$"), buy_for_self
    )
    buy_success_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{BUY_FOR_SELF_TEXT}.*"), buy_success
    )
    faq_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{FAQ_TEXT}$"),
        faq,
    )
    my_subs_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{MY_PURCHASES_TEXT}$"),
        my_subs,
    )
    go_back_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{GO_BACK_TEXT}$"),
        go_back,
    )

    app.add_handlers(
        [
            start_handler,
            buy_sub_handler,
            buy_self_handler,
            buy_success_handler,
            faq_handler,
            my_subs_handler,
            go_back_handler,
        ]
    )

    app.run_polling()


if __name__ == "__main__":
    main()

    cur.close()
    conn.close()
