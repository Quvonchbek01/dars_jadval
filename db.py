import asyncpg
import os
from dotenv import load_dotenv

# .env fayldan ma'lumotlarni olish
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Postgresga ulanish
async def connect_db():
    return await asyncpg.create_pool(DATABASE_URL)

# Baza yaratish (faqat bir marta)
async def create_db():
    conn = await connect_db()
    async with conn.acquire() as connection:
        # Users jadvali
        await connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            user_name TEXT,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0
        );
        """)
        
        # Feedback jadvali
        await connection.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            user_id BIGINT,
            feedback_text TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

# Foydalanuvchini ro'yxatga olish
async def register_user(user_id, user_name):
    conn = await connect_db()
    async with conn.acquire() as connection:
        await connection.execute("""
        INSERT INTO users (user_id, user_name) 
        VALUES ($1, $2) 
        ON CONFLICT (user_id) DO NOTHING;
        """, user_id, user_name)

# Foydalanuvchi statistikasini olish
async def get_user_stats(user_id):
    conn = await connect_db()
    async with conn.acquire() as connection:
        result = await connection.fetchrow("""
        SELECT last_active, usage_count 
        FROM users 
        WHERE user_id = $1;
        """, user_id)
        return result

# Fikrni saqlash
async def save_feedback(user_id, feedback_text):
    conn = await connect_db()
    async with conn.acquire() as connection:
        await connection.execute("""
        INSERT INTO feedback (user_id, feedback_text) 
        VALUES ($1, $2);
        """, user_id, feedback_text)

# Admin uchun foydalanuvchilar soni
async def get_total_users():
    conn = await connect_db()
    async with conn.acquire() as connection:
        result = await connection.fetchval("SELECT COUNT(*) FROM users;")
        return result

# Bugungi foydalanuvchilar soni
async def get_daily_users():
    conn = await connect_db()
    async with conn.acquire() as connection:
        result = await connection.fetchval("""
        SELECT COUNT(*) 
        FROM users 
        WHERE last_active >= CURRENT_DATE;
        """)
        return result

# Barcha foydalanuvchilar ID sini olish (mass sending uchun)
async def get_all_users():
    conn = await connect_db()
    async with conn.acquire() as connection:
        rows = await connection.fetch("SELECT user_id FROM users;")
        return [row['user_id'] for row in rows]
# ✅ Userning statistikasi va Top 5 foydalanuvchini olish
async def get_top_users():
    from database import conn, cur
    cur.execute("SELECT full_name, usage_count FROM users ORDER BY usage_count DESC LIMIT 5")
    return cur.fetchall()
