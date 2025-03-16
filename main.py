import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiohttp import web
from dotenv import load_dotenv
from db import save_user, get_total_users, get_daily_users
from admin import router as admin_router

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(admin_router)

# Reply Keyboard
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📅 Dars jadvali"), KeyboardButton(text="📊 Statistika")],
    [KeyboardButton(text="📩 Adminga murojaat")]
], resize_keyboard=True)

# Orqaga qaytish keyboard
back_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="⬅️ Orqaga qaytish")]
], resize_keyboard=True)

# State
class ContactAdmin(StatesGroup):
    waiting_for_message = State()


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await save_user(message.from_user.id)
    await message.answer(
        "Assalomu alaykum!\n\n"
        "📅 Dars jadvalini ko‘rish uchun 'Dars jadvali' tugmasini bosing.",
        reply_markup=main_keyboard
    )


@dp.message(lambda message: message.text == "📅 Dars jadvali")
async def web_app(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="🗓️ Web App'ni ochish",
            web_app=WebAppInfo(url="https://imjadval.netlify.app")
        )
    ]])
    await message.answer("📢 Dars jadvalini ko'rish uchun tugmani bosing:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "📊 Statistika")
async def show_stats(message: types.Message):
    total_users = await get_total_users()
    daily_users = await get_daily_users()
    await message.answer(f"👤 Jami foydalanuvchilar: {total_users}\n📈 Bugungi foydalanuvchilar: {daily_users}", reply_markup=back_keyboard)


@dp.message(lambda message: message.text == "📩 Adminga murojaat")
async def contact_admin(message: types.Message, state: FSMContext):
    await message.answer("✍️ Adminga yuboradigan xabaringizni yozing:", reply_markup=back_keyboard)
    await state.set_state(ContactAdmin.waiting_for_message)


@dp.message(StateFilter(ContactAdmin.waiting_for_message), lambda message: message.text == "⬅️ Orqaga qaytish")
async def cancel_contact(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Adminga murojaat bekor qilindi.", reply_markup=main_keyboard)


@dp.message(lambda message: message.text == "⬅️ Orqaga qaytish")
async def back_to_main(message: types.Message):
    await message.answer("🔙 Asosiy menyuga qaytdingiz.", reply_markup=main_keyboard)


@dp.message(StateFilter(ContactAdmin.waiting_for_message))
async def forward_to_admin(message: types.Message, state: FSMContext):
    if message.text:
        await bot.send_message(ADMIN_ID, f"👤 @{message.from_user.username}\n\n{message.text}")
        await message.answer("✅ Xabaringiz adminga yetkazildi.", reply_markup=main_keyboard)
        await state.clear()


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
