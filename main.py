import os
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update
from aiogram.filters import Command, CallbackData  # ✅ CallbackData ni to‘g‘ri joyidan import qildik
from aiohttp import web
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Muhit o'zgaruvchilari (Token va Webhook URL)
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Render tomonidan ajratilgan portni olish (agar yo‘q bo‘lsa, 10000 ni ishlatish)
PORT = int(os.getenv("PORT", 10000))

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)

# ✅ CallbackData obyektini to‘g‘ri joydan import qildik
class WebCallback(CallbackData, prefix="web"):
    action: str

# /start komandasiga javob
@router.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🌍 Web", callback_data=WebCallback(action="open_web").pack())
    ]])
    await message.answer("Assalomu alaykum. Dars jadvalini Web app orqali ko'rishingiz mumkin. Web appga kirish uchun pastdagi tugmani bosing yoki /web xabarini yuboring", reply_markup=keyboard)

# Callbackni tutib olish
@router.callback_query(WebCallback.filter())
async def web_callback_handler(callback: types.CallbackQuery, callback_data: WebCallback):
    if callback_data.action == "open_web":
        await callback.message.answer("/web")  # Bot avtomatik `/web` komandasi yuboradi
        await callback.answer()  # Tugmachani bosgandan keyin yuklash animatsiyasini yopish

# /web komandasiga javob
@router.message(Command("web"))
async def web1(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="📅 Web App'ni ochish",
            web_app=WebAppInfo(url="https://imjadval.netlify.app")
        )
    ]])
    await message.answer("📢 Web App'ni ochish uchun tugmani bosing:", reply_markup=keyboard)

# Webhook orqali kelgan so‘rovlarni qabul qilish (POST)
async def on_webhook(request):
    json_str = await request.json()
    update = Update.model_validate(json_str)
    await dp.feed_update(bot, update)
    return web.Response(text="✅ Update qabul qilindi!", status=200)

# GET so‘rovlarga javob berish (UptimeRobot uchun)
async def on_ping(request):
    return web.Response(text="✅ Bot ishlayapti!", status=200)

# Webhookni sozlash
async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook o‘rnatildi: {WEBHOOK_URL}")

# Webhook serverni ishga tushirish
async def start_webhook():
    await set_webhook()  # Webhookni sozlash

    app = web.Application()
    app.router.add_post('/webhook', on_webhook)  # Telegram uchun
    app.router.add_get('/', on_ping)  # UptimeRobot uchun

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    
    print(f"🚀 Server {PORT} portda ishlayapti...")

    # Bot sessiyasini yopish (Unclosed connector muammosini hal qilish)
    try:
        await asyncio.Event().wait()  # Serverni cheksiz ishlashga majbur qilish
    finally:
        await bot.session.close()
        print("🔴 Bot sessiyasi yopildi!")

# Webhook serverni ishga tushirish
if __name__ == "__main__":
    asyncio.run(start_webhook())
