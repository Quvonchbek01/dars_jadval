import asyncpg
import os
from dotenv import load_dotenv

# ✅ .env fayldan DATABASE_URL olish
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Databasega ulanish (pool orqali)
pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

# ✅ Foydalanuvchilar jadvalini yaratish
async def create_db():
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                full_name TEXT,
                usage_count INTEGER DEFAULT 1,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                feedback_text TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

# ✅ Foydalanuvchini ro‘yxatdan o‘tkazish
async def register_user(user_id, full_name):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, full_name)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE 
            SET usage_count = users.usage_count + 1, last_active = CURRENT_TIMESTAMP;
        """, user_id, full_name)

# ✅ Foydalanuvchi statistikasi
async def get_user_stats(user_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

# ✅ Fikrni saqlash
async def save_feedback(user_id, feedback_text):
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO feedback (user_id, feedback_text) VALUES ($1, $2);", user_id, feedback_text)

# ✅ Jami foydalanuvchilar soni
async def get_total_users():
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM users;")

# ✅ Bugungi foydalanuvchilar soni
async def get_daily_users():
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            SELECT COUNT(*) FROM users
            WHERE last_active::DATE = CURRENT_DATE;
        """)

# ✅ Barcha userlarni olish (Broadcast uchun)
async def get_all_users():
    async with pool.acquire() as conn:
        return [row['user_id'] for row in await conn.fetch("SELECT user_id FROM users;")]
