from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from db import is_admin, get_all_users
from aiogram import Bot

router = Router()

# 📋 Admin panel
@router.message(Command("panel"))
async def admin_panel(message: types.Message):
    if await is_admin(message.from_user.id):
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📢 Broadcast")],
            [KeyboardButton(text="🔙 Orqaga")]
        ], resize_keyboard=True)
        await message.answer("📋 Admin paneliga xush kelibsiz!", reply_markup=keyboard)
    else:
        await message.answer("❌ Siz admin emassiz!")

# 📢 Broadcastni boshlash
@router.message(F.text == "📢 Broadcast")
async def start_broadcast(message: types.Message):
    if await is_admin(message.from_user.id):
        await message.answer("📢 Yuboriladigan xabarni kiriting:")
    else:
        await message.answer("❌ Siz admin emassiz!")

# 📝 Broadcast matnini qabul qilish
@router.message(F.text)
async def handle_broadcast_text(message: types.Message, bot: Bot):
    if await is_admin(message.from_user.id):
        users = await get_all_users()
        for user_id in users:
            try:
                await bot.send_message(chat_id=user_id, text=message.text)
            except:
                pass
        await message.answer("✅ Broadcast muvaffaqiyatli yakunlandi!")