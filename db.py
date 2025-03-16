import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ✅ PostgreSQL ulanish
async def create_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        full_name TEXT,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usage_count INTEGER DEFAULT 1,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    await conn.close()


# ✅ Foydalanuvchini ro'yxatdan o'tkazish
async def register_user(user_id, full_name):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
    INSERT INTO users (user_id, full_name) 
    VALUES ($1, $2)
    ON CONFLICT (user_id) DO UPDATE 
    SET usage_count = users.usage_count + 1, last_active = CURRENT_TIMESTAMP;
    """, user_id, full_name)
    await conn.close()


# ✅ Foydalanuvchi statistikasini olish
async def get_user_stats(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    result = await conn.fetchrow("SELECT usage_count, last_active FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return result


# ✅ Jami foydalanuvchilar soni
async def get_total_users():
    conn = await asyncpg.connect(DATABASE_URL)
    result = await conn.fetchval("SELECT COUNT(*) FROM users")
    await conn.close()
    return result


# ✅ Top 5 eng faol foydalanuvchilar
async def get_top_users():
    conn = await asyncpg.connect(DATABASE_URL)
    result = await conn.fetch("SELECT full_name, usage_count FROM users ORDER BY usage_count DESC LIMIT 5")
    await conn.close()
    return result


# ✅ Barcha foydalanuvchilar ID'si (broadcast uchun)
async def get_all_users():
    conn = await asyncpg.connect(DATABASE_URL)
    result = await conn.fetch("SELECT user_id FROM users")
    await conn.close()
    return [user['user_id'] for user in result]


# ✅ Fikrlarni saqlash
async def save_feedback(user_id, feedback):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO feedback (user_id, feedback_text) VALUES ($1, $2)", user_id, feedback)
    await conn.close()
