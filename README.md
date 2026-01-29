# LessonFlowAI

🎬 AI 驱动的教学视频自动生成系统

通过自然语言描述，自动生成包含 Manim 动画、配音、字幕的完整教学视频。

## 特性

- 🗣️ **自然语言输入**: 描述你想讲解的内容，AI 自动生成完整课程
- 🎨 **Manim 动画**: 使用 ManimCE 生成高质量数学动画
- 🎙️ **智能配音**: 集成阿里云 TTS，支持字级时间戳精准对齐
- 📝 **自动字幕**: 基于配音时间戳自动生成 SRT/VTT 字幕
- 🔄 **增量更新**: 修改部分内容时，只重新生成变更的场景
- 📦 **完整产物**: 输出源码、素材、脚本，可复现可修改

## 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/brianxiadong/LessonFlowAI.git
cd LessonFlowAI

# 安装 Python 依赖
pip install -e .

# 安装 Manim 依赖
brew install ffmpeg  # macOS
# apt install ffmpeg  # Ubuntu
```

### 2. 配置阿里云 TTS（可选）

```bash
export ALIYUN_ACCESS_KEY_ID="your_key_id"
export ALIYUN_ACCESS_KEY_SECRET="your_key_secret"
export ALIYUN_TTS_APP_KEY="your_app_key"
```

### 3. 使用 Claude Skills 生成课程

在 Claude Code 中输入：

```
生成一个讲解 Transformer Attention 的教学视频，3分钟，面向初学者
```

## 架构

LessonFlowAI 采用 6 个串联 Skill 的流水线架构：

```
用户输入 → Planner → Animator → Builder → Voice → Subtitles → Post → 最终视频
              │          │         │        │         │          │
              ▼          ▼         ▼        ▼         ▼          ▼
          outline.md  scene.py  render.mp4  audio.wav  subs.srt  final.mp4
          storyboard.json
```

### Skills 说明

| Skill | 功能 | 输出 |
|-------|------|------|
| **01-planner** | 课程策划 | outline.md, storyboard.json, glossary.json |
| **02-animator** | Manim 代码生成 | scenes/*.py |
| **03-builder** | 渲染与自动修复 | renders/*.mp4, qa_report.json |
| **04-subtitles** | 字幕生成对齐 | subs/*.srt |
| **05-voice** | TTS 配音 | audio/*.wav |
| **06-post** | FFmpeg 合成 | final/*.mp4 |

### 核心 DSL: storyboard.json

分镜脚本是各 Skill 之间的中间表示，定义了：

- 场景列表和时长
- 视觉元素（文本、公式、图形）
- 动画序列
- 旁白文本
- 质量检查规则

详见 [schema/storyboard.schema.json](schema/storyboard.schema.json)

## 目录结构

```
LessonFlowAI/
├── .claude/skills/          # Claude Skills 定义
├── schema/                  # JSON Schema
├── templates/
│   ├── manim_snippets/      # Manim 代码模板
│   ├── style_guides/        # 视觉风格配置
│   └── examples/            # 示例文件
├── scripts/                 # 辅助脚本
├── courses/                 # 生成的课程（输出目录）
└── pyproject.toml
```

## 使用示例

### 完整生成

```
lesson: 傅里叶变换直觉理解，5分钟，大学生，学术风格
```

### 增量修改

```
把第 2 个场景的 Query 方框改成红色
```

### 预览单个场景

```
预览 scene_003
```

## 约束规则

为确保生成质量，系统强制以下约束：

- 每个 Scene 时长: 5-15 秒
- 每个 Scene 元素数: ≤ 12
- 布局: 必须使用 3x3 网格锚点
- 修复策略: 仅允许局部补丁，禁止大改结构

## 技术栈

- **动画引擎**: [ManimCE](https://www.manim.community/)
- **TTS**: 阿里云智能语音交互
- **视频合成**: FFmpeg
- **AI 编排**: Claude Skills

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 验证 storyboard
python scripts/validate_storyboard.py path/to/storyboard.json
```

## License

MIT
