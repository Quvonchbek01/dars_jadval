import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Bot Token va Webhook URL ni .env faylidan olish
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# /start komandasiga javob
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="📅 Web App'ni ochish",
            web_app=types.WebAppInfo(url="https://imjadval.netlify.app")
        )
    )
    await message.answer("📢 Web App'ni ochish uchun tugmani bosing:", reply_markup=keyboard)

# Webhook orqali kelgan so‘rovlarni qabul qilish
async def on_webhook(request):
    json_str = await request.json()
    update = types.Update(**json_str)
    await dp.process_update(update)
    return web.Response()

# Webhookni sozlash
async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)

# Webhook serverni ishga tushirish
async def start_webhook():
    await set_webhook()  # Webhookni sozlash

    app = web.Application()
    app.router.add_post('/webhook', on_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=5000)
    await site.start()

# Webhook serverni ishga tushirish
if __name__ == "__main__":
    import asyncio
    asyncio.run(start_webhook())
