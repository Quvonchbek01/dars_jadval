from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import os
from aiohttp import web
from dotenv import load_dotenv

# .env faylini o'qish
load_dotenv()

# Bot Token va Webhook URL ni .env faylidan o'qish
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Start komandasiga javob
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="📅 Web App'ni ochish",
            web_app=types.WebAppInfo(url="https://imjadval.netlify.app")
        )
    )
    await message.answer("📢 Web App'ni ochish uchun tugmani bosing:", reply_markup=keyboard)

# Webhookni sozlash
async def on_webhook(request):
    json_str = await request.json()
    update = types.Update(**json_str)
    await dp.process_update(update)
    return web.Response()

# Webhookni sozlash
async def set_webhook():
    webhook_url = WEBHOOK_URL
    await bot.set_webhook(webhook_url)

# Serverni ishga tushirish
def start_server():
    app = web.Application()
    app.router.add_post('/webhook', on_webhook)
    web.run_app(app, host='0.0.0.0', port=3001)

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(set_webhook())  # Webhookni sozlash
    loop.run_in_executor(None, start_server)  # Serverni ishga tushirish
    executor.start_polling(dp, skip_updates=True)