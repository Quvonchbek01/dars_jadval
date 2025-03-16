import asyncpg
import os
from dotenv import load_dotenv

# ✅ .env faylni yuklash
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ✅ Databasega ulanish
async def connect_db():
    return await asyncpg.connect(DATABASE_URL)


# ✅ Databaseni avtomatik yaratish
async def create_db():
    conn = await connect_db()
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        full_name VARCHAR(255),
        usage_count INTEGER DEFAULT 0,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        feedback_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Eng faol foydalanuvchini olish uchun trigger
    CREATE OR REPLACE FUNCTION update_usage() RETURNS TRIGGER AS $$
    BEGIN
        UPDATE users SET usage_count = usage_count + 1, last_active = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS usage_trigger ON users;
    CREATE TRIGGER usage_trigger
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_usage();
    ''')
    await conn.close()


# ✅ Foydalanuvchini ro'yxatdan o'tkazish
async def register_user(user_id, full_name):
    conn = await connect_db()
    await conn.execute('''
    INSERT INTO users (user_id, full_name)
    VALUES ($1, $2)
    ON CONFLICT (user_id) DO NOTHING
    ''', user_id, full_name)
    await conn.close()


# ✅ Foydalanuvchi statistikasini olish
async def get_user_stats():
    conn = await connect_db()

    total_users = await conn.fetchval('SELECT COUNT(*) FROM users')

    top_users = await conn.fetch('''
    SELECT full_name, usage_count 
    FROM users 
    ORDER BY usage_count DESC
    LIMIT 5
    ''')

    await conn.close()

    return {
        'total_users': total_users,
        'top_users': top_users
    }


# ✅ Foydalanuvchi aktivligini yangilash
async def update_usage(user_id):
    conn = await connect_db()
    await conn.execute('''
    UPDATE users SET usage_count = usage_count + 1, last_active = CURRENT_TIMESTAMP WHERE user_id = $1
    ''', user_id)
    await conn.close()


# ✅ Barcha userlarni olish (Broadcast uchun)
async def get_all_users():
    conn = await connect_db()
    result = await conn.fetch('SELECT user_id FROM users')
    await conn.close()
    return [row['user_id'] for row in result]
