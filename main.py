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
from db import register_user, get_user_stats, save_feedback, get_total_users, get_daily_users, get_all_users, create_db

# ✅ .env fayldan token va port olish
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))  # Default port: 10000

# ✅ Bot va Dispatcher
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ✅ FSM uchun state
class UserState(StatesGroup):
    feedback = State()
    broadcast = State()

# ✅ Start menyu
start_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📚 Dars jadvali", web_app=WebAppInfo(url="https://imjadval.netlify.app"))],
    [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="💬 Fikr bildirish")]
], resize_keyboard=True)

# ✅ Admin panel
admin_panel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📈 Foydalanuvchilar statistikasini ko'rish")],
    [KeyboardButton(text="📨 Broadcast")],
    [KeyboardButton(text="⬅️ Orqaga")]
], resize_keyboard=True)

# ✅ Orqaga tugma
back_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="⬅️ Orqaga")]
], resize_keyboard=True)

# ✅ /start handler
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    await register_user(user_id, user_name)
    await message.answer("👋 Assalomu alaykum! Dars jadval botiga xush kelibsiz!", reply_markup=start_menu)

# ✅ 📊 Statistika
@dp.message(lambda message: message.text == "📊 Statistika")
async def show_stats(message: Message):
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)
    await message.answer(f"📅 Oxirgi faollik: {stats['last_active']}\n✅ Umumiy foydalanishlar soni: {stats['usage_count']}")

# ✅ 💬 Fikr bildirish
@dp.message(lambda message: message.text == "💬 Fikr bildirish")
async def start_feedback(message: Message, state: FSMContext):
    await state.set_state(UserState.feedback)
    await message.answer("✍️ Fikringizni yozing:", reply_markup=back_button)

# ✅ 💬 Fikrni qabul qilish + Adminga yuborish
@dp.message(UserState.feedback)
async def handle_feedback(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🔙 Asosiy menyuga qaytdingiz.", reply_markup=start_menu)
        return
    
    user_id = message.from_user.id
    feedback_text = message.text
    
    # ✅ Fikrni bazaga saqlash
    await save_feedback(user_id, feedback_text)
    
    # ✅ Admin ID'ga yuborish
    admin_id = 5883662749  # Admin ID
    await bot.send_message(admin_id, f"💬 Yangi fikr: \n\n{feedback_text}\n\n👤 Fikr egasi: [{message.from_user.full_name}](tg://user?id={user_id})", parse_mode="Markdown")
    
    await message.answer("✅ Fikringiz adminga yuborildi.", reply_markup=start_menu)
    await state.clear()

# ✅ 🛡 Admin panel
@dp.message(Command("admin"))
async def admin_panel_handler(message: Message):
    if message.from_user.id == 5883662749:  # Admin ID
        await message.answer("🛡 Admin panelga xush kelibsiz!", reply_markup=admin_panel)
    else:
        await message.answer("❌ Sizda admin huquqlari yo'q.")

# ✅ 📈 Foydalanuvchilar statistikasi
@dp.message(lambda message: message.text == "📈 Foydalanuvchilar statistikasini ko'rish")
async def admin_stats(message: Message):
    total_users = await get_total_users()
    daily_users = await get_daily_users()
    await message.answer(f"👤 Jami foydalanuvchilar: {total_users}\n📈 Bugungi foydalanuvchilar: {daily_users}")

# ✅ 📨 Mass xabar yuborish
@dp.message(lambda message: message.text == "📨 Broadcast")
async def broadcast_start(message: Message, state: FSMContext):
    await state.set_state(UserState.broadcast)
    await message.answer("✍️ Yuboriladigan xabar matnini kiriting:", reply_markup=back_button)

# ✅ 📩 Mass xabar yuborish logikasi
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

# ✅ Uptimerobot uchun GET so'rovni qabul qiladigan route
async def handle_get_request(request):
    return web.Response(text="✅ Bot ishlayapti!")

# ✅ Webhook o'rnatish
async def on_startup():
    await create_db()  # Baza faqat bir marta yaratiladi
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    
    # 🎯 Muammo yechimi: Dispatcher routerini ro'yxatdan o'tkazish
    dp.include_router(dp.router)

# ✅ Aiohttp server
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
setup_application(app, dp)
app.router.add_get("/", handle_get_request)  # GET so'rov uchun

# ✅ Asosiy async loop
async def main():
    await on_startup()
    await web._run_app(app, host="0.0.0.0", port=PORT)

# ✅ Botni ishga tushirish
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
