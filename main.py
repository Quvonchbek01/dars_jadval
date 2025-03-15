import os
import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update
from aiogram.filters import Command
from aiohttp import web
from dotenv import load_dotenv
from broadcast import router as broadcast_router
from db import save_user

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(broadcast_router)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await save_user(message.from_user.id)
    await message.answer(
        "Assalomu alaykum!\n\n"
        "📅 Dars jadvalini ko‘rish uchun /web tugmasini bosing."
    )

@dp.message(Command("web"))
async def web_app(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="🗓️ Web App'ni ochish",
            web_app=WebAppInfo(url="https://imjadval.netlify.app")
        )
    ]])
    await message.answer("📢 Web App'ni ochish uchun tugmani bosing:", reply_markup=keyboard)

async def on_webhook(request):
    json_str = await request.json()
    update = Update.model_validate(json_str)
    await dp.feed_update(bot, update)
    return web.Response(text="✅ Update qabul qilindi!", status=200)

async def on_ping(request):
    return web.Response(text="✅ Bot ishlayapti!", status=200)

async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook o‘rnatildi: {WEBHOOK_URL}")

async def start_webhook():
    await set_webhook()
    app = web.Application()
    app.router.add_post('/webhook', on_webhook)
    app.router.add_get('/', on_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    
    print(f"🚀 Server {PORT} portda ishlayapti...")
    
    try:
        await asyncio.Event().wait()
    finally:
        await bot.session.close()
        print("🔴 Bot sessiyasi yopildi!")

if __name__ == "__main__":
    asyncio.run(start_webhook())
