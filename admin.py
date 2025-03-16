from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import get_total_users, get_daily_users, get_all_users, save_feedback

admin_router = Router()

# 🎛️ Admin keyboard
admin_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📨 Xabar yuborish")],
    [KeyboardButton(text="💬 Adminga murojaat"), KeyboardButton(text="⬅️ Orqaga")]
], resize_keyboard=True)

back_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="⬅️ Orqaga")]
], resize_keyboard=True)

admin_state = None


@admin_router.message(Command("admin"))
async def admin_panel(message: types.Message):
    await message.answer("🛡 Admin paneliga xush kelibsiz!", reply_markup=admin_keyboard)


@admin_router.message(lambda message: message.text == "📊 Statistika")
async def show_stats(message: types.Message):
    total_users = await get_total_users()
    daily_users = await get_daily_users()
    await message.answer(
        f"👤 Jami foydalanuvchilar: {total_users}\n📈 Bugungi foydalanuvchilar: {daily_users}",
        reply_markup=back_keyboard
    )


@admin_router.message(lambda message: message.text == "📨 Xabar yuborish")
async def broadcast_start(message: types.Message):
    global admin_state
    admin_state = 'broadcast'
    await message.answer("✍️ Xabar matnini yuboring:", reply_markup=back_keyboard)


@admin_router.message(lambda message: message.text == "💬 Adminga murojaat")
async def feedback_start(message: types.Message):
    global admin_state
    admin_state = 'feedback'
    await message.answer("✍️ Adminga murojaat matnini yuboring:", reply_markup=back_keyboard)


@admin_router.message(lambda message: message.text == "⬅️ Orqaga")
async def back_to_main(message: types.Message):
    global admin_state
    admin_state = None
    await message.answer("🔙 Admin paneliga qaytdingiz.", reply_markup=admin_keyboard)


@admin_router.message(lambda message: message.text and admin_state == 'broadcast')
async def send_broadcast(message: types.Message, bot: types.Bot):
    global admin_state
    users = await get_all_users()
    sent_count = 0
    for user_id in users:
        try:
            await bot.send_message(user_id, message.text)
            sent_count += 1
        except:
            continue

    await message.answer(f"✅ {sent_count} ta foydalanuvchiga yuborildi.", reply_markup=admin_keyboard)
    admin_state = None


@admin_router.message(lambda message: message.text and admin_state == 'feedback')
async def send_feedback(message: types.Message):
    global admin_state
    await save_feedback(message.from_user.id, message.text)
    await message.answer("✅ Murojaatingiz adminga yuborildi.", reply_markup=admin_keyboard)
    admin_state = None
