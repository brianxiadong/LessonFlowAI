#!/bin/bash
# LessonFlowAI 环境初始化脚本

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_NAME="lessonflow_env"
VENV_PATH="$PROJECT_ROOT/.venv/$VENV_NAME"

echo "🚀 LessonFlowAI 环境初始化"
echo "================================"

# 1. 创建虚拟环境目录
mkdir -p "$PROJECT_ROOT/.venv"

# 2. 检查/创建虚拟环境
if [ -d "$VENV_PATH" ]; then
    echo "✅ 虚拟环境已存在: $VENV_PATH"
else
    echo "📦 创建虚拟环境: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
    echo "✅ 虚拟环境创建成功"
fi

# 3. 激活虚拟环境
echo "🔄 激活虚拟环境..."
source "$VENV_PATH/bin/activate"

# 4. 升级 pip
echo "📦 升级 pip..."
pip install --upgrade pip -q

# 5. 安装核心依赖
echo "📦 安装核心依赖..."
pip install manim moviepy pillow requests -q

# 6. 验证安装
echo ""
echo "🔍 验证安装..."
python -c "import manim; print(f'  ✅ manim {manim.__version__}')"
python -c "import moviepy; print(f'  ✅ moviepy {moviepy.__version__}')"
python -c "import PIL; print(f'  ✅ pillow {PIL.__version__}')"

echo ""
echo "================================"
echo "✅ 环境初始化完成！"
echo ""
echo "使用方法："
echo "  source $VENV_PATH/bin/activate"
echo ""
echo "或者运行命令时指定 Python:"
echo "  $VENV_PATH/bin/python your_script.py"
