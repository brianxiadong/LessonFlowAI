---
name: manim-animator
description: 根据分镜脚本生成可运行的 Manim Python 代码
---

# Manim 代码生成 Skill (Animator)

## 概述

此 Skill 负责将分镜脚本 (storyboard.json) 转换为可执行的 Manim Python 代码。每个 Scene 生成一个独立的 Python 文件，便于独立渲染和错误定位。

## 触发条件

- 前置条件：`storyboard.json` 已存在且通过验证
- 触发方式：
  - 自动：Orchestrator 调用
  - 手动：用户说 "生成动画代码" / "运行 animator"

## 输入

- `courses/[lesson_id]/storyboard.json` - 分镜脚本
- `courses/[lesson_id]/style_guide.json` - 风格配置（可选，使用默认）
- `templates/manim_snippets/` - 代码模板库

## 输出

```
courses/[lesson_id]/
  scenes/
    scene_001.py
    scene_002.py
    ...
    __init__.py
```

## 执行步骤

### 步骤 1：加载分镜脚本

```python
import json
from pathlib import Path

lesson_path = Path("courses/[lesson_id]")
storyboard = json.loads((lesson_path / "storyboard.json").read_text())
```

### 步骤 2：加载风格配置

如果存在 `style_guide.json`，加载自定义风格；否则使用 storyboard.meta.style 对应的预设。

### 步骤 3：为每个 Scene 生成代码

**生成规则**：

1. **类命名**：`Scene001`, `Scene002`... 或使用 scene.id 转换
2. **继承基类**：使用 `GridLayoutScene` 确保网格布局
3. **元素创建**：按 visual.elements 顺序创建
4. **动画执行**：按 animation.steps 顺序播放
5. **时长控制**：确保总动画时长 ≈ scene.duration_s

**代码模板**：

```python
"""
LessonFlowAI 自动生成
Scene: {scene_id}
Duration: {duration_s}s
"""

from manim import *
import sys
sys.path.insert(0, "{project_root}/templates/manim_snippets")

from base.grid_layout import GridLayoutScene
from base.style_mixin import StyleMixin, STYLE_PRESETS


class {class_name}(GridLayoutScene, StyleMixin):
    """
    {scene_description}
    """
    
    def setup(self):
        super().setup()
        self.set_style("{style_name}")
    
    def construct(self):
        # ========== 元素创建 ==========
        {element_creation_code}
        
        # ========== 动画序列 ==========
        {animation_code}


# 渲染配置
if __name__ == "__main__":
    scene = {class_name}()
    scene.render()
```

### 步骤 4：元素类型到代码的映射

| DSL type | Manim 代码 |
|----------|-----------|
| text | `self.create_text(content, anchor, element_id, size, color)` |
| formula | `self.create_formula(content, anchor, element_id, size, color)` |
| box | `self.create_box(label, anchor, element_id, color, width, height)` |
| circle | `self.styled_circle(radius, color_name).move_to(anchor_pos)` |
| arrow | `self.create_arrow_between(from_id, to_id, element_id, color, style)` |
| axes | `Axes(...).move_to(anchor_pos)` |

**元素创建代码生成示例**：

输入 DSL：
```json
{
  "type": "text",
  "id": "title",
  "content": "什么是 Attention?",
  "anchor": "top-center",
  "size": "large",
  "color": "WHITE"
}
```

生成代码：
```python
title = self.create_text(
    content="什么是 Attention?",
    anchor="top-center",
    element_id="title",
    size="large",
    color=WHITE
)
```

### 步骤 5：动画动作到代码的映射

| DSL action | Manim 代码 |
|------------|-----------|
| create | `self.play(Create({target}), run_time={duration})` |
| write | `self.play(Write({target}), run_time={duration})` |
| fade_in | `self.play(FadeIn({target}), run_time={duration})` |
| fade_out | `self.play(FadeOut({target}), run_time={duration})` |
| transform | `self.play(Transform({from}, {to}), run_time={duration})` |
| move_to | `self.play({target}.animate.move_to({pos}), run_time={duration})` |
| scale | `self.play({target}.animate.scale({factor}), run_time={duration})` |
| highlight | `self.play(Indicate({target}, color={color}), run_time={duration})` |
| wait | `self.wait({duration})` |

**动画代码生成示例**：

输入 DSL：
```json
{
  "action": "write",
  "target": "title",
  "duration_s": 2
}
```

生成代码：
```python
self.play(Write(self.get_element("title")), run_time=2)
```

**多目标动画**：

输入 DSL：
```json
{
  "action": "fade_in",
  "target": ["box_q", "box_k", "box_v"],
  "duration_s": 1.5
}
```

生成代码：
```python
self.play(
    FadeIn(self.get_element("box_q")),
    FadeIn(self.get_element("box_k")),
    FadeIn(self.get_element("box_v")),
    run_time=1.5
)
```

### 步骤 6：生成场景入口文件

创建 `scenes/__init__.py`：

```python
"""
LessonFlowAI 自动生成的场景模块
课程: {lesson_title}
"""

from .scene_001 import Scene001
from .scene_002 import Scene002
# ...

__all__ = [
    "Scene001",
    "Scene002",
    # ...
]

# 场景顺序（用于批量渲染）
SCENE_ORDER = [
    "Scene001",
    "Scene002",
    # ...
]
```

### 步骤 7：代码语法检查

对每个生成的文件进行语法检查：

```bash
python -m py_compile courses/[lesson_id]/scenes/scene_001.py
```

如果有语法错误，尝试自动修复（最多 3 次）。

## 强制约束

### 布局约束

所有元素必须使用网格锚点，禁止使用绝对坐标：

```python
# ✅ 正确
self.create_text("Hello", anchor="top-center")

# ❌ 禁止
text = Text("Hello").move_to([1.5, 2.3, 0])
```

### 元素数量约束

单个 Scene 元素不超过 12 个。生成代码前检查：

```python
if len(scene["visual"]["elements"]) > 12:
    raise ValueError(f"Scene {scene['id']} 元素数超过限制 (12)")
```

### 时长约束

动画总时长应接近 scene.duration_s：

```python
total_animation_time = sum(step.get("duration_s", 1) for step in steps)
if abs(total_animation_time - scene["duration_s"]) > 2:
    print(f"警告: Scene {scene['id']} 动画时长 ({total_animation_time}s) 与目标时长 ({scene['duration_s']}s) 差异较大")
```

## 增量更新支持

1. 读取 `.build_cache.json` 获取上次构建的 hash
2. 对比每个 scene._hash
3. 仅对 hash 变化的 scene 重新生成代码

```python
# 伪代码
for scene in storyboard["scenes"]:
    cached_hash = build_cache.get(scene["id"], {}).get("hash")
    if scene.get("_hash") != cached_hash:
        generate_scene_code(scene)
        print(f"🔄 重新生成: {scene['id']}")
    else:
        print(f"⏭️ 跳过（未变更）: {scene['id']}")
```

## 输出确认

```
✅ Manim 代码生成完成！
📁 输出目录: courses/lesson_001/scenes/
📄 生成文件:
   - scene_001.py ✅
   - scene_002.py ✅ (新生成)
   - scene_003.py ⏭️ (未变更，跳过)
   - __init__.py ✅

下一步: 运行 Skill 3 (Builder) 编译渲染
```

## 常见模式代码示例

### 模式 1：公式推导

```python
# 继承公式推导模板
from patterns.formula_derivation import FormulaDerivationScene

class Scene001(FormulaDerivationScene):
    def construct(self):
        step1 = self.create_formula_step(r"E = mc^2", "middle-center", "step1")
        self.play(Write(step1))
        # ...
```

### 模式 2：流程图

```python
from patterns.flowchart import FlowchartScene

class Scene002(FlowchartScene):
    def construct(self):
        input_node = self.create_node("输入", "top-center", "input")
        output_node = self.create_node("输出", "bottom-center", "output")
        self.play(FadeIn(input_node), FadeIn(output_node))
        
        arrow = self.connect_nodes("input", "output", "arrow1")
        self.play(Create(arrow))
```

### 模式 3：对比图

```python
from patterns.comparison import ComparisonScene

class Scene003(ComparisonScene):
    def construct(self):
        title = self.create_comparison_title("方法A", "方法B")
        self.play(Write(title))
        # ...
```

## 错误处理

如果代码生成失败：
1. 记录错误到 `logs/animator_error.log`
2. 输出具体的 scene_id 和错误信息
3. 建议用户检查 storyboard.json 中该 scene 的定义

```
❌ 代码生成失败
Scene: scene_003
错误: 元素 'arrow_ab' 引用了不存在的 from: 'box_a'
建议: 检查 storyboard.json 中 scene_003 的 elements 定义
```
