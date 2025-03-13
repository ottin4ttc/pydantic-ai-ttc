"""Simple chat app example build with FastAPI.

Run with:

    uv run -m ttc_agent.chat_app
"""

from __future__ import annotations as _annotations

import asyncio
import json
import sqlite3
import os
from collections.abc import AsyncIterator
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Annotated, Any, Callable, Literal, TypeVar

import fastapi
import logfire
from fastapi import Depends, Request
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing_extensions import LiteralString, ParamSpec, TypedDict
from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

# Load environment variables from .env file
load_dotenv()

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')

openaiKey = os.getenv('OPENAI_API_KEY')
dmxKey = os.getenv('DMX_API_KEY')

if not openaiKey or not dmxKey:
    raise ValueError("API keys must be set in .env file")

model = OpenAIModel(
        'gpt-4o-mini',
        provider=OpenAIProvider(api_key=openaiKey)
    )

modelDmx = OpenAIModel(
        'gpt-4o-mini',
        provider=OpenAIProvider(
            api_key=dmxKey,
            base_url='https://vip.dmxapi.com/v1'
        )
    )

agent = Agent(modelDmx, instrument=True)
THIS_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(_app: fastapi.FastAPI):
    async with Database.connect() as db:
        yield {'db': db}


from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI(lifespan=lifespan)
logfire.instrument_fastapi(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from .direct_api import router as direct_router
from .api import router as api_router
app.include_router(direct_router, prefix="/api")  # Keep existing API prefix for compatibility
app.include_router(api_router, prefix="/api")

# Mount static files
app.mount("/static", StaticFiles(directory=THIS_DIR / "static"), name="static")


@app.get('/')
async def index() -> FileResponse:
    static_dir = THIS_DIR / "static"
    if static_dir.exists() and (static_dir / "index.html").exists():
        return FileResponse(static_dir / "index.html")
    return FileResponse((THIS_DIR / 'chat_app.html'), media_type='text/html')

@app.get('/chat_app.ts')
async def main_ts() -> FileResponse:
    """Get the raw typescript code, it's compiled in the browser, forgive me."""
    return FileResponse((THIS_DIR / 'chat_app.ts'), media_type='text/plain')


async def get_db(request: Request) -> Database:
    return request.state.db


@app.get('/api/chat/')
async def get_chat(database: Database = Depends(get_db)) -> Response:
    msgs = await database.get_messages()
    return Response(
        b'\n'.join(json.dumps(to_chat_message(m)).encode('utf-8') for m in msgs),
        media_type='text/plain',
    )


class ChatMessage(TypedDict):
    """Format of messages sent to the browser."""

    role: Literal['user', 'model']
    timestamp: str
    content: str


def to_chat_message(m: ModelMessage) -> ChatMessage:
    first_part = m.parts[0]
    if isinstance(m, ModelRequest):
        if isinstance(first_part, UserPromptPart):
            assert isinstance(first_part.content, str)
            return {
                'role': 'user',
                'timestamp': first_part.timestamp.isoformat(),
                'content': first_part.content,
            }
    elif isinstance(m, ModelResponse):
        if isinstance(first_part, TextPart):
            return {
                'role': 'model',
                'timestamp': m.timestamp.isoformat(),
                'content': first_part.content,
            }
    raise UnexpectedModelBehavior(f'Unexpected message type for chat app: {m}')


@app.post('/api/chat/')
async def post_chat(
    prompt: Annotated[str, fastapi.Form()], database: Database = Depends(get_db)
) -> StreamingResponse:
    async def stream_messages():
        """Streams new line delimited JSON `Message`s to the client."""
        # stream the user prompt so that can be displayed straight away
        yield (
            json.dumps(
                {
                    'role': 'user',
                    'timestamp': datetime.now(tz=timezone.utc).isoformat(),
                    'content': prompt,
                }
            ).encode('utf-8')
            + b'\n'
        )
        # get the chat history so far to pass as context to the agent
        messages = await database.get_messages()
        # run the agent with the user prompt and the chat history
        async with agent.run_stream(prompt, message_history=messages) as result:
            async for text in result.stream(debounce_by=0.01):
                # text here is a `str` and the frontend wants
                # JSON encoded ModelResponse, so we create one
                m = ModelResponse(parts=[TextPart(text)], timestamp=result.timestamp())
                yield json.dumps(to_chat_message(m)).encode('utf-8') + b'\n'

        # add new messages (e.g. the user prompt and the agent response in this case) to the database
        await database.add_messages(result.new_messages_json())

    return StreamingResponse(stream_messages(), media_type='text/plain')


@app.post('/api/chat/{conversation_id}')
async def post_chat_with_id(
    conversation_id: str,
    request: Request,
    database: Database = Depends(get_db)
) -> StreamingResponse:
    # 解析请求体中的 JSON 数据
    data = await request.json()
    prompt = data.get('content', '')
    # role_type 暂时未使用，但保留以便将来扩展
    # role_type = data.get('role_type', 'default')
    
    async def stream_messages():
        """Streams new line delimited JSON `Message`s to the client."""
        # stream the user prompt so that can be displayed straight away
        yield (
            json.dumps(
                {
                    'role': 'user',
                    'timestamp': datetime.now(tz=timezone.utc).isoformat(),
                    'content': prompt,
                }
            ).encode('utf-8')
            + b'\n'
        )
        # 获取特定会话的聊天历史
        messages = await database.get_messages(conversation_id)
        # run the agent with the user prompt and the chat history
        async with agent.run_stream(prompt, message_history=messages) as result:
            async for text in result.stream(debounce_by=0.01):
                # text here is a `str` and the frontend wants
                # JSON encoded ModelResponse, so we create one
                m = ModelResponse(parts=[TextPart(text)], timestamp=result.timestamp())
                yield json.dumps(to_chat_message(m)).encode('utf-8') + b'\n'

        # 将新消息添加到特定会话
        await database.add_messages(result.new_messages_json(), conversation_id)

    return StreamingResponse(stream_messages(), media_type='text/plain')


@app.get('/api/chat/{conversation_id}/history')
async def get_chat_history_by_id(
    conversation_id: str,
    database: Database = Depends(get_db)
) -> list[ChatMessage]:
    # 获取特定会话的聊天历史
    msgs = await database.get_messages(conversation_id)
    return [to_chat_message(m) for m in msgs]


class ConversationDict(TypedDict):
    """会话数据的类型定义"""
    id: str
    role_type: str
    created_at: str
    updated_at: str

@app.get('/api/conversations')
async def get_conversations() -> list[ConversationDict]:
    # 由于我们目前没有真正的会话存储，所以返回一个模拟的会话列表
    # 在实际应用中，这应该从数据库中获取
    return [
        {
            "id": "d1c689f1-5d92-4af3-a123-25d783870486",
            "role_type": "default",
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "updated_at": datetime.now(tz=timezone.utc).isoformat()
        }
    ]

@app.get('/api/conversations/{conversation_id}')
async def get_conversation(conversation_id: str) -> ConversationDict:
    # 由于我们目前没有真正的会话存储，所以返回一个模拟的会话
    # 在实际应用中，这应该从数据库中获取
    return {
        "id": conversation_id,
        "role_type": "default",
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "updated_at": datetime.now(tz=timezone.utc).isoformat()
    }

# 将通配符路由移到最后，确保所有 API 路由先匹配
@app.get('/{path:path}')
async def serve_react(path: str):
    static_dir = THIS_DIR / "static"
    if path and (static_dir / path).exists():
        return FileResponse(static_dir / path)
    elif static_dir.exists() and (static_dir / "index.html").exists():
        return FileResponse(static_dir / "index.html")
    return FileResponse((THIS_DIR / 'chat_app.html'), media_type='text/html')


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
        cls, file: Path = THIS_DIR / '.chat_app_messages.sqlite'
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
        
        # 检查消息表是否存在
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        messages_table_exists = cur.fetchone() is not None
        
        if messages_table_exists:
            # 检查表结构
            cur.execute("PRAGMA table_info(messages)")
            columns = [column[1] for column in cur.fetchall()]
            
            # 如果没有 conversation_id 列，添加它
            if 'conversation_id' not in columns:
                print("Adding conversation_id column to messages table")
                cur.execute("ALTER TABLE messages ADD COLUMN conversation_id TEXT DEFAULT 'default'")
                con.commit()
        else:
            # 创建新表
            cur.execute(
                'CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT, message_list TEXT);'
            )
            con.commit()
        
        # 检查会话表是否存在
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
        conversations_table_exists = cur.fetchone() is not None
        
        if conversations_table_exists:
            # 检查表结构
            cur.execute("PRAGMA table_info(conversations)")
            columns = [column[1] for column in cur.fetchall()]
            
            # 如果没有 bot_name 列，添加它
            if 'bot_name' not in columns:
                print("Adding bot_name column to conversations table")
                cur.execute("ALTER TABLE conversations ADD COLUMN bot_name TEXT DEFAULT 'Assistant'")
                con.commit()
        else:
            # 创建新表
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
            con.commit()
        
        return con

    async def add_messages(self, messages: bytes, conversation_id: str = "default"):
        try:
            await self._asyncify(
                self._execute,
                'INSERT INTO messages (conversation_id, message_list) VALUES (?, ?);',
                conversation_id,
                messages,
                commit=True,
            )
            await self._asyncify(self.con.commit)
        except Exception as e:
            print(f"Error adding messages: {e}")

    async def get_messages(self, conversation_id: str | None = None) -> list[ModelMessage]:
        try:
            if conversation_id:
                # 如果提供了会话 ID，只获取该会话的消息
                c = await self._asyncify(
                    self._execute, 'SELECT message_list FROM messages WHERE conversation_id = ? ORDER BY id', conversation_id
                )
            else:
                # 否则获取所有消息
                c = await self._asyncify(
                    self._execute, 'SELECT message_list FROM messages ORDER BY id'
                )
            rows = await self._asyncify(c.fetchall)
            messages: list[ModelMessage] = []
            for row in rows:
                messages.extend(ModelMessagesTypeAdapter.validate_json(row[0]))
            return messages
        except Exception as e:
            print(f"Error getting messages: {e}")
            # 如果出错，返回空列表
            return []

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


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'ttc_agent.chat_app:app', reload=True, reload_dirs=[str(THIS_DIR)]
    )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                