#!/bin/bash

# 存储脚本开始时的目录
INITIAL_DIR=$(pwd)

# 确保在脚本结束时返回初始目录
trap 'cd "$INITIAL_DIR"' EXIT

# 进入脚本所在目录
cd "$(dirname "$0")"

# 检查环境变量
check_env_vars() {
    echo "=== Checking environment variables ==="
    local missing_vars=0
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ OPENAI_API_KEY is not set"
        missing_vars=1
    else
        echo "✓ OPENAI_API_KEY is set"
    fi
    
    if [ -z "$DMX_API_KEY" ]; then
        echo "❌ DMX_API_KEY is not set"
        missing_vars=1
    else
        echo "✓ DMX_API_KEY is set"
    fi
    
    if [ $missing_vars -ne 0 ]; then
        echo "Please set the required environment variables in .env file"
        return 1
    fi
    return 0
}

# 检查必要的命令是否存在
check_dependencies() {
    echo "=== Checking dependencies ==="
    local missing_deps=0
    
    # 检查 curl
    if ! command -v curl &> /dev/null; then
        echo "❌ curl is not installed"
        missing_deps=1
    else
        echo "✓ curl is installed"
    fi
    
    # 检查 python
    if ! command -v python &> /dev/null; then
        echo "❌ python is not installed"
        missing_deps=1
    else
        echo "✓ python is installed"
        echo "Python version: $(python --version)"
    fi
    
    # 检查 node
    if ! command -v node &> /dev/null; then
        echo "❌ node is not installed"
        missing_deps=1
    else
        echo "✓ node is installed"
        echo "Node version: $(node --version)"
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is not installed"
        missing_deps=1
    else
        echo "✓ npm is installed"
        echo "NPM version: $(npm --version)"
    fi
    
    if [ $missing_deps -ne 0 ]; then
        echo "Please install missing dependencies and try again."
        exit 1
    fi
}

# 检查 Python 包依赖
check_python_packages() {
    echo "=== Checking Python packages ==="
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python -m venv .venv
    fi
    
    # 激活虚拟环境
    source .venv/Scripts/activate
    
    # 检查 pyproject.toml 是否存在
    if [ ! -f "pyproject.toml" ]; then
        echo "❌ pyproject.toml not found"
        deactivate
        return 1
    fi
    
    echo "Installing project in development mode..."
    if ! pip install -e ".[uitest]"; then
        echo "❌ Failed to install project dependencies"
        deactivate
        return 1
    fi
    
    echo "Installing playwright browsers..."
    if ! playwright install; then
        echo "❌ Failed to install playwright browsers"
        deactivate
        return 1
    fi
    
    echo "✓ All Python dependencies installed successfully"
    deactivate
    return 0
}

# 启动服务
start_services() {
    echo "=== Starting services ==="
    echo "Starting backend service..."
    
    # 启动后端服务并将输出重定向到日志文件
    python -m ttc_agent.chat_app > backend.log 2>&1 &
    BACKEND_PID=$!
    
    # 等待后端启动
    echo "Waiting for backend to start..."
    local max_attempts=30
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://127.0.0.1:8000/conversations > /dev/null 2>&1; then
            echo "✓ Backend is ready"
            break
        fi
        attempt=$((attempt+1))
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "Still waiting for backend... ($attempt/$max_attempts)"
            echo "Last few lines of backend log:"
            tail -n 5 backend.log
        fi
        # 检查进程是否还在运行
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo "❌ Backend process died. Check backend.log for details:"
            cat backend.log
            return 1
        fi
        sleep 1
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Backend failed to start. Check backend.log for details:"
        cat backend.log
        return 1
    fi
    
    echo "Starting frontend service..."
    cd ttc_agent/react_frontend
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    npm run dev > ../../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ../..
    
    # 等待前端启动
    echo "Waiting for frontend to start..."
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo "✓ Frontend is ready"
            return 0
        fi
        attempt=$((attempt+1))
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "Still waiting for frontend... ($attempt/$max_attempts)"
            echo "Last few lines of frontend log:"
            tail -n 5 frontend.log
        fi
        # 检查进程是否还在运行
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "❌ Frontend process died. Check frontend.log for details:"
            cat frontend.log
            return 1
        fi
        sleep 1
    done
    
    echo "❌ Frontend failed to start. Check frontend.log for details:"
    cat frontend.log
    return 1
}

# 清理函数
cleanup() {
    echo "=== Cleaning up ==="
    if [ -n "$BACKEND_PID" ]; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # 确保所有相关进程都被终止
    echo "Ensuring all services are stopped..."
    pkill -f "ttc_agent.chat_app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    # 清理日志文件
    rm -f backend.log frontend.log
    
    echo "✓ Cleanup complete"
}

# 设置清理陷阱
trap cleanup EXIT INT TERM

# 主流程
main() {
    # 检查环境变量
    if ! check_env_vars; then
        echo "❌ Environment check failed"
        exit 1
    fi
    
    # 检查依赖
    check_dependencies
    
    # 检查 Python 包依赖
    if ! check_python_packages; then
        echo "❌ Failed to install Python packages"
        exit 1
    fi
    
    # 启动服务
    if ! start_services; then
        echo "❌ Failed to start services"
        exit 1
    fi
    
    # 等待额外的时间确保服务完全就绪
    echo "Waiting for services to stabilize..."
    sleep 5
    
    echo "=== Running UI tests ==="
    # 运行测试
    if [ -d ".venv" ]; then
        source .venv/Scripts/activate
        python -m pytest ttc_agent/tests/ui/test_conversation.py -v
        TEST_RESULT=$?
        deactivate
    else
        echo "❌ Virtual environment not found. Please create one with 'python -m venv .venv'"
        TEST_RESULT=1
    fi
    
    if [ $TEST_RESULT -eq 0 ]; then
        echo "✓ Tests completed successfully"
    else
        echo "❌ Tests failed"
    fi
    
    return $TEST_RESULT
}

# 运行主流程
main 