import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# Ma'lumotlar bazasiga ulanish
async def connect_db():
    return await asyncpg.connect(DATABASE_URL)

# Foydalanuvchini bazaga saqlash
async def save_user(user_id: int):
    conn = await connect_db()
    await conn.execute("INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)
    await conn.close()

# Barcha userlarni olish
async def get_all_users():
    conn = await connect_db()
    users = await conn.fetch("SELECT user_id FROM users")
    await conn.close()
    return [user['user_id'] for user in users]

# Admin yoki yo'qligini tekshirish
async def is_admin(user_id: int) -> bool:
    return user_id == int(os.getenv("ADMIN_ID"))