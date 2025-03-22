from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, WebAppInfo
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncio
import os
from dotenv import load_dotenv
from db import register_user, get_user_stats, save_feedback, get_total_users, get_daily_users, get_all_users, create_db

# ✅ .env yuklash
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))
ADMIN_ID = 5883662749

# ✅ Bot va Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ✅ FSM uchun state
class UserState(StatesGroup):
    feedback = State()
    broadcast = State()

# ✅ Menyular
start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Dars jadvali", web_app=WebAppInfo(url="https://imjadval.netlify.app"))],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="💬 Fikr bildirish")]
    ], resize_keyboard=True
)

admin_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📈 Foydalanuvchilar statistikasi")],
        [KeyboardButton(text="📨 Xabar yuborish")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ], resize_keyboard=True
)

back_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⬅️ Orqaga")]], resize_keyboard=True)

# ✅ /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await register_user(message.from_user.id, message.from_user.full_name)
    await message.answer("👋 Assalomu alaykum! Forish IM dars jadvali botiga xush kelibsiz!", reply_markup=start_menu)

# ✅ 📊 Statistika
@dp.message(lambda message: message.text == "📊 Statistika")
async def show_stats(message: Message):
    stats = await get_user_stats(message.from_user.id)
    if stats:
        await message.answer(f"📅 Oxirgi faollik: {stats['last_active']}\n✅ Umumiy foydalanishlar soni: {stats['usage_count']}")
    else:
        await message.answer("📊 Siz hali botdan foydalanmagansiz.")

# ✅ 💬 Fikr bildirish
@dp.message(lambda message: message.text == "💬 Fikr bildirish")
async def start_feedback(message: Message, state: FSMContext):
    await state.set_state(UserState.feedback)
    await message.answer("✍️ Botimiz sizga yoqdimi? 1 dan 10 gacha baholang. Botimiz haqida fikr bildiring. Yana qanday imkoniyatlar qo'shilishini xohlar edingiz? Talab va takliflarni ham yozib qoldirishingiz mumkin, siz bilan tez orada bog'lanaman. Rahmat!", reply_markup=back_button)

@dp.message(UserState.feedback)
async def handle_feedback(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🔙 Asosiy menyuga qaytdingiz.", reply_markup=start_menu)
        return

    await save_feedback(message.from_user.id, message.text)
    await bot.send_message(ADMIN_ID, f"💬 Yangi fikr: {message.text}\n👤 [{message.from_user.full_name}](tg://user?id={message.from_user.id})", parse_mode="Markdown")
    await message.answer("✅ Xabaringiz adminga yuborildi.", reply_markup=start_menu)
    await state.clear()

# ✅ 🛡 Admin panel
@dp.message(Command("admin"))
async def admin_panel_handler(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛡 Admin panelga xush kelibsiz!", reply_markup=admin_panel)
    else:
        await message.answer("❌ Sizda admin huquqlari yo‘q.")

# ✅ 📈 Statistika
@dp.message(lambda message: message.text == "📈 Foydalanuvchilar statistikasi")
async def admin_stats(message: Message):
    total_users, daily_users = await get_total_users(), await get_daily_users()
    await message.answer(f"👤 Jami foydalanuvchilar: {total_users}\n📈 Bugungi foydalanuvchilar: {daily_users}")

# ✅ 📨 Broadcast
@dp.message(lambda message: message.text == "📨 Xabar yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    await state.set_state(UserState.broadcast)
    await message.answer("✍️ Yuboriladigan xabar matnini kiriting:", reply_markup=back_button)

@dp.message(UserState.broadcast)
async def broadcast_message(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🔙 Admin panelga qaytdingiz.", reply_markup=admin_panel)
        return

    users = await get_all_users()
    sent_count = 0
    for user_id in users:
        try:
            await bot.send_message(user_id, message.text)
            sent_count += 1
        except:
            continue
    await message.answer(f"✅ {sent_count} ta foydalanuvchiga yuborildi.", reply_markup=admin_panel)
    await state.clear()

# ✅ 🔙 Orqaga qaytish
@dp.message(lambda message: message.text == "⬅️ Orqaga")
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔙 Asosiy menyuga qaytdingiz.", reply_markup=start_menu)

# ✅ Uptimerobot uchun GET request
async def handle_get_request(request):
    return web.Response(text="✅ Bot ishlayapti!")

# ✅ Webhook o‘rnatish
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

# ✅ Botni ishga tushirish
if __name__ == "__main__":
    asyncio.run(main())
