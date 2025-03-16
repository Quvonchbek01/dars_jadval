import asyncpg
from config import DB_URL


# 🚀 Databaseni yaratish (faqat bir marta)
async def create_db():
    conn = await asyncpg.connect(DB_URL)
    
    # ✅ Agar users jadvali mavjud bo'lsa, boshqa jadvallar ham bor deb hisoblanadi
    table_exists = await conn.fetchval('''
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'users'
    );
    ''')

    if not table_exists:
        # ✅ Users jadvali
        await conn.execute('''
        CREATE TABLE users (
            user_id BIGINT PRIMARY KEY,
            user_name TEXT,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')

        # ✅ Feedback jadvali
        await conn.execute('''
        CREATE TABLE feedback (
            user_id BIGINT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')

        # ✅ Banned users jadvali
        await conn.execute('''
        CREATE TABLE banned_users (
            user_id BIGINT PRIMARY KEY,
            banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
    
    await conn.close()
