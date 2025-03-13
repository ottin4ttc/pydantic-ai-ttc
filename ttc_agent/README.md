# ttc_agent

## 运行 Chat App

### 方法一：使用启动脚本（推荐）

使用项目根目录中的 `start_ttc_agent.sh` 脚本可以同时启动后端和前端服务：

```sh
# 在项目根目录下执行
./start_ttc_agent.sh
```

这个脚本会：
1. 启动后端服务 (http://127.0.0.1:8000)
2. 等待后端服务完全启动
3. 启动前端服务 (http://localhost:5173)
4. 按 Ctrl+C 可以同时停止所有服务

### 方法二：分别启动服务

如果需要单独启动服务，请按照以下步骤操作：

1. 确保你已经安装了所有必要的依赖项。你可以使用 `pip` 来安装它们，通常依赖项会在 `requirements.txt` 或 `pyproject.toml` 文件中列出。

2. 打开终端并导航到项目的根目录。

3. 运行以下命令来启动后端服务：

```sh
# 热加载：
uvicorn ttc_agent.chat_app:app --reload

# 正常启动
python -m ttc_agent.chat_app
```

4. 在另一个终端中，导航到前端目录并启动前端服务：

```sh
# 导航到前端目录
cd ttc_agent/react_frontend

# 安装依赖（如果尚未安装）
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 上运行，后端服务将在 http://127.0.0.1:8000 上运行。
