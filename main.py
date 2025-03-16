import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update
from aiogram.filters import Command
from aiohttp import web
from dotenv import load_dotenv
from db import save_user, get_stats, get_all_users, ban_user, unban_user, save_feedback

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

admin_id = int(os.getenv('ADMIN_ID'))

# ✅ Start command
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await save_user(message.from_user.id)
    await message.answer(
        "Assalomu alaykum!\n\n"
        "📅 Dars jadvalini ko‘rish uchun /web tugmasini bosing.\n\n"
        "✍️ Feedback qoldirish uchun /feedback ni bosing!"
    )

# ✅ Web App ochish
@dp.message(Command("web"))
async def web_app(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="🗓️ Web App'ni ochish",
            web_app=WebAppInfo(url="https://imjadval.netlify.app")
        )
    ]])
    await message.answer("📢 Web App'ni ochish uchun tugmani bosing:", reply_markup=keyboard)

# ✅ Admin panel
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id == admin_id:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("📢 Barchaga xabar", callback_data="send_all")],
            [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
            [InlineKeyboardButton("👤 Userlar ro'yxati", callback_data="user_list")],
            [InlineKeyboardButton("🚫 Ban", callback_data="ban")],
            [InlineKeyboardButton("✅ Unban", callback_data="unban")],
            [InlineKeyboardButton("📝 Feedbacklar", callback_data="feedbacks")]
        ])
        await message.answer("⚡️ Admin panelga xush kelibsiz!", reply_markup=keyboard)
    else:
        await message.answer("❌ Siz admin emassiz!")

# ✅ Barchaga xabar
@dp.callback_query(F.data == "send_all")
async def send_to_all(callback: types.CallbackQuery):
    await callback.message.answer("📢 Barchaga yuboriladigan xabarni yuboring:")
    await bot.send_message(callback.from_user.id, "✅ Xabar tayyor bo‘lsa, menga yuboring!")

# ✅ Statistika
@dp.callback_query(F.data == "stats")
async def stats(callback: types.CallbackQuery):
    stats = await get_stats()
    await callback.message.answer(f"📊 Kunlik: {stats['daily']}\n📈 Oylik: {stats['monthly']}\n🌐 Jami: {stats['total']}")

# ✅ Userlar ro'yxati
@dp.callback_query(F.data == "user_list")
async def user_list(callback: types.CallbackQuery):
    users = await get_all_users()
    await callback.message.answer(f"👤 Userlar soni: {len(users)}")

# ✅ Ban / Unban
@dp.callback_query(F.data == "ban")
async def ban_user_func(callback: types.CallbackQuery):
    await callback.message.answer("❌ Ban qilmoqchi bo'lgan user ID sini yuboring:")

@dp.callback_query(F.data == "unban")
async def unban_user_func(callback: types.CallbackQuery):
    await callback.message.answer("✅ Unban qilmoqchi bo'lgan user ID sini yuboring:")

# ✅ Feedback qoldirish
@dp.message(Command("feedback"))
async def feedback_handler(message: types.Message):
    await message.answer("✍️ Fikr-mulohazangizni yozing:")

@dp.message(F.text)
async def save_feedback_handler(message: types.Message):
    await save_feedback(message.from_user.id, message.text)
    await message.answer("✅ Fikringiz uchun rahmat!")

# ✅ Admin feedbacklarni ko'rishi
@dp.callback_query(F.data == "feedbacks")
async def show_feedbacks(callback: types.CallbackQuery):
    feedbacks = await get_feedbacks()
    text = '\n\n'.join([f"👤 {f['user_id']}: {f['text']}" for f in feedbacks])
    await callback.message.answer(f"📝 Foydalanuvchilar feedbacklari:\n\n{text}")
