import asyncpg
import os
from datetime import datetime
from dotenv import load_dotenv

# ✅ .env fayldan ma'lumotlarni olish
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL URI (render yoki boshqa serverda)

# ✅ Ma'lumotlar bazasini yaratish funksiyasi
async def create_db():
    conn = await asyncpg.connect(DATABASE_URL)

    # ✅ Foydalanuvchilar jadvali
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        full_name VARCHAR(100),
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usage_count INTEGER DEFAULT 0
    )
    """)

    # ✅ Fikrlar jadvali
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        feedback_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ✅ Foydalanuvchilar statistikasini qayd qiladigan jadval
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS daily_stats (
        date DATE PRIMARY KEY,
        user_count INTEGER DEFAULT 0
    )
    """)

    await conn.close()

# ✅ Foydalanuvchini ro'yxatdan o'tkazish
async def register_user(user_id: int, full_name: str):
    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
    INSERT INTO users (user_id, full_name)
    VALUES ($1, $2)
    ON CONFLICT (user_id) DO NOTHING
    """, user_id, full_name)

    await conn.close()

# ✅ Foydalanuvchi statistikasi
async def get_user_stats(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)

    user_stats = await conn.fetchrow("""
    SELECT last_active, usage_count 
    FROM users 
    WHERE user_id = $1
    """, user_id)

    await conn.close()
    return user_stats

# ✅ Fikrni saqlash
async def save_feedback(user_id: int, feedback_text: str):
    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
    INSERT INTO feedback (user_id, feedback_text)
    VALUES ($1, $2)
    """, user_id, feedback_text)

    await conn.close()

# ✅ Jami foydalanuvchilar sonini olish
async def get_total_users():
    conn = await asyncpg.connect(DATABASE_URL)

    total_users = await conn.fetchval("SELECT COUNT(*) FROM users")

    await conn.close()
    return total_users

# ✅ Bugungi faollikni hisoblash
async def get_daily_users():
    conn = await asyncpg.connect(DATABASE_URL)

    today = datetime.now().date()
    daily_users = await conn.fetchval("""
    SELECT user_count 
    FROM daily_stats 
    WHERE date = $1
    """, today) or 0

    await conn.close()
    return daily_users

# ✅ Barcha foydalanuvchilarning ID'larini olish (Broadcast uchun)
async def get_all_users():
    conn = await asyncpg.connect(DATABASE_URL)

    users = await conn.fetch("SELECT user_id FROM users")

    await conn.close()
    return [user['user_id'] for user in users]
