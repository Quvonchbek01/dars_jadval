from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os
import asyncio
from dotenv import load_dotenv
from db import register_user, get_user_stats, save_feedback, get_total_users, get_top_users, get_all_users, create_db

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ✅ FSM uchun state
class UserState(StatesGroup):
    feedback = State()
    broadcast = State()


# ✅ Menyular
start_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📊 Statistika")],
    [KeyboardButton(text="💬 Fikr bildirish")],
], resize_keyboard=True)

admin_panel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📈 Barcha statistika")],
    [KeyboardButton(text="📢 Broadcast")],
    [KeyboardButton(text="⬅️ Orqaga")],
], resize_keyboard=True)

back_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="⬅️ Orqaga")]
], resize_keyboard=True)


# ✅ /start handler
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    await register_user(user_id, user_name)
    await message.answer("👋 Assalomu alaykum!", reply_markup=start_menu)


# ✅ 📊 Statistika
@dp.message(lambda message: message.text == "📊 Statistika")
async def show_stats(message: Message):
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)
    await message.answer(f"✅ Umumiy foydalanishlar soni: {stats['usage_count']}")


# ✅ 💬 Fikr bildirish
@dp.message(lambda message: message.text == "💬 Fikr bildirish")
async def start_feedback(message: Message, state: FSMContext):
    await state.set_state(UserState.feedback)
    await message.answer("✍️ Fikringizni yozing:", reply_markup=back_button)


@dp.message(UserState.feedback)
async def handle_feedback(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🔙 Asosiy menyuga qaytdingiz.", reply_markup=start_menu)
        return
    
    user_id = message.from_user.id
    feedback_text = message.text
    await save_feedback(user_id, feedback_text)
    
    admin_id = 5883662749  # Admin ID
    await bot.send_message(admin_id, f"💬 Yangi feedback:\n\n{feedback_text}\n\n👤 [{message.from_user.full_name}](tg://user?id={user_id})", parse_mode="Markdown")
    
    await message.answer("✅ Fikringiz adminga yuborildi.", reply_markup=start_menu)
    await state.clear()


# ✅ Admin panel
@dp.message(Command("admin"))
async def admin_panel_handler(message: Message):
    if message.from_user.id == 5883662749:
        await message.answer("🛡 Admin panelga xush kelibsiz!", reply_markup=admin_panel)
    else:
        await message.answer("❌ Sizda admin huquqi yo'q.")


# ✅ 📈 Barcha statistikalar
@dp.message(lambda message: message.text == "📈 Barcha statistika")
async def admin_stats(message: Message):
    total_users = await get_total_users()
    top_users = await get_top_users()

    top_text = "\n".join([f"{user['full_name']} — {user['usage_count']} marta" for user in top_users])

    await message.answer(f"👤 Jami foydalanuvchilar: {total_users}\n\n🔥 Top 5 userlar:\n{top_text}")


# ✅ Uptimerobot uchun GET so'rovi
async def handle_get_request(request):
    return web.Response(text="✅ Bot ishlayapti!")


# ✅ Webhook o'rnatish
async def on_startup():
    await create_db()
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")


# ✅ Aiohttp server
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
setup_application(app, dp)
app.router.add_get("/", handle_get_request)


# ✅ Asosiy async loop
async def main():
    await on_startup()
    await web._run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    asyncio.run(main())
