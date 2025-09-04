import sqlite3
import datetime

from config import DB_FILE

def get_db_connection():
    """
    创建并返回一个SQLite数据库连接。
    配置row_factory以便可以通过列名访问数据。
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """
    设置数据库，创建所有需要的表并插入示例数据（如果不存在）。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            last_active_at TEXT,
            goal TEXT
        )
    ''')

    # 对话记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message_type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 情绪日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            emotion TEXT NOT NULL,
            intensity INTEGER NOT NULL,
            note TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 资源表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # 标签表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # 资源标签关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resource_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            FOREIGN KEY (resource_id) REFERENCES resources(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id),
            UNIQUE(resource_id, tag_id)
        )
    ''')

    # 插入示例数据（如果表为空）
    cursor.execute("SELECT COUNT(*) FROM resources")
    if cursor.fetchone()[0] == 0:
        print("正在插入示例资源数据...")
        current_time = datetime.datetime.now().isoformat()
        
        resources_data = [
            ('正念冥想入门', 'audio', 'http://example.com/mindfulness.mp3', '一段帮助放松的冥想音频', current_time),
            ('焦虑管理指南', 'article', 'http://example.com/anxiety-guide', '关于如何管理焦虑情绪的文章', current_time),
            ('深呼吸练习', 'exercise', 'http://example.com/breathing', '简单的深呼吸放松练习', current_time),
            ('情绪日记模板', 'article', 'http://example.com/emotion-journal', '帮助记录情绪变化的模板', current_time),
            ('渐进式肌肉放松', 'video', 'http://example.com/pmr', '渐进式肌肉放松教学视频', current_time)
        ]
        
        cursor.executemany("INSERT INTO resources (title, type, url, description, created_at) VALUES (?, ?, ?, ?, ?)", resources_data)
        
        tags_data = [('放松',), ('焦虑管理',), ('正念',), ('情绪记录',), ('睡眠',)]
        cursor.executemany("INSERT OR IGNORE INTO tags (name) VALUES (?)", tags_data)
        
        resource_tags_data = [
            (1, 1), (1, 3), (2, 2), (2, 3), (3, 1), (3, 2), (4, 2), (4, 4), (5, 1), (5, 5)
        ]
        cursor.executemany("INSERT OR IGNORE INTO resource_tags (resource_id, tag_id) VALUES (?, ?)", resource_tags_data)

    conn.commit()
    conn.close()
    print("✅ 数据库表已设置完毕，包含示例数据。")

def get_user_conversation_history(user_id: int, limit: int = 5) -> str:
    """从数据库获取用户最近的对话历史。"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT message_type, content FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", 
                   (user_id, limit))
    history = cursor.fetchall()
    conn.close()
    formatted_history = [f"{row['message_type']}: {row['content']}" for row in reversed(history)]
    return "\n".join(formatted_history)

def save_conversation_message(user_id: int, message_type: str, content: str):
    """保存对话消息到数据库。"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (user_id, message_type, content, timestamp) VALUES (?, ?, ?, ?)",
                   (user_id, message_type, content, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_emotion_log(user_id: int, emotion: str, intensity: int, note: str = None) -> bool:
    """保存情绪日志到数据库。"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO emotion_logs (user_id, timestamp, emotion, intensity, note) VALUES (?, ?, ?, ?, ?)",
                       (user_id, datetime.datetime.now().isoformat(), emotion, intensity, note))
        conn.commit()
        return True
    except Exception as e:
        print(f"保存情绪日志失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def find_resources(tag: str = None) -> list:
    """根据标签从数据库查询资源。"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if tag:
        cursor.execute('''
            SELECT r.title, r.type, r.url
            FROM resources r
            JOIN resource_tags rt ON r.id = rt.resource_id
            JOIN tags t ON rt.tag_id = t.id
            WHERE t.name = ?
            LIMIT 3
        ''', (tag,))
    else:
        cursor.execute("SELECT title, type, url FROM resources LIMIT 3")
    
    resources = cursor.fetchall()
    conn.close()
    return [{"title": r['title'], "type": r['type'], "url": r['url']} for r in resources]