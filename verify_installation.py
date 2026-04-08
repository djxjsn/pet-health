
import sys
import io
from importlib.metadata import version

# 解决Windows中文编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== Python环境 ===")
print(f"Python版本: {sys.version}")
print()

print("=== 核心依赖检查 ===")

packages = [
    ("langchain", "langchain"),
    ("langchain-core", "langchain_core"),
    ("langchain-openai", "langchain_openai"),
    ("langchain-community", "langchain_community"),
    ("langchain-text-splitters", "langchain_text_splitters"),
    ("langchain-classic", "langchain_classic"),
    ("langgraph", "langgraph"),
    ("openai", "openai"),
    ("python-dotenv", "dotenv")
]

for pkg_name, module_name in packages:
    try:
        __import__(module_name)
        ver = version(pkg_name)
        print(f"[OK] {pkg_name}: {ver}")
    except ImportError as e:
        print(f"[FAIL] {pkg_name} 导入失败: {e}")
    except Exception as e:
        print(f"[WARN] {pkg_name}: 无法获取版本 - {e}")

print()
print("=== 安装验证完成 ===")
print("所有依赖检查完毕！")


