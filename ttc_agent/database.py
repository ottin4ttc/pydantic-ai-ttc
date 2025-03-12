import sqlite3
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from typing import Any, Callable, TypeVar, ParamSpec
from typing_extensions import LiteralString

R = TypeVar('R')
P = ParamSpec('P')

class Database:
    """数据库连接和基础操作类"""

    def __init__(self, db_path: Path):
        self._loop = asyncio.get_event_loop()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.con = self._connect(db_path)

    @staticmethod
    def _connect(file: Path) -> sqlite3.Connection:
        con = sqlite3.connect(str(file))
        cur = con.cursor()
        # 创建会话表
        cur.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                role_type TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        ''')
        # 创建消息表
        cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tokens_used INTEGER,
                process_logs TEXT,
                timestamp TIMESTAMP NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')
        con.commit()
        return con

    async def _asyncify(
        self, 
        func: Callable[P, R], 
        *args: P.args, 
        **kwargs: P.kwargs
    ) -> R:
        """将同步操作转换为异步操作"""
        return await self._loop.run_in_executor(
            self._executor,
            partial(func, **kwargs),
            *args,
        )

    def _execute(
        self, 
        sql: LiteralString, 
        *args: Any, 
        commit: bool = False
    ) -> sqlite3.Cursor:
        """执行SQL语句"""
        cur = self.con.cursor()
        cur.execute(sql, args)
        if commit:
            self.con.commit()
        return cur

    async def close(self):
        """关闭数据库连接"""
        await self._asyncify(self.con.close)

@asynccontextmanager
async def get_database(db_path: Path):
    """数据库连接管理器"""
    db = Database(db_path)
    try:
        yield db
    finally:
        await db.close() 