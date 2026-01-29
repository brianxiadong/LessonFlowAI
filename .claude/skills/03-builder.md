---
name: manim-builder
description: 编译渲染 Manim 场景，失败时自动修复并重试
---

# 编译与自愈 Skill (Builder)

## 概述

此 Skill 负责执行 Manim 渲染命令，监控编译过程，失败时自动分析错误并进行最小化修复。包含轻量级质量检测（边界盒检查）。

## 触发条件

- 前置条件：`scenes/` 目录下有 Python 文件
- 触发方式：
  - 自动：Orchestrator 调用
  - 手动：用户说 "渲染动画" / "build" / "compile"

## 输入

```
courses/[lesson_id]/
  scenes/
    scene_001.py
    scene_002.py
    ...
```

## 输出

```
courses/[lesson_id]/
  renders/
    scene_001.mp4
    scene_002.mp4
    ...
  logs/
    build.log
    qa_report.json
  patches/           # 如有修复
    scene_001_patch_001.diff
```

## 执行步骤

### 步骤 1：检查渲染环境

```bash
# 检查 Manim 安装
manim --version

# 检查 FFmpeg
ffmpeg -version

# 检查 LaTeX（可选但推荐）
latex --version
```

如果缺少依赖，提示用户安装：
```
❌ 环境检查失败
缺少: FFmpeg
安装命令: brew install ffmpeg (macOS)
```

### 步骤 2：确定渲染队列

根据 `.build_cache.json` 判断哪些 Scene 需要重新渲染：

```python
scenes_to_render = []
for scene_file in scenes_dir.glob("scene_*.py"):
    scene_id = scene_file.stem
    
    # 检查代码文件是否更新
    file_hash = hash_file(scene_file)
    cached_hash = build_cache.get(scene_id, {}).get("code_hash")
    
    if file_hash != cached_hash:
        scenes_to_render.append(scene_file)
```

### 步骤 3：逐个场景渲染

对每个场景执行：

```bash
# 渲染命令
manim -qh --media_dir courses/[lesson_id]/renders \
    courses/[lesson_id]/scenes/scene_001.py Scene001
```

**渲染质量选项**：

| 参数 | 分辨率 | FPS | 用途 |
|------|--------|-----|------|
| -ql | 480p | 15 | 快速预览 |
| -qm | 720p | 30 | 测试 |
| -qh | 1080p | 60 | 生产 |
| -qk | 4K | 60 | 高清 |

### 步骤 4：错误捕获与分析

如果渲染失败，捕获错误输出：

```python
result = subprocess.run(
    ["manim", "-qh", scene_file, class_name],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    error_log = result.stderr
    analyze_and_repair(scene_file, error_log)
```

### 步骤 5：自动修复策略

**错误类型与修复策略**：

| 错误类型 | 识别特征 | 修复策略 |
|----------|----------|----------|
| 语法错误 | `SyntaxError` | 定位行号，尝试修复括号/缩进 |
| 导入错误 | `ImportError`, `ModuleNotFoundError` | 修正导入路径 |
| 属性错误 | `AttributeError` | 检查对象方法名 |
| 类型错误 | `TypeError` | 检查参数类型 |
| 键错误 | `KeyError` | 检查元素 ID 是否注册 |
| LaTeX 错误 | `LaTeX Error` | 检查公式语法 |

**修复流程**：

```
┌─────────────────────────────────────────────────────┐
│                 自动修复流程                         │
├─────────────────────────────────────────────────────┤
│  1. 解析错误信息，提取：                             │
│     - 错误类型                                      │
│     - 错误行号                                      │
│     - 错误上下文                                    │
│                                                     │
│  2. 匹配修复策略                                    │
│                                                     │
│  3. 生成修复补丁（最小改动原则）                     │
│                                                     │
│  4. 应用补丁，保存原文件备份                         │
│                                                     │
│  5. 重新渲染                                        │
│                                                     │
│  6. 如仍失败，重复 1-5（最多 3 次）                  │
│                                                     │
│  7. 3 次后仍失败，报告错误，人工介入                 │
└─────────────────────────────────────────────────────┘
```

**最小改动原则**：

```python
# ❌ 禁止：大幅重写代码
# 原代码
text = Text("Hello")
# 错误修复后
text = Text("Hello", font_size=36, color=WHITE).move_to(ORIGIN)  # 改动过多

# ✅ 正确：仅修复错误点
# 原代码（缺少导入）
# from manim import *  <- 缺失
text = Text("Hello")

# 修复补丁
+ from manim import *
  text = Text("Hello")
```

### 步骤 6：质量检测

渲染成功后，执行轻量级质检：

**边界检查**：

```python
# 在 Scene 渲染结束前调用
bounds_violations = self.check_bounds(margin=0.5)
if bounds_violations:
    print(f"⚠️ 边界警告: {bounds_violations}")
```

**重叠检测**：

```python
overlaps = self.check_overlaps()
if overlaps:
    print(f"⚠️ 重叠警告: {overlaps}")
```

**生成质检报告** (`qa_report.json`)：

```json
{
  "lesson_id": "lesson_001",
  "build_time": "2026-01-29T10:30:00Z",
  "scenes": {
    "scene_001": {
      "status": "success",
      "render_time_s": 12.5,
      "output_file": "renders/scene_001.mp4",
      "qa_checks": {
        "bounds_check": "pass",
        "overlap_check": "pass",
        "duration_actual_s": 10.2
      }
    },
    "scene_002": {
      "status": "success",
      "qa_checks": {
        "bounds_check": "warning",
        "bounds_violations": [
          {"id": "formula_long", "issue": "out_of_right_bound"}
        ],
        "overlap_check": "pass"
      }
    }
  }
}
```

### 步骤 7：更新构建缓存

```python
# 更新 .build_cache.json
build_cache[scene_id] = {
    "code_hash": hash_file(scene_file),
    "render_hash": hash_file(output_video),
    "rendered": True,
    "last_build": datetime.now().isoformat()
}
```

## 渲染脚本

创建辅助脚本 `scripts/render_all.sh`：

```bash
#!/bin/bash
# 批量渲染所有场景

LESSON_DIR=$1
QUALITY=${2:-h}  # 默认高清

if [ -z "$LESSON_DIR" ]; then
    echo "Usage: render_all.sh <lesson_dir> [quality]"
    exit 1
fi

SCENES_DIR="$LESSON_DIR/scenes"
RENDERS_DIR="$LESSON_DIR/renders"
LOG_FILE="$LESSON_DIR/logs/build.log"

mkdir -p "$RENDERS_DIR"
mkdir -p "$(dirname $LOG_FILE)"

echo "========== 开始渲染 ==========" | tee -a "$LOG_FILE"
echo "时间: $(date)" | tee -a "$LOG_FILE"
echo "质量: -q$QUALITY" | tee -a "$LOG_FILE"

for scene_file in "$SCENES_DIR"/scene_*.py; do
    filename=$(basename "$scene_file" .py)
    classname=$(echo "$filename" | sed 's/scene_/Scene/' | sed 's/_//g')
    
    echo "渲染: $filename -> $classname" | tee -a "$LOG_FILE"
    
    manim -q$QUALITY --media_dir "$RENDERS_DIR" \
        "$scene_file" "$classname" 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ $filename 渲染成功" | tee -a "$LOG_FILE"
    else
        echo "❌ $filename 渲染失败" | tee -a "$LOG_FILE"
    fi
done

echo "========== 渲染完成 ==========" | tee -a "$LOG_FILE"
```

## 错误修复示例

### 示例 1：缺少导入

**错误**：
```
NameError: name 'Circle' is not defined
```

**分析**：`Circle` 是 Manim 对象，缺少导入

**补丁**：
```diff
+ from manim import *
  
  class Scene001(GridLayoutScene):
```

### 示例 2：元素 ID 未注册

**错误**：
```
KeyError: Element 'box_a' not found. Available: ['title', 'subtitle']
```

**分析**：尝试访问未注册的元素

**补丁**：
```diff
  def construct(self):
      title = self.create_text("Title", "top-center", "title")
+     box_a = self.create_box("A", "middle-left", "box_a")
      
      arrow = self.create_arrow_between("title", "box_a")
```

### 示例 3：LaTeX 公式错误

**错误**：
```
LaTeX Error: Missing $ inserted
```

**分析**：公式语法错误

**补丁**：
```diff
- formula = MathTex(r"E = mc^2 \text{能量公式}")
+ formula = MathTex(r"E = mc^2 \quad \text{能量公式}")
```

## 输出确认

```
✅ 渲染完成！
📁 输出目录: courses/lesson_001/renders/
📹 视频文件:
   - scene_001.mp4 ✅ (10.2s, 1080p)
   - scene_002.mp4 ✅ (12.5s, 1080p)
   - scene_003.mp4 ⚠️ (8.1s, 有边界警告)

📊 质检报告: logs/qa_report.json
   - 边界检查: 2 通过, 1 警告
   - 重叠检测: 3 通过

🔧 修复记录: 1 个自动修复
   - scene_002.py: 修复导入错误 (patch_001)

下一步: 运行 Skill 4 (Subtitles) 生成字幕
```

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| FFmpeg 未找到 | 未安装或不在 PATH | `brew install ffmpeg` |
| LaTeX 编译超时 | 公式过于复杂 | 简化公式或分步显示 |
| 内存不足 | 场景元素过多 | 减少单场景元素数 |
| 渲染速度慢 | 分辨率过高 | 开发时用 `-ql` |
