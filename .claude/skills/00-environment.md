---
name: environment-setup
description: LessonFlowAI 虚拟环境配置和依赖管理
---

# 环境配置 Skill (Environment Setup)

## 概述

此 Skill 负责管理 LessonFlowAI 的 Python 虚拟环境，确保所有依赖正确安装。

## 虚拟环境配置

**环境名称**: `lessonflow_env`
**Python 版本**: >= 3.9
**位置**: 项目根目录下的 `.venv/lessonflow_env`

## 必需依赖

```txt
# 核心依赖
manim>=0.18.0
moviepy>=1.0.0
pillow>=9.0.0
requests>=2.28.0

# 可选依赖（TTS）
# alibabacloud-nls  # 阿里云语音合成（可用 HTTP API 替代）
```

## 执行步骤

### 步骤 1：检查虚拟环境是否存在

```bash
VENV_PATH="$PROJECT_ROOT/.venv/lessonflow_env"

if [ -d "$VENV_PATH" ]; then
    echo "✅ 虚拟环境已存在: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
else
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    pip install --upgrade pip
fi
```

### 步骤 2：安装/检查依赖

```bash
# 检查核心依赖
check_and_install() {
    local package=$1
    if ! python -c "import $package" 2>/dev/null; then
        echo "📦 安装 $package..."
        pip install $package
    else
        echo "✅ $package 已安装"
    fi
}

check_and_install manim
check_and_install moviepy
check_and_install pillow
```

### 步骤 3：完整的环境初始化脚本

在项目根目录创建 `scripts/init_env.sh`:

```bash
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
pip install manim moviepy pillow -q

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
```

### 步骤 4：在其他 Skill 中使用虚拟环境

**方法 A：激活环境后运行**

```bash
source .venv/lessonflow_env/bin/activate
python scripts/your_script.py
```

**方法 B：直接使用虚拟环境的 Python（推荐）**

```bash
.venv/lessonflow_env/bin/python scripts/your_script.py
```

**方法 C：在 Python 脚本中自动检测**

```python
#!/usr/bin/env python3
"""
自动检测并使用 lessonflow_env 虚拟环境
"""
import os
import sys
import subprocess

def ensure_venv():
    """确保在正确的虚拟环境中运行"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_python = os.path.join(project_root, '.venv', 'lessonflow_env', 'bin', 'python')
    
    # 检查是否已在虚拟环境中
    if sys.prefix != sys.base_prefix:
        return True  # 已在某个虚拟环境中
    
    # 如果虚拟环境存在，用它重新执行
    if os.path.exists(venv_python):
        print(f"🔄 切换到虚拟环境: lessonflow_env")
        os.execv(venv_python, [venv_python] + sys.argv)
    
    # 虚拟环境不存在，提示创建
    print("❌ 虚拟环境不存在，请先运行: bash scripts/init_env.sh")
    sys.exit(1)

# 在脚本开头调用
ensure_venv()

# 后续正常导入
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
# ...
```

## 环境变量配置

在 `.env` 文件中可以配置：

```bash
# LessonFlowAI 环境配置
LESSONFLOW_VENV=lessonflow_env
LESSONFLOW_PYTHON=.venv/lessonflow_env/bin/python

# TTS 配置（可选）
ALIYUN_ACCESS_KEY_ID=
ALIYUN_ACCESS_KEY_SECRET=
ALIYUN_TTS_APP_KEY=
```

## 快捷命令

在 `pyproject.toml` 或 shell alias 中定义：

```bash
# ~/.bashrc 或 ~/.zshrc
alias lf-python='.venv/lessonflow_env/bin/python'
alias lf-pip='.venv/lessonflow_env/bin/pip'
alias lf-activate='source .venv/lessonflow_env/bin/activate'
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `No module named 'xxx'` | 运行 `bash scripts/init_env.sh` 重新初始化 |
| 虚拟环境损坏 | 删除 `.venv/lessonflow_env` 后重新创建 |
| Python 版本不对 | 使用 `python3.9 -m venv ...` 指定版本 |
| manim 渲染失败 | 确保安装了 ffmpeg: `brew install ffmpeg` |

## 与其他 Skill 的集成

所有需要 Python 的 Skill 都应该：

1. **优先使用虚拟环境的 Python**：
   ```bash
   .venv/lessonflow_env/bin/python script.py
   ```

2. **脚本开头添加自动环境检测**（推荐）:
   ```python
   #!/usr/bin/env python3
   import os, sys
   
   def ensure_venv():
       if sys.prefix != sys.base_prefix:
           return  # 已在虚拟环境中
       script_dir = os.path.dirname(os.path.abspath(__file__))
       # 根据脚本位置调整路径深度
       project_root = os.path.dirname(os.path.dirname(script_dir))
       venv_python = os.path.join(project_root, '.venv', 'lessonflow_env', 'bin', 'python')
       if os.path.exists(venv_python):
           print("🔄 切换到虚拟环境: lessonflow_env")
           os.execv(venv_python, [venv_python] + sys.argv)
       else:
           print("⚠️ 未找到虚拟环境，请先运行: bash scripts/init_env.sh")
           sys.exit(1)
   
   ensure_venv()
   # 后续正常导入...
   ```

3. **在文档中注明依赖的包**

## 新课程脚本的标准模板

所有在 `courses/[lesson_id]/` 下创建的 Python 脚本应使用此模板开头：

```python
#!/usr/bin/env python3
"""
脚本描述

用法：
  .venv/lessonflow_env/bin/python this_script.py
"""
import os
import sys

def ensure_venv():
    """自动切换到 lessonflow_env 虚拟环境"""
    if sys.prefix != sys.base_prefix:
        return
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    venv_python = os.path.join(project_root, '.venv', 'lessonflow_env', 'bin', 'python')
    if os.path.exists(venv_python):
        print("🔄 切换到虚拟环境: lessonflow_env")
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        print("⚠️ 请先运行: bash scripts/init_env.sh")
        sys.exit(1)

ensure_venv()

# ===== 正常导入 =====
from moviepy import VideoFileClip  # 或其他需要的库
# ...
```
