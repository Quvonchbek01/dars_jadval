from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import logging
import asyncio
import os
from dotenv import load_dotenv

# ✅ Database funksiyalar
from db import register_user, get_user_stats, save_feedback, get_total_users, get_daily_users, get_all_users, create_db, init_db

# ✅ .env fayldan token va port olish
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))  # Default port: 10000
ADMIN_ID = int(os.getenv("ADMIN_ID", 5883662749))  # Admin ID

# ✅ Bot va Dispatcher
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ✅ FSM uchun state
class UserState(StatesGroup):
    feedback = State()
    broadcast = State()

# ✅ Asosiy menyu
start_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📚 Dars jadvali", web_app=WebAppInfo(url="https://imjadval.netlify.app") )],
    [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="💬 Fikr bildirish")]
], resize_keyboard=True)

# ✅ /start handler
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    await register_user(user_id, user_name)
    await message.answer("👋 Assalomu alaykum!", reply_markup=start_menu)

# ✅ Mass xabar yuborish
@dp.message(UserState.broadcast)
async def broadcast_message(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🔙 Admin panelga qaytdingiz.", reply_markup=start_menu)
        return
    
    users = await get_all_users()
    sent_count, failed_count = 0, 0
    for user_id in users:
        try:
            await bot.send_message(user_id, message.text)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            logging.warning(f"Xatolik: {e}")

    await message.answer(f"✅ {sent_count} ta foydalanuvchiga yuborildi.\n❌ {failed_count} foydalanuvchiga yuborilmadi.", reply_markup=start_menu)
    await state.clear()

# ✅ Webhook o‘rnatish
async def on_startup():
    await init_db()
    await create_db()
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")

# ✅ Aiohttp server
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
setup_application(app, dp)

# ✅ Asosiy async loop
async def main():
    await on_startup()
    await web._run_app(app, host="0.0.0.0", port=PORT)

# ✅ Botni ishga tushirish
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
