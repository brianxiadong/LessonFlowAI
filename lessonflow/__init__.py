"""
LessonFlowAI - AI 驱动的教学视频自动生成系统

通过自然语言描述，自动生成包含 Manim 动画、配音、字幕的完整教学视频。
"""

__version__ = "0.1.0"
__author__ = "LessonFlowAI Team"

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 模板目录
TEMPLATES_DIR = PROJECT_ROOT / "templates"
SCHEMA_DIR = PROJECT_ROOT / "schema"
COURSES_DIR = PROJECT_ROOT / "courses"
