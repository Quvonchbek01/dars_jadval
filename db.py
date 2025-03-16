import asyncpg
import os
from dotenv import load_dotenv

# ✅ .env fayldan DATABASE_URL olish
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


# ✅ Databasega ulanish funksiyasi
async def connect_db():
    return await asyncpg.connect(DATABASE_URL)


# ✅ Foydalanuvchilar jadvalini avtomatik yaratish
async def create_db():
    conn = await connect_db()
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
    await conn.close()


# ✅ Foydalanuvchini ro'yxatdan o'tkazish
async def register_user(user_id, full_name):
    conn = await connect_db()
    await conn.execute("""
        INSERT INTO users (user_id, full_name)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE 
        SET usage_count = users.usage_count + 1, last_active = CURRENT_TIMESTAMP;
    """, user_id, full_name)
    await conn.close()


# ✅ Foydalanuvchi statistikasi
async def get_user_stats(user_id):
    conn = await connect_db()
    user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return user


# ✅ Fikrni saqlash
async def save_feedback(user_id, feedback_text):
    conn = await connect_db()
    await conn.execute("""
        INSERT INTO feedback (user_id, feedback_text)
        VALUES ($1, $2);
    """, user_id, feedback_text)
    await conn.close()


# ✅ Jami foydalanuvchilar soni
async def get_total_users():
    conn = await connect_db()
    total_users = await conn.fetchval("SELECT COUNT(*) FROM users;")
    await conn.close()
    return total_users


# ✅ Bugungi foydalanuvchilar soni
async def get_daily_users():
    conn = await connect_db()
    daily_users = await conn.fetchval("""
        SELECT COUNT(*) FROM users
        WHERE last_active::DATE = CURRENT_DATE;
    """)
    await conn.close()
    return daily_users


# ✅ Hammasi userlarni olish (Broadcast uchun)
async def get_all_users():
    conn = await connect_db()
    users = await conn.fetch("SELECT user_id FROM users;")
    await conn.close()
    return [user['user_id'] for user in users]
