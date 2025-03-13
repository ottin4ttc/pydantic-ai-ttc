import os
import time
import logging
import json
import datetime
import shutil
from typing import Dict, Any, List, Optional
from playwright.sync_api import Page

# HTML报告模板
HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UI Test Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .summary {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .summary-box {
            flex: 1;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .summary-box.passed {
            background-color: #e6f7e6;
            border: 1px solid #c3e6cb;
        }
        .summary-box.failed {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        .summary-box.total {
            background-color: #e2e3e5;
            border: 1px solid #d6d8db;
        }
        .summary-box h2 {
            margin-top: 0;
            font-size: 18px;
        }
        .summary-box .count {
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }
        .test-case {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .test-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .test-name {
            font-size: 18px;
            font-weight: bold;
        }
        .test-status {
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        }
        .test-status.pass {
            background-color: #d4edda;
            color: #155724;
        }
        .test-status.fail {
            background-color: #f8d7da;
            color: #721c24;
        }
        .test-details {
            margin-bottom: 15px;
        }
        .test-details p {
            margin: 5px 0;
        }
        .steps-container {
            margin-top: 20px;
        }
        .step {
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-radius: 3px;
            margin-bottom: 10px;
            border-left: 3px solid #6c757d;
        }
        .step-time {
            color: #6c757d;
            font-size: 0.9em;
        }
        .screenshots {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .screenshot {
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }
        .screenshot img {
            width: 100%;
            height: auto;
            display: block;
        }
        .screenshot-caption {
            padding: 10px;
            background-color: #f8f9fa;
            text-align: center;
            font-size: 0.9em;
        }
        .error-container {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        .timestamp {
            color: #6c757d;
            font-size: 0.9em;
        }
        footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #6c757d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>UI Test Report</h1>
        <span class="timestamp">Generated: {{timestamp}}</span>
    </div>
    
    <div class="summary">
        <div class="summary-box passed">
            <h2>Passed</h2>
            <div class="count">{{passed_count}}</div>
        </div>
        <div class="summary-box failed">
            <h2>Failed</h2>
            <div class="count">{{failed_count}}</div>
        </div>
        <div class="summary-box total">
            <h2>Total</h2>
            <div class="count">{{total_count}}</div>
        </div>
    </div>
    
    <div class="test-results">
        {{test_cases}}
    </div>
    
    <footer>
        <p>Test Run Directory: {{run_dir}}</p>
        <p>Generated by TTC Agent UI Test Framework</p>
    </footer>
</body>
</html>
"""

TEST_CASE_TEMPLATE = """
<div class="test-case">
    <div class="test-header">
        <div class="test-name">{{name}}</div>
        <div class="test-status {{status}}">{{status_text}}</div>
    </div>
    
    <div class="test-details">
        <p><strong>Duration:</strong> {{duration}} seconds</p>
        <p><strong>Started:</strong> {{start_time}}</p>
        <p><strong>Finished:</strong> {{end_time}}</p>
    </div>
    
    {{error_section}}
    
    <div class="steps-container">
        <h3>Steps:</h3>
        {{steps}}
    </div>
    
    <div class="screenshots">
        <h3>Screenshots:</h3>
        {{screenshots}}
    </div>
</div>
"""

STEP_TEMPLATE = """
<div class="step">
    <div class="step-time">{{time}}</div>
    <div class="step-description">{{description}}</div>
</div>
"""

SCREENSHOT_TEMPLATE = """
<div class="screenshot">
    <img src="{{path}}" alt="{{name}}">
    <div class="screenshot-caption">{{test_name}} - {{name}}</div>
</div>
"""

ERROR_TEMPLATE = """
<div class="error-container">
    <h3>Error:</h3>
    <pre>{{error_message}}</pre>
</div>
"""

# 创建测试运行目录
def create_test_run_dir() -> str:
    """创建测试运行目录，包含截图和日志子目录"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # 使用绝对路径，确保目录创建在项目根目录下
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    run_dir = os.path.join(project_root, f"test_results/run_{timestamp}")
    
    # 创建目录结构
    os.makedirs(f"{run_dir}/screenshots", exist_ok=True)
    os.makedirs(f"{run_dir}/logs", exist_ok=True)
    os.makedirs(f"{run_dir}/reports", exist_ok=True)
    os.makedirs(f"{run_dir}/reports/assets", exist_ok=True)  # 为报告添加资源目录
    
    return run_dir

# 设置日志
def setup_logger(run_dir: str) -> logging.Logger:
    """设置日志记录器，同时输出到控制台和文件"""
    logger = logging.getLogger("ui_test")
    logger.setLevel(logging.DEBUG)
    
    # 防止重复添加处理程序
    if logger.handlers:
        return logger
    
    # 创建文件处理程序
    log_file = f"{run_dir}/logs/test.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理程序
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化程序
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理程序到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized. Log file: {log_file}")
    return logger

# 测试结果类 - 重命名为UITestResult
class UITestResult:
    """跟踪单个测试的结果"""
    def __init__(self, name: str, run_dir: str):
        self.name = name
        self.run_dir = run_dir
        self.status = "running"  # running, pass, fail
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.error: Optional[str] = None
        self.screenshots: List[Dict[str, str]] = []
        self.steps: List[Dict[str, Any]] = []
    
    def add_step(self, description: str) -> None:
        """添加测试步骤"""
        self.steps.append({
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "description": description
        })
    
    def add_screenshot(self, name: str, page: Page) -> str:
        """添加截图"""
        # 在screenshots目录中保存原始截图
        # 使用测试名称作为前缀，确保不同测试的截图有唯一标识
        test_name_prefix = self.name.replace(" ", "_").lower()
        screenshot_filename = f"{test_name_prefix}_{name}-{len(self.screenshots)}.png"
        screenshot_path = f"{self.run_dir}/screenshots/{screenshot_filename}"
        page.screenshot(path=screenshot_path)
        
        # 同时在reports/assets目录中保存一份副本，用于HTML报告
        assets_dir = f"{self.run_dir}/reports/assets"
        assets_path = f"{assets_dir}/{screenshot_filename}"
        
        # 确保assets目录存在
        os.makedirs(assets_dir, exist_ok=True)
        
        # 复制截图到assets目录
        shutil.copy2(screenshot_path, assets_path)
        
        # 存储相对于reports目录的路径，用于HTML报告
        rel_path = f"assets/{screenshot_filename}"
        self.screenshots.append({
            "name": name,
            "path": rel_path,
            "full_path": screenshot_path  # 保存完整路径，用于其他用途
        })
        return screenshot_path
    
    def mark_passed(self) -> None:
        """标记测试为通过"""
        self.status = "pass"
        self.end_time = time.time()
    
    def mark_failed(self, error: str) -> None:
        """标记测试为失败"""
        self.status = "fail"
        self.end_time = time.time()
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """将测试结果转换为字典"""
        return {
            "name": self.name,
            "status": self.status,
            "start_time": datetime.datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.datetime.fromtimestamp(self.end_time).strftime("%Y-%m-%d %H:%M:%S") if self.end_time else None,
            "duration": round(self.end_time - self.start_time, 2) if self.end_time else None,
            "error": self.error,
            "screenshots": self.screenshots,
            "steps": self.steps
        }

# 测试报告生成器 - 重命名为ReportGenerator
class ReportGenerator:
    """生成测试报告"""
    def __init__(self, run_dir: str):
        self.run_dir = run_dir
        self.results: List[UITestResult] = []
    
    def add_result(self, result: UITestResult) -> None:
        """添加测试结果"""
        self.results.append(result)
    
    def generate_json_report(self) -> str:
        """生成JSON格式的报告"""
        report_data = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "run_dir": self.run_dir,
            "results": [result.to_dict() for result in self.results]
        }
        
        report_path = f"{self.run_dir}/reports/report.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return report_path
    
    def generate_html_report(self) -> str:
        """生成HTML格式的报告"""
        # 计算统计信息
        passed = sum(1 for result in self.results if result.status == "pass")
        failed = sum(1 for result in self.results if result.status == "fail")
        total = len(self.results)
        
        # 生成测试用例HTML
        test_cases_html = ""
        for result in self.results:
            # 生成步骤HTML
            steps_html = ""
            for step in result.steps:
                step_html = STEP_TEMPLATE.replace("{{time}}", step["time"])
                step_html = step_html.replace("{{description}}", step["description"])
                steps_html += step_html
            
            # 生成截图HTML
            screenshots_html = ""
            for screenshot in result.screenshots:
                screenshot_html = SCREENSHOT_TEMPLATE.replace("{{path}}", screenshot["path"])
                screenshot_html = screenshot_html.replace("{{name}}", screenshot["name"])
                screenshot_html = screenshot_html.replace("{{test_name}}", result.name)
                screenshots_html += screenshot_html
            
            # 生成错误部分HTML
            error_section = ""
            if result.error:
                error_section = ERROR_TEMPLATE.replace("{{error_message}}", result.error)
            
            # 生成测试用例HTML
            test_case_html = TEST_CASE_TEMPLATE.replace("{{name}}", result.name)
            test_case_html = test_case_html.replace("{{status}}", result.status)
            test_case_html = test_case_html.replace("{{status_text}}", "PASSED" if result.status == "pass" else "FAILED")
            test_case_html = test_case_html.replace("{{duration}}", str(round(result.end_time - result.start_time, 2) if result.end_time else 0))
            test_case_html = test_case_html.replace("{{start_time}}", datetime.datetime.fromtimestamp(result.start_time).strftime("%Y-%m-%d %H:%M:%S"))
            test_case_html = test_case_html.replace("{{end_time}}", datetime.datetime.fromtimestamp(result.end_time).strftime("%Y-%m-%d %H:%M:%S") if result.end_time else "N/A")
            test_case_html = test_case_html.replace("{{error_section}}", error_section)
            test_case_html = test_case_html.replace("{{steps}}", steps_html)
            test_case_html = test_case_html.replace("{{screenshots}}", screenshots_html)
            
            test_cases_html += test_case_html
        
        # 生成完整的HTML报告
        html_report = HTML_REPORT_TEMPLATE.replace("{{timestamp}}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        html_report = html_report.replace("{{passed_count}}", str(passed))
        html_report = html_report.replace("{{failed_count}}", str(failed))
        html_report = html_report.replace("{{total_count}}", str(total))
        html_report = html_report.replace("{{test_cases}}", test_cases_html)
        html_report = html_report.replace("{{run_dir}}", self.run_dir)
        
        # 创建包含时间戳、测试结果摘要和测试用例数量的报告文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        status_summary = "PASS" if failed == 0 else f"FAIL_{failed}"
        report_filename = f"report_{timestamp}_{status_summary}_{total}cases.html"
        
        # 同时保存一个固定名称的报告（用于脚本引用）和一个详细命名的报告（用于存档）
        report_path = f"{self.run_dir}/reports/report.html"
        detailed_report_path = f"{self.run_dir}/reports/{report_filename}"
        
        with open(report_path, 'w') as f:
            f.write(html_report)
        
        # 复制一份带有详细命名的报告
        with open(detailed_report_path, 'w') as f:
            f.write(html_report)
        
        return detailed_report_path 