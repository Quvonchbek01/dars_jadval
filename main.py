from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException

API_TOKEN = "revoked"
CHANNEL_ID = "-1002464209662"
SCHEDULE_MESSAGE_IDS = {
    "5-A": {
        "Dushanba" : 3,
        "Seshanba" : 4,
        "Chorshanba" : 5,
        "Payshanba" : 6,
        "Juma": 7,
    },
    "5-B": {
        "Dushanba": 9,
        "Seshanba": 10,
        "Chorshanba": 11, 
        "Payshanba": 12,
        "Juma": 13,  
    },
    "5-D": {
        "Dushanba": 16,
        "Seshanba": 17,
        "Chorshanba": 18,
        "Payshanba": 19,
        "Juma": 20,
    },
    "6-A": {
        "Dushanba": 22,
        "Seshanba": 23,
        "Chorshanba": 24,
        "Payshanba": 25,
        "Juma": 26,
    },
    "6-B": {
        "Dushanba": 28,
        "Seshanba": 29,
        "Chorshanba": 30,
        "Payshanba": 31,
        "Juma": 32,
    },
     "6-D": {
        "Dushanba": 34,
        "Seshanba": 35,
        "Chorshanba": 36,
        "Payshanba": 37,
        "Juma": 38,
    },
    "7-A": {
        "Dushanba": 40,
        "Seshanba": 41,
        "Chorshanba": 42,
        "Payshanba": 43,
        "Juma": 44,
    },
    "7-B": {
        "Dushanba": 46,
        "Seshanba": 47,
        "Chorshanba": 48,
        "Payshanba": 49,
        "Juma": 50,
    },
    "7-D": {
        "Dushanba": 52,
        "Seshanba": 53,
        "Chorshanba": 54,
        "Payshanba": 55,
        "Juma": 56,
    },
    "8-A": {
        "Dushanba": 58,
        "Seshanba": 59,
        "Chorshanba": 60,
        "Payshanba": 61,
        "Juma": 62,
    },
    "8-B": {
        "Dushanba": 64,
        "Seshanba": 65,
        "Chorshanba": 66,
        "Payshanba": 67,
        "Juma": 68,
    },
     "8-D": {
        "Dushanba": 70,
        "Seshanba": 71,
        "Chorshanba": 72,
        "Payshanba": 73,
        "Juma": 74,
    },
    "9-A": {
        "Dushanba": 76,
        "Seshanba": 77,
        "Chorshanba": 78,
        "Payshanba": 79,
        "Juma": 80,
    },
    "9-B": {
        "Dushanba": 82,
        "Seshanba": 83,
        "Chorshanba": 84,
        "Payshanba": 85,
        "Juma": 86,
    },
     "9-D": {
        "Dushanba": 88,
        "Seshanba": 89,
        "Chorshanba": 90,
        "Payshanba": 91,
        "Juma": 92,
    },
    "10-A": {
        "Dushanba": 94,
        "Seshanba": 95,
        "Chorshanba": 96,
        "Payshanba": 97,
        "Juma": 98,
    },
    "10-B": {
        "Dushanba": 100,
        "Seshanba": 101,
        "Chorshanba": 102,
        "Payshanba": 103,
        "Juma": 104,
    },
    "10-D": {
        "Dushanba": 106,
        "Seshanba": 107,
        "Chorshanba": 108
        "Payshanba": 19,
        "Juma": 110,
    },
    "11-A": {
        "Dushanba": 113,
        "Seshanba": 114,
        "Chorshanba": 115,
        "Payshanba": 116,
        "Juma": 117
    },
    "11-B": {
        "Dushanba": 119,
        "Seshanba": 120,
        "Chorshanba": 121,
        "Payshanba": 122,
        "Juma": 123,
    },
     "11-D": {
        "Dushanba": 125,
        "Seshanba": 126,
        "Chorshanba": 127,
        "Payshanba": 128,
        "Juma": 129,
    },
}

bot = TeleBot(API_TOKEN)

@bot.message_handler(commands=["start", "jadval"])
def start(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Sinf guruhlarini ajratish
    group_1 = ["5-A", "5-B", "5-D"]
    group_2 = ["6-A", "6-B", "6-D"]
    group_3 = ["7-A", "7-B", "7-D"]
    group_4 = ["8-A", "8-B", "8-D"]
    group_5 =  ["9-A", "9-B","9-D"]
    group_6 = ["10-A", "10-B", "10-D"]
    group_7 = ["11-A", "11-B", "11-D"]
    
    # Guruhlar uchun tugmalar qo'shish
    for group in [group_1, group_2, group_3, group_4, group_5, group_6, group_7]:
        row = [InlineKeyboardButton(sinf, callback_data=sinf) for sinf in group]
        keyboard.row(*row)
    
    bot.send_message(
        message.chat.id,
        "Assalomu alaykum, qaysi sinfning dars jadvalini ko‘rmoqchisiz?",
        reply_markup=keyboard,
    )

@bot.callback_query_handler(func=lambda call: call.data in SCHEDULE_MESSAGE_IDS)
def send_schedule(call):
    sinf = call.data
    keyboard = InlineKeyboardMarkup(row_width=2)
    for kun in SCHEDULE_MESSAGE_IDS[sinf].keys():
        keyboard.add(InlineKeyboardButton(kun, callback_data=f"{sinf}:{kun}"))
    bot.edit_message_text(
        f"{sinf} sinf tanlandi, endi hafta kunini tanlang !",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=keyboard,
    )

@bot.callback_query_handler(func=lambda call: ":" in call.data)
def send_day_schedule(call):
    sinf, kun = call.data.split(":")
    if sinf in SCHEDULE_MESSAGE_IDS and kun in SCHEDULE_MESSAGE_IDS[sinf]:
        try:
            message_id = SCHEDULE_MESSAGE_IDS[sinf][kun]
            bot.forward_message(
                chat_id=call.message.chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=message_id,
            )
        except ApiTelegramException as e:
            bot.send_message(call.message.chat.id, "Xatolik yuz berdi!")
    else:
        bot.send_message(call.message.chat.id, "Noto'g'ri sinf yoki kun tanlandi.")

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)