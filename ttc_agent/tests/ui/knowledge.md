# UI 测试知识库

## 测试环境设置

### 前置条件
- Python 3.8+
- pytest
- pytest-playwright
- Node.js 和 npm（用于运行前端服务）

### 安装
```bash
# 安装 Python 依赖
pip install pytest-playwright
playwright install  # 安装浏览器二进制文件

# 安装前端依赖
cd ttc_agent/react_frontend
npm install
```

### 运行测试
我们提供了一个便捷的脚本来运行UI测试：

```bash
./run_ui_tests.sh
```

这个脚本会：
1. 启动后端服务（默认端口 8000）
2. 启动前端服务（默认端口 5173）
3. 等待服务就绪
4. 运行UI测试
5. 清理所有服务

如果你需要单独运行测试（服务已经在运行），可以直接使用：
```bash
pytest tests/ui/test_conversation.py -v
```

## 测试结构

### 位置
- 所有UI测试位于 `tests/ui/` 目录
- 主要测试文件:
  - `test_conversation.py`: 对话管理和消息流测试

### 测试类别

1. 对话管理测试
   - 创建新对话
   - 在对话之间切换
   - 验证对话持久性

2. 消息流测试
   - 发送消息
   - 接收响应
   - 消息历史验证

## 组件测试属性

### 1. ChatInterface 组件
主要的聊天界面组件测试属性：
```html
<div data-testid="chat-interface">              <!-- 整个聊天界面 -->
  <div data-testid="chat-header">              <!-- 聊天头部 -->
  <div data-testid="chat-messages">            <!-- 消息列表区域 -->
    <div data-testid="user-message">           <!-- 用户消息 -->
    <div data-testid="assistant-message">      <!-- 助手消息 -->
    <div data-testid="message-loading">        <!-- 加载状态 -->
  <div data-testid="chat-input-container">     <!-- 输入区域容器 -->
    <form data-testid="chat-form">            <!-- 消息输入表单 -->
      <input data-testid="chat-input">        <!-- 消息输入框 -->
      <button data-testid="send-button">      <!-- 发送按钮 -->
```

### 2. ConversationList 组件
对话列表组件测试属性：
```html
<div data-testid="conversation-list">          <!-- 对话列表容器 -->
  <button data-testid="new-conversation-button"> <!-- 新建对话按钮 -->
  <div data-testid="conversations-container">   <!-- 对话列表容器 -->
    <button 
      data-testid="conversation-${id}"         <!-- 单个对话项 -->
      data-conversation-id="${id}"             <!-- 对话ID -->
      data-is-current="true/false"             <!-- 当前选中状态 -->
    >
```

### 3. MessageItem 组件
消息项组件测试属性：
```html
<div 
  data-testid="message-${id}"                 <!-- 消息项 -->
  data-message-role="${role}"                 <!-- 消息角色 -->
  data-message-id="${id}"                     <!-- 消息ID -->
>
  <div data-testid="assistant-avatar">        <!-- 助手头像 -->
  <div data-testid="user-avatar">            <!-- 用户头像 -->
  <div data-testid="message-content">        <!-- 消息内容容器 -->
    <div data-testid="message-text">         <!-- 消息文本 -->
    <div data-testid="message-timestamp">    <!-- 消息时间戳 -->
```

### 4. ChatContainer 组件
聊天容器组件测试属性：
```html
<div data-testid="chat-container">            <!-- 整个聊天容器 -->
  <div data-testid="chat-main">              <!-- 主聊天区域 -->
    <div data-testid="chat-header">          <!-- 聊天头部 -->
    <div data-testid="error-alert">          <!-- 错误提示 -->
    <div data-testid="messages-scroll-area"> <!-- 消息滚动区域 -->
      <div data-testid="empty-messages">     <!-- 空消息提示 -->
      <div data-testid="loading-indicator">  <!-- 加载指示器 -->
    <div data-testid="chat-input-area">      <!-- 输入区域 -->
      <form data-testid="chat-form">         <!-- 消息表单 -->
        <input data-testid="message-input">  <!-- 消息输入框 -->
        <button data-testid="send-button">   <!-- 发送按钮 -->
```

## 测试最佳实践

### 1. 元素选择策略
- 使用 `data-testid` 作为主要的选择器
- 避免使用样式类名或其他不稳定的属性
- 使用额外的数据属性（如 `data-conversation-id`）来帮助验证状态

### 2. 测试独立性
- 每个测试应该是独立的
- 测试之间不应该相互依赖
- 每个测试后清理测试数据

### 3. 断言
- 使用显式等待来处理动态内容
- 确保断言具体且有意义
- 包含正面和负面的断言

### 4. 错误处理
- 添加适当的错误消息
- 优雅地处理超时
- 记录相关信息以便调试

## 常见问题和解决方案

### 1. 时序问题
- 使用 `expect` 配合适当的超时时间
- 等待特定条件而不是固定延迟
- 使用 `networkidle` 等状态来确保数据加载完成

### 2. 状态管理
- 测试间清理应用状态
- 使用隔离的测试数据
- 实现适当的清理机制

## 维护指南

### 添加新测试
1. 如果测试新功能，创建新的测试文件
2. 更新知识库，添加新的测试模式
3. 记录新的选择器或模式

### 更新测试
1. 保持选择器的最新状态
2. 更新文档以反映测试模式的变化
3. 尽可能保持向后兼容性 