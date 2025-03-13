# UI 测试指南

本文档记录了前端组件中用于 UI 测试的 TestId 属性，以便测试代码可以可靠地定位和交互这些元素。

## 测试 ID 命名约定

所有用于测试的元素都使用 `data-testid` 属性进行标记。命名约定如下：

- 容器元素: `{component-name}-container`
- 按钮: `{action}-button`
- 输入框: `{purpose}-input`
- 列表项: `{item-type}-{id}`

## 主要组件测试 ID

### 聊天容器 (ChatContainer)

| 元素 | TestId | 描述 |
|------|--------|------|
| 主容器 | `chat-container` | 整个聊天界面的容器 |
| 聊天主区域 | `chat-main` | 右侧聊天主区域 |
| 聊天头部 | `chat-header` | 聊天标题区域 |
| 消息滚动区域 | `messages-scroll-area` | 消息列表的滚动区域 |
| 空消息提示 | `empty-messages` | 无消息时显示的提示 |
| 加载指示器 | `loading-indicator` | 消息加载中的指示器 |
| 错误提示 | `error-alert` | 错误消息提示 |
| 输入区域 | `chat-input-area` | 消息输入区域 |
| 聊天表单 | `chat-form` | 消息输入表单 |
| 消息输入框 | `message-input` | 消息输入框 |
| 发送按钮 | `send-button` | 发送消息按钮 |

### 对话列表 (ConversationList)

| 元素 | TestId | 描述 |
|------|--------|------|
| 列表容器 | `conversation-list` | 对话列表容器 |
| 新建对话按钮 | `new-conversation-button` | 创建新对话的按钮 |
| 对话列表容器 | `conversations-container` | 包含所有对话项的容器 |
| 对话项 | `conversation-{id}` | 单个对话项，其中 {id} 是对话的唯一标识符 |

### 消息项 (MessageItem)

| 元素 | TestId | 描述 |
|------|--------|------|
| 消息容器 | `message-{id}` | 单个消息的容器，其中 {id} 是消息的唯一标识符 |
| 助手头像 | `assistant-avatar` | AI 助手的头像 |
| 用户头像 | `user-avatar` | 用户的头像 |
| 消息内容 | `message-content` | 消息的主体内容容器 |
| 消息文本 | `message-text` | 消息的文本内容 |
| 消息时间戳 | `message-timestamp` | 消息的时间戳 |

### 其他属性

除了 `data-testid` 外，一些元素还有其他有用的属性：

| 属性 | 描述 |
|------|------|
| `data-message-role` | 消息的角色（user 或 model） |
| `data-message-id` | 消息的唯一标识符 |
| `data-conversation-id` | 对话的唯一标识符 |
| `data-is-current` | 标识当前活跃的对话（值为 "true" 或 "false"） |

## 使用示例

在测试代码中，可以使用这些 TestId 来定位元素：

```typescript
// 查找新建对话按钮
const newConvButton = page.locator('[data-testid="new-conversation-button"]');

// 查找消息输入框
const messageInput = page.locator('[data-testid="message-input"]');

// 查找发送按钮
const sendButton = page.locator('[data-testid="send-button"]');

// 查找当前活跃的对话
const activeConversation = page.locator('[data-is-current="true"]');

// 查找所有消息
const messages = page.locator('[data-testid^="message-"]');

// 查找最后一条消息的文本
const lastMessageText = page.locator('[data-testid="message-text"]').last();
``` 