"""Database module for the chat app."""

from __future__ import annotations as _annotations

import asyncio
import json
import sqlite3
import uuid
from collections.abc import AsyncIterator
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Callable, TypeVar

import logfire
from typing_extensions import LiteralString, ParamSpec

from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter

P = ParamSpec('P')
R = TypeVar('R')


@dataclass
class Database:
    """Rudimentary database to store chat messages in SQLite.

    The SQLite standard library package is synchronous, so we
    use a thread pool executor to run queries asynchronously.
    """

    con: sqlite3.Connection
    _loop: asyncio.AbstractEventLoop
    _executor: ThreadPoolExecutor

    @classmethod
    @asynccontextmanager
    async def connect(
        cls, file: Path = Path(__file__).parent / '.chat_app_messages.sqlite'
    ) -> AsyncIterator[Database]:
        with logfire.span('connect to DB'):
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            con = await loop.run_in_executor(executor, cls._connect, file)
            slf = cls(con, loop, executor)
        try:
            yield slf
        finally:
            await slf._asyncify(con.close)

    @staticmethod
    def _connect(file: Path) -> sqlite3.Connection:
        con = sqlite3.connect(str(file))
        con = logfire.instrument_sqlite3(con)
        cur = con.cursor()
        with logfire.span('CREATE'):
            # Create messages table
            cur.execute(
                'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message_list TEXT);'
            )
            # Create conversations table
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    role_type TEXT,
                    bot_name TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                '''
            )
            # Create bots table
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS bots (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role_type TEXT NOT NULL,
                    system_prompt TEXT NOT NULL,
                    is_default BOOLEAN DEFAULT 0,
                    created_at TEXT,
                    updated_at TEXT
                );
                '''
            )
            
            # Insert default bots if none exist
            cur.execute("SELECT COUNT(*) FROM bots")
            if cur.fetchone()[0] == 0:
                now = datetime.now().isoformat()
                # Insert Xiaomai (小麦) as the default bot
                cur.execute(
                    '''
                    INSERT INTO bots (id, name, role_type, system_prompt, is_default, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (str(uuid.uuid4()), "小麦", "ttc_assistant", 
                     """You are 小麦 (Xiaomai), TTC's dedicated AI assistant. Your role is to help both TTC employees and customers:

For TTC Employees:
- Assist with internal processes and workflows
- Provide guidance on company policies and procedures
- Help with technical documentation and resources
- Support project management and team collaboration

For TTC Customers:
- Provide professional and friendly customer service
- Explain TTC's products and services clearly
- Help troubleshoot technical issues
- Guide users through setup and configuration
- Answer questions about pricing and features

Always maintain a helpful, professional, and friendly tone. Communicate clearly in both English and Chinese as needed. When unsure, ask for clarification to provide the most accurate assistance.""",
                     1, now, now)
                )
        con.commit()
        return con

    async def add_messages(self, messages: bytes):
        await self._asyncify(
            self._execute,
            'INSERT INTO messages (message_list) VALUES (?);',
            messages,
            commit=True,
        )
        await self._asyncify(self.con.commit)

    async def get_messages(self) -> list[ModelMessage]:
        c = await self._asyncify(
            self._execute, 'SELECT message_list FROM messages order by id'
        )
        rows = await self._asyncify(c.fetchall)
        messages: list[ModelMessage] = []
        for row in rows:
            messages.extend(ModelMessagesTypeAdapter.validate_json(row[0]))
        return messages

    def _execute(
        self, sql: LiteralString, *args: Any, commit: bool = False
    ) -> sqlite3.Cursor:
        cur = self.con.cursor()
        cur.execute(sql, args)
        if commit:
            self.con.commit()
        return cur

    async def _asyncify(
        self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs
    ) -> R:
        return await self._loop.run_in_executor(  # type: ignore
            self._executor,
            partial(func, **kwargs),
            *args,  # type: ignore
        )


async def get_database(request: Any) -> Database:
    """Get the database from the request state."""
    return request.state.db
