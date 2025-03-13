# UI 测试说明

本目录包含 TTC Agent 的 UI 测试。这些测试使用 Playwright 来自动化浏览器交互，验证前端功能的正确性。

## 测试结构

- `test_conversation.py`: 测试多个对话的创建和切换功能
- `UITestReadme.md`: 记录前端组件中的 TestId 属性
- `README.md`: 本文件，提供测试说明

## 如何编写 UI 测试

### 1. 使用 TestId 定位元素

所有 UI 测试应该使用 `data-testid` 属性来定位元素，而不是依赖于 CSS 类名、文本内容或 DOM 结构。这样可以使测试更加稳定，不会因为样式或文本变化而失败。

```python
# 推荐：使用 data-testid
button = page.locator('[data-testid="new-conversation-button"]')

# 不推荐：使用文本内容
button = page.get_by_text("新对话")

# 不推荐：使用 CSS 类名
button = page.locator('.some-class-name')
```

### 2. 查阅 UITestReadme.md

在编写测试时，请查阅 `UITestReadme.md` 文件，了解可用的 TestId。该文件记录了前端组件中的所有 TestId 及其用途。

### 3. 使用页面对象模式

为了使测试代码更加清晰和可维护，我们使用页面对象模式。每个页面或主要组件都有一个对应的类，封装了与该页面交互的方法。

```python
class ConversationPage:
    def __init__(self, page):
        self.page = page
        
    def create_new_conversation(self):
        # 使用 TestId 定位按钮
        button = self.page.locator('[data-testid="new-conversation-button"]')
        button.click()
        # 等待网络请求完成
        self.page.wait_for_load_state("networkidle")
```

### 4. 添加足够的等待

UI 测试需要等待页面加载、网络请求完成或元素变为可见。请确保添加足够的等待，避免测试不稳定。

```python
# 等待元素可见
element.wait_for(state="visible")

# 等待网络请求完成
page.wait_for_load_state("networkidle")

# 等待导航完成
page.wait_for_load_state("domcontentloaded")
```

### 5. 添加有用的断言消息

当断言失败时，添加有用的消息可以帮助快速定位问题。

```python
assert first_response != second_response, "First and second responses should be different"
```

## 运行测试

使用提供的脚本运行 UI 测试：

```bash
./run_ui_tests.sh
```

该脚本会：
1. 检查环境变量和依赖
2. 启动后端和前端服务
3. 运行 UI 测试
4. 清理服务

## 调试测试

如果测试失败，可以查看生成的截图和日志：

- `error-screenshot.png`: 当测试遇到错误时的截图
- `page-loaded.png`: 页面加载完成时的截图
- `test-start.png`: 测试开始时的截图
- `after-first-conversation.png`: 第一个对话完成后的截图
- `after-second-conversation.png`: 第二个对话完成后的截图
- `final-state.png`: 测试结束时的截图

这些截图可以帮助理解测试失败的原因。 