from enum import Enum
from redis_conn.redis_connection import redis_conn


class BotState(Enum):
    START = "start"
    BUY_PREMIUM = "buy premium"
    MY_SUBS_LIST = "my subs list"
    PREMIUM_SUBS_LIST = "different subs list"
    STARS_SUBS_LIST = "stars subscriptions list"
    FAQ = 'faq page for users'
    INVOICE_LIST = "sending invoice for user"
    ADMIN_PANEL = "admin panel"
    USERS_STATS = 'bot users stats'
    SELL_STATS = 'bot sells stats'
    SELL_VARIABLES = 'bot selling prices'
    ABOUT_US = 'about us page'
    BUY_STARS = "buy stars"
    CUSTOM_AMOUNT = "entering custom amount of stars"


def get_user_state(user_id):
    r = redis_conn
    state = r.get(f"user:{user_id}:state")
    if state is None:
        return BotState.START
    return BotState(state)


def set_user_state(user_id, state):
    r = redis_conn
    r.set(f"user:{user_id}:state", state.value)
