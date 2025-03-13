# AI Development Knowledge Base

## 前后端集成最佳实践

### 1. 服务启动顺序和依赖管理

**问题**: 前端启动时后端未就绪导致连接错误。

**解决方案**:
```bash
# 健康检查模式
wait_for_service() {
    max_attempts=60
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        # 检查进程是否存活
        if ! ps -p $PID > /dev/null; then
            echo "Service process died"
            return 1
        fi
        
        # 检查服务是否可用
        if curl -s http://localhost:port/health > /dev/null 2>&1; then
            echo "Service is ready"
            return 0
        fi
        
        attempt=$((attempt+1))
        sleep 1
    done
    return 1
}
```

### 2. Vite 开发代理配置

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: (proxy) => {
          // 错误处理
          proxy.on('error', (err) => {
            console.log('Proxy error:', err);
          });
          
          // 请求日志
          proxy.on('proxyReq', (_proxyReq, req) => {
            console.log('Sending Request:', req.method, req.url);
          });
        }
      }
    }
  }
});
```

## Shell 脚本最佳实践

### 1. 进程管理
```bash
# 启动和清理模式
start_process() {
    command &  # 后台运行
    PROCESS_PID=$!  # 存储PID
}

cleanup() {
    if [ -n "$PID" ]; then
        kill $PID 2>/dev/null || true
    fi
}

trap cleanup SIGINT SIGTERM  # 处理终止信号
```

### 2. 目录管理
```bash
# 使用脚本位置的绝对路径
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR"

# 保存和恢复工作目录
CURRENT_DIR=$(pwd)
cd /target/path
# 执行操作
cd "$CURRENT_DIR"
```

### 3. 错误处理
```bash
# 错误处理选项
set -e  # 出错时退出
set -u  # 使用未定义变量时退出
set -o pipefail  # 管道失败时退出

# 优雅地处理错误
if ! command; then
    echo "Error: command failed"
    cleanup
    exit 1
fi
```

## 调试和监控

### 1. 常用调试命令
```bash
# 检查进程
ps -p $PID

# 检查端口占用
lsof -i :8000

# 实时查看日志
tail -f logfile

# 检查网络连接
curl -v http://localhost:8000
```

### 2. 日志最佳实践
```bash
# 使用不同日志级别
log_error() { echo "ERROR: $*" >&2; }
log_info() { echo "INFO: $*"; }
log_debug() { [[ $DEBUG ]] && echo "DEBUG: $*"; }
```

## 安全注意事项

- 使用环境变量管理敏感配置
- 实现适当的CORS策略
- 避免以root身份运行进程
- 正确处理API密钥和敏感信息 