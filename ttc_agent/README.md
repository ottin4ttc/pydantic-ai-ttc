# ttc_agent

## 运行 Chat App

要运行 `chat_app.py`，请按照以下步骤操作：

1. 确保你已经安装了所有必要的依赖项。你可以使用 `pip` 来安装它们，通常依赖项会在 `requirements.txt` 或 `pyproject.toml` 文件中列出。

2. 打开终端并导航到项目的根目录。

3. 运行以下命令来启动 `chat_app.py`：

```sh
# 热加载：
uvicorn ttc_agent.chat_app:app --reload

# 正常启动
python -m ttc_agent.chat_app