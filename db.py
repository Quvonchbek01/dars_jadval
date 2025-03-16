import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def connect_db():
    return await asyncpg.connect(DATABASE_URL)

# ✅ Bazani avtomatik yaratish
async def create_table():
    conn = await connect_db()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS feedback (
            user_id BIGINT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    await conn.close()

# ✅ Foydalanuvchini bazaga saqlash
async def save_user(user_id):
    conn = await connect_db()
    await conn.execute("""
        INSERT INTO users (user_id)
        VALUES ($1)
        ON CONFLICT (user_id) DO NOTHING
    """, user_id)
    await conn.close()

# ✅ Kunlik va umumiy foydalanuvchilar
async def get_total_users():
    conn = await connect_db()
    total = await conn.fetchval("SELECT COUNT(*) FROM users")
    await conn.close()
    return total

async def get_daily_users():
    conn = await connect_db()
    daily_users = await conn.fetchval("""
        SELECT COUNT(*)
        FROM users
        WHERE last_active >= CURRENT_DATE
    """)
    await conn.close()
    return daily_users

# ✅ Foydalanuvchining oxirgi faolligini yangilash
async def update_last_active(user_id):
    conn = await connect_db()
    await conn.execute("""
        UPDATE users 
        SET last_active = CURRENT_TIMESTAMP
        WHERE user_id = $1
    """, user_id)
    await conn.close()

# ✅ Adminga murojaatlarni saqlash
async def save_feedback(user_id, message):
    conn = await connect_db()
    await conn.execute("""
        INSERT INTO feedback (user_id, message)
        VALUES ($1, $2)
    """, user_id, message)
    await conn.close()

# ✅ Foydalanuvchilarga xabar yuborish
async def get_all_users():
    conn = await connect_db()
    users = await conn.fetch("SELECT user_id FROM users")
    await conn.close()
    return [user['user_id'] for user in users]
