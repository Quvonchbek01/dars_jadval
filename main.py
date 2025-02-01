from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import os
from aiohttp import web

TOKEN = '7743651084:AAG1yZesza5dkkipyhg9Iw6nJeLkBCrxcYc'
WEBHOOK_URL = "https://dars_jadval/webhook"  # O'zingizning server URL

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def on_start(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="📅 Web App'ni ochish",
            web_app=types.WebAppInfo(url="https://imjadval.netlify.app")
        )
    )
    await message.answer("📢 Web App'ni ochish uchun tugmani bosing:", reply_markup=keyboard)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await on_start(message)

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
    loop.create_task(set_webhook())
    loop.run_in_executor(None, start_server)
    executor.start_polling(dp, skip_updates=True)
