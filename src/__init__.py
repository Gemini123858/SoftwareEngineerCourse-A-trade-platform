"""
将此目录标记为一个 Python 包。

添加空的 __init__.py 可让相对导入（例如 `from . import models`）在静态分析器
（Pylance/pyright）和以包方式运行（python -m）时正常工作。

注意：如果你直接使用 `python src/data_manager.py` 运行模块，仍然会因为相对导入失败而报错——
应使用 `python -m src.data_manager` 或从包的顶层导入。
"""

# 这是一个包标记文件，提供更完整的说明和导出列表。
__all__ = ["models", "data_manager", "services", "main"]

# 说明：
# - 推荐使用包运行模块：python3 -m src.main
# - 若编辑器仍报错，可在项目 `.vscode/settings.json` 中添加
#   "python.analysis.extraPaths": ["./src"] 来帮助 Pylance 查找模块。
