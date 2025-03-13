# TTC Agent UI 测试框架

这个目录包含了TTC Agent的UI测试框架，用于自动化测试前端界面的功能。

## 特性

- **详细日志记录**：每次测试运行都会生成详细的日志，记录测试的每一步操作和结果
- **截图捕获**：在测试的关键步骤和错误发生时自动捕获截图
- **HTML报告**：生成美观的HTML报告，包含测试结果、步骤、截图和错误信息
- **智能报告命名**：报告文件名包含时间戳、测试结果摘要和测试用例数量，便于快速识别
- **独立测试运行目录**：每次测试运行都会创建一个独立的目录，包含所有相关的日志、截图和报告
- **页面对象模式**：使用页面对象模式组织测试代码，提高可维护性和可读性

## 目录结构

```
ttc_agent/tests/ui/
├── __init__.py           # 使UI测试目录成为一个Python包
├── test_utils.py         # 测试工具模块，包含日志、报告和截图功能
├── test_conversation.py  # 会话功能的UI测试
└── README.md             # 本文档
```

每次测试运行会在项目根目录下创建一个新的`test_results`目录，结构如下：

```
test_results/
└── run_YYYYMMDD_HHMMSS/  # 测试运行时间戳
    ├── logs/             # 日志文件
    │   └── test.log      # 详细日志
    ├── reports/          # 测试报告
    │   ├── assets/       # 报告资源文件（截图副本）
    │   │   ├── page-loaded-0.png
    │   │   ├── test-start-0.png
    │   │   └── ...
    │   ├── report.html                                # 固定名称的HTML报告（最新结果）
    │   ├── report_YYYYMMDD_HHMMSS_PASS_10cases.html   # 带时间戳和结果摘要的HTML报告（通过示例）
    │   ├── report_YYYYMMDD_HHMMSS_FAIL_2_10cases.html # 带时间戳和结果摘要的HTML报告（失败示例）
    │   └── report.json                                # JSON格式报告
    └── screenshots/      # 原始截图
        ├── page-loaded-0.png
        ├── test-start-0.png
        └── ...
```

## 运行测试

使用提供的脚本运行UI测试：

```bash
./run_ui_tests.sh
```

这个脚本会：
1. 检查环境变量和依赖
2. 启动后端和前端服务
3. 运行UI测试
4. 生成测试报告
5. 清理服务

### 手动运行测试

如果你想手动运行测试，可以使用以下命令：

```bash
# 激活虚拟环境
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac

# 确保后端和前端服务已经启动
# 然后运行测试
python -m pytest ttc_agent/tests/ui/test_conversation.py -v

# 退出虚拟环境
deactivate
```

> **注意**：必须使用 `python -m pytest` 而不是直接使用 `pytest` 命令，以确保Python正确识别包结构。

## 查看测试报告

测试完成后，HTML报告将生成在`test_results/run_YYYYMMDD_HHMMSS/reports/`目录下，有两种格式：

1. **固定名称报告**：`report.html` - 始终是最新的测试结果，便于脚本引用
2. **详细命名报告**：`report_YYYYMMDD_HHMMSS_STATUS_Ncases.html` - 包含以下信息：
   - **时间戳**：测试执行的日期和时间（YYYYMMDD_HHMMSS格式）
   - **测试状态**：
     - `PASS` - 所有测试都通过
     - `FAIL_X` - 有X个测试失败
   - **测试用例数量**：`Ncases` - 表示执行的测试用例总数

例如：
- `report_20230615_143022_PASS_10cases.html` - 2023年6月15日14:30:22执行，所有10个测试用例都通过
- `report_20230616_091545_FAIL_2_8cases.html` - 2023年6月16日09:15:45执行，8个测试用例中有2个失败

这种命名方式使您可以快速识别测试运行的时间和结果，无需打开报告文件即可了解测试状态。

您可以在浏览器中打开HTML报告查看详细的测试结果，包括：

- 测试摘要（通过/失败/总数）
- 每个测试的详细信息（名称、状态、持续时间）
- 测试步骤列表
- 测试过程中捕获的截图
- 错误信息（如果测试失败）

报告中的截图是从原始截图复制到`reports/assets`目录的副本，确保HTML报告可以正确显示它们。

## 编写新的UI测试

### 1. 导入必要的模块

```python
import pytest
from playwright.sync_api import Page
from ttc_agent.tests.ui.test_utils import create_test_run_dir, setup_logger, UITestResult, ReportGenerator
```

### 2. 设置全局变量

```python
# 全局变量
RUN_DIR = create_test_run_dir()
LOGGER = setup_logger(RUN_DIR)
REPORT_GENERATOR = ReportGenerator(RUN_DIR)
```

### 3. 创建页面对象类

```python
class YourPageObject:
    def __init__(self, page: Page):
        self.page = page
        
    def some_action(self):
        LOGGER.info("执行某个动作")
        # 实现动作
        return self
```

### 4. 创建测试夹具

```python
@pytest.fixture
def your_page(page: Page):
    LOGGER.info("设置页面夹具")
    page.goto("http://localhost:5173")
    return YourPageObject(page)
```

### 5. 编写测试函数

```python
def test_some_feature(your_page):
    test_result = UITestResult("test_some_feature", RUN_DIR)
    
    try:
        LOGGER.info("开始测试")
        test_result.add_step("第一步")
        # 测试代码
        
        test_result.add_screenshot("某个状态", your_page.page)
        
        # 更多测试步骤...
        
        test_result.mark_passed()
        
    except Exception as e:
        LOGGER.error(f"测试失败: {str(e)}")
        test_result.mark_failed(str(e))
        test_result.add_screenshot("失败", your_page.page)
        raise
        
    finally:
        REPORT_GENERATOR.add_result(test_result)
        REPORT_GENERATOR.generate_json_report()
        REPORT_GENERATOR.generate_html_report()
```

## 测试工具API

### UITestResult

用于跟踪单个测试的结果。

```python
# 创建测试结果对象
result = UITestResult("测试名称", run_dir)

# 添加测试步骤
result.add_step("步骤描述")

# 添加截图
result.add_screenshot("截图名称", page)

# 标记测试通过
result.mark_passed()

# 标记测试失败
result.mark_failed("错误信息")
```

### ReportGenerator

用于生成测试报告。

```python
# 创建报告生成器
generator = ReportGenerator(run_dir)

# 添加测试结果
generator.add_result(test_result)

# 生成JSON报告
json_path = generator.generate_json_report()

# 生成HTML报告
html_path = generator.generate_html_report()  # 返回详细命名的报告路径
```

## 最佳实践

1. **使用数据测试ID**：使用`data-testid`属性定位元素，而不是依赖CSS类或文本内容
2. **详细记录日志**：使用`LOGGER`记录测试的每一步操作和结果
3. **捕获关键截图**：在测试的关键步骤和错误发生时捕获截图
4. **使用页面对象模式**：将页面操作封装在页面对象类中，提高代码可维护性
5. **适当等待**：使用显式等待而不是固定延时，提高测试稳定性
6. **错误处理**：使用try/except/finally结构处理错误并确保生成报告
7. **保留历史报告**：利用详细命名的报告文件进行测试历史追踪和比较

## 故障排除

如果遇到导入错误，请确保：

1. 所有目录都有 `__init__.py` 文件，使它们成为Python包
2. 使用绝对导入而不是相对导入 (例如 `from ttc_agent.tests.ui.test_utils import ...`)
3. 使用 `python -m pytest` 运行测试，而不是直接使用 `pytest` 命令

### 常见问题

1. **pytest误将工具类识别为测试类**：
   - 避免在非测试类上使用`Test`前缀，因为pytest会尝试将其作为测试类收集
   - 我们的工具类使用`UITestResult`和`ReportGenerator`命名，避免了这个问题

2. **找不到模块**：
   - 确保使用绝对导入路径
   - 确保所有目录都有`__init__.py`文件

3. **测试结果目录不存在**：
   - 确保`create_test_run_dir()`函数使用绝对路径创建目录

4. **HTML报告中看不到截图**：
   - 截图会自动复制到`reports/assets`目录，确保HTML报告可以正确显示它们
   - 如果仍然看不到截图，检查浏览器控制台是否有路径错误 

5. **无法区分不同的测试运行**：
   - 现在报告文件名包含时间戳、测试结果摘要和测试用例数量，便于快速识别不同的测试运行
   - 可以通过文件名快速了解测试状态，无需打开报告文件