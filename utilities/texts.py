from currencyapi import (
    three_m_price,
    six_m_price,
    twelve_m_price,
)

WELCOME_TEXT = "خوش آمدید"
START_TEXT = "start"
BUY_PREMIUM_TEXT = "🛍️ خرید پرمیوم تلگرام"
BUY_FOR_SELF_TEXT = "🙋‍♂️ خرید برای خودم"
BUY_FOR_FRIENDS_TEXT = "🙋‍♂️🙋‍♂️🙋‍♂️ خرید برای دوستان"
BUY_SUCCESS_TEXT = "✅ خرید با موفقیت انجام شد"
LOREM = "لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ، و با استفاده از طراحان گرافیک است، چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است، و برای شرایط فعلی تکنولوژی مورد نیاز، و کاربردهای متنوع با هدف بهبود ابزارهای کاربردی می باشد، کتابهای زیادی در شصت و سه درصد گذشته حال و آینده، شناخت فراوان جامعه و متخصصان را می طلبد، تا با نرم افزارها شناخت بیشتری را برای طراحان رایانه ای علی الخصوص طراحان خلاقی، و فرهنگ پیشرو در زبان فارسی ایجاد کرد، در این صورت می توان امید داشت که تمام و دشواری موجود در ارائه راهکارها، و شرایط سخت تایپ به پایان رسد و زمان مورد نیاز شامل حروفچینی دستاوردهای اصلی، و جوابگوی سوالات پیوسته اهل دنیای موجود طراحی اساسا مورد استفاده قرار گیرد."
FAQ_FULL_TEXT = [
    ("❓ تلگرام پرمیوم چیست؟", "تلگرام پرمیوم یک سرویس اشتراکی است که امکانات بیشتری را نسبت به نسخه رایگان تلگرام ارائه می‌دهد. این امکانات شامل امکانات اضافی، سفارشی‌سازی بیشتر، فضای ذخیره‌سازی بزرگتر و عدم نمایش تبلیغات می‌شود."),
    ("❓ چرا باید تلگرام پرمیوم را بخرم؟", "با خرید تلگرام پرمیوم، شما می‌توانید از امکانات ویژه‌ای مانند ارسال فایل‌های بزرگتر، سرعت دانلود بالاتر، استیکرهای انحصاری، و گزینه‌های سفارشی‌سازی بیشتر بهره‌مند شوید. این امکانات تجربه کاربری شما را بهبود می‌بخشند."),
    ("❓ چگونه می‌توانم اشتراک تلگرام پرمیوم را بخرم؟", "برای خرید اشتراک تلگرام پرمیوم، کافی است با بات ما ارتباط برقرار کنید و مراحل ساده‌ای را دنبال کنید. بات شما را راهنمایی می‌کند تا اشتراک خود را انتخاب و پرداخت را انجام دهید."),
    ("❓ اگر به مشکلی برخوردم چه کاری باید انجام دهم؟", "در صورت بروز هرگونه مشکل، شما می‌توانید از طریق بات یا حساب پشتیبانی با تیم ما در ارتباط باشید بگیرید. تیم پشتیبانی ما به صورت ۲۴/۷ آماده کمک به شماست."),
    ("❓ آیا می‌توانم اشتراک تلگرام پرمیوم را به شخص دیگری هدیه دهم؟", "بله، شما می‌توانید اشتراک تلگرام پرمیوم را به عنوان هدیه به دوستان یا خانواده خود ارائه دهید. برای این کار کافی است در قسمت خرید اشتراک یوز نیم شخص مورد نظر را وارد کنید."),
    ("❓ آیا اشتراک تلگرام پرمیوم در تمام دستگاه‌ها قابل استفاده است؟", "بله، با خرید اشتراک تلگرام پرمیوم، می‌توانید از امکانات آن در تمام دستگاه‌هایی که تلگرام بر روی آن‌ها نصب شده است، استفاده کنید."),
]
FAQ_TEXT = "❓ پرسش‌ های متداول (FAQ)"
MY_PURCHASES_TEXT = "❇️ درخواست های من"
GO_BACK_TEXT = "🔙 بازگشت"
THREE_M_SUB_TEXT = "تلگرام پرمیوم سه ماهه"
SIX_M_SUB_TEXT = "تلگرام پرمیوم شش ماهه"
TWELVE_M_SUB_TEXT = "تلگرام پرمیوم دوازده ماهه"
PENDING_APPROVAL_TEXT = "🕰 در انتظار تایید"
REVIEWING_TEXT = "⌛ در حال بررسی"
APPROVED_TEXT = "✅ تایید شده"
CANCELLED_TEXT = "🚫  لغو شده"
CHOOSE_USERNAME_ERROR_TEXT = "⚠️ لطفاً برای حساب خود یوزرنیم انتخاب کنید"
SUB_HELP_TEXT = """⭐️ لطفا نام کاربری مورد نظر برای خرید پرمیوم ارسال کنید"""
CHOOSE_OPTION_TEXT = "⭐️ لطفا نوع اشتراک تلگرام پریموم خود را انتخاب کنید"
INVALID_OPTION_TEXT = "❗️ گزینه نامعتبر لطفا دوباره تلاش کنید."
FAILED_UPDATE_STATUS_TEXT = "❗️ وضعیت به‌روزرسانی نشد."
ERROR_SENDING_PHOTO = "❗️ هنگام ارسال عکس برای ادمین خطایی رخ داد."
UNKNOWN_TEXT = "نامشخص"
NO_SUB_TEXT = "🚫 شما اشتراکی ندارید."
USERNAME_LIMITS_TEXT = "⚠️ لطفا یوزر نیم را به درستی وارد کنید. یک یوزر نیم درست شامل : حروف انگلیسی A تا Z ، اعداد 0 تا 9 ، آندرسکور( _ )، و ۵ تا ۳۲ حرف است"
STATUS_UPDATED_TEXT = "وضعیت تغییر کرد به : "
ITS_PAID_TEXT = "✅ مشتری گرامی تراکنش شما تایید شد"
ADMIN_PANEL_TEXT = "👤  ادمین"
USERS_STATS = "📊 آمار کاربران"
PHOTO_SENT_SUCCESSFULLY = "✅ عکس واریزی شما با موفقیت برای ادمین ما ارسال شد"


def cancelled_username_text(sub_name):
    text = f"""
🔴 درخواست شما لغو شد
درخواست : {sub_name}
به دلیل اشتباه بودن نام کاربری یا دلیلی دیگر لفو شد
اگر فکر میکنی که اشتباه شده میتونی با ادمین ما در ارتباط باشی 👇

⚠️ مشتری گرامی هر وقت که خواستی میتونی با کلیک کردن روی 
"{MY_PURCHASES_TEXT} "

وضعیت درخواست های خودت رو ببینی
"""
    return text


def cancelled_payment_text(sub_name):
    text = f"""
🔴 درخواست شما لغو شد
درخواست :{sub_name}
به دلیل اشتباه بودن تراکنش شما لفو شد
اگر فکر میکنی که اشتباه شده میتونی با ادمین ما در ارتباط باشی 👇

⚠️ مشتری گرامی هر وقت که خواستی میتونی با کلیک کردن روی 
"{MY_PURCHASES_TEXT} "

وضعیت درخواست های خودت رو ببینی
    """
    return text


def approved_payment(sub_name):
    text = f"""
✅ تراکنش شما تایید شد
درخواست :{sub_name}
تراکنیش شما با موفقیت تایید شد و درخواست شما به زودی برای شما فعال خواهد شد

 ⚠️ مشتری گرامی هر وقت که خواستی میتونی با کلیک کردن روی 
"{MY_PURCHASES_TEXT} "

وضعیت درخواست های خودت رو ببینی
"""
    return text


def approved(sub_name):
    text = f"""
✅ درخواست شما تایید شد
درخواست :{sub_name}
درخواست شما با موفقیت تایید شد و تلگرام پرمیوم شما برای شما فعال شد

⚠️ مشتری گرامی هر وقت که خواستی میتونی با کلیک کردن روی 
{MY_PURCHASES_TEXT} "

وضعیت درخواست های خودت رو ببینی
    """
    return text
