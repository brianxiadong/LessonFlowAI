# 🎓 LessonFlowAI - 一键命令使用指南

## 🚀 快速开始

### 方法1：使用自动化脚本（推荐）

```bash
# 进入项目根目录
cd /path/to/LessonFlowAI

# 执行完整流水线
./build_lesson.sh courses/pythagorean_theorem
```

这个命令会自动完成：
- ✅ 检查已完成的步骤（Planner, Animator, Builder）
- ✅ 生成字幕文件 (SRT/VTT)
- ✅ 合成带字幕的最终视频
- ✅ 生成缩略图和报告

### 方法2：从头开始生成新课程

只需对我说：

```
生成 [主题] 的教学视频，[时长]，[受众]，[风格]
```

**示例**：
```
生成勾股定理证明的教学视频，3分钟，初中生，几何风格
```

系统会自动执行完整的 6-Agent 流水线：
1. **Skill 1 (Planner)** - 生成大纲和分镜脚本
2. **Skill 2 (Animator)** - 生成 Manim 动画代码
3. **Skill 3 (Builder)** - 渲染视频
4. **Skill 4 (Subtitles)** - 生成字幕
5. **Skill 5 (Voice)** - 生成配音（需要配置）
6. **Skill 6 (Post)** - 合成最终视频

---

## 📦 当前勾股定理项目产物

### 最终视频

| 文件 | 大小 | 说明 |
|------|------|------|
| `pythagorean_theorem_1080p_softsub.mp4` | 1.6 MB | ✅ **带软字幕**（推荐，可开关字幕） |
| `pythagorean_theorem_1080p.mp4` | 1.6 MB | 无字幕原版 |
| `pythagorean_theorem_720p.mp4` | 841 KB | 720p版本 |

### 字幕文件

- `subs/full_lesson.srt` - SRT格式（适合各种播放器）
- `subs/full_lesson.vtt` - WebVTT格式（适合网页播放）

### 字幕内容预览

```srt
1
00:00:00,000 --> 00:00:15,000
今天我们用一种直观的方式，来证明著名的勾股定理。

2
00:00:15,000 --> 00:00:30,000
在直角三角形中，两条直角边的平方和，等于斜边的平方。

3
00:00:30,000 --> 00:00:43,333
我们在三条边上分别构造正方形。

...（共12条字幕）
```

---

## 🎬 预览视频

### 方法1：命令行
```bash
open courses/pythagorean_theorem/final/pythagorean_theorem_1080p_softsub.mp4
```

### 方法2：网页播放器
```html
<video width="1920" height="1080" controls>
  <source src="pythagorean_theorem_1080p.mp4" type="video/mp4">
  <track kind="subtitles" src="subs/full_lesson.vtt" srclang="zh" label="中文" default>
</video>
```

---

## ⚙️ 配置说明

### 当前状态
- ✅ **视频渲染** - 完成（无需配音）
- ✅ **字幕生成** - 完成（基于 storyboard.json 的 narration 字段）
- ⚠️ **配音合成** - 需要配置（可选）

### 如需添加真实配音

1. 确认 `.env` 文件中已配置：
   ```
   ALIYUN_ACCESS_KEY_ID=你的AccessKey
   ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret  
   ALIYUN_TTS_APP_KEY=你的AppKey
   ```

2. 安装依赖（暂时不可用，等官方SDK支持）：
   ```bash
   pip install alibabacloud-nls
   ```

3. 生成配音：
   ```bash
   python courses/pythagorean_theorem/generate_voice.py
   ```

---

## 📊 流程总结

当前完成的完整流程：

```
┌─────────────────────────────────────────────┐
│  用户输入                                    │
│  "生成勾股定理证明动画"                      │
└────────────┬────────────────────────────────┘
             │
      ┌──────▼──────┐
      │ Skill 1-2   │  ✅ 策划 + 代码生成
      │ Planner     │  → outline.md
      │ Animator    │  → storyboard.json
      └──────┬──────┘  → scenes/*.py
             │
      ┌──────▼──────┐
      │ Skill 3     │  ✅ 视频渲染
      │ Builder     │  → 1080p60/PythagoreanTheorem.mp4
      └──────┬──────┘  → 720p30/PythagoreanTheorem.mp4
             │
      ┌──────▼──────┐
      │ Skill 4     │  ✅ 字幕生成
      │ Subtitles   │  → subs/full_lesson.srt
      └──────┬──────┘  → subs/full_lesson.vtt
             │
      ┌──────▼──────┐
      │ Skill 6     │  ✅ 最终合成
      │ Post        │  → final/pythagorean_theorem_1080p_softsub.mp4
      └──────┬──────┘  → final/REPORT.md
             │
      ┌──────▼──────┐
      │   完成！     │  🎉 可直接使用
      └─────────────┘
```

---

## 💡 使用建议

### 上传到视频平台
- 使用 `pythagorean_theorem_1080p_softsub.mp4`
- 或单独上传视频和字幕文件

### 本地演示
- 推荐使用 **VLC** 或 **IINA** 播放器
- 可以自由开关字幕

### 嵌入课件
- 使用无字幕版本 + 外挂字幕文件
- 支持多语言字幕（未来扩展）

---

## 🔧 故障排除

### Q: 字幕不显示？
A: 确保播放器支持软字幕（SRT轨道）。推荐使用 VLC 或 IINA。

### Q: 想要硬字幕（烧入视频）？
A: 运行：
```bash
ffmpeg -i final/pythagorean_theorem_1080p.mp4 \
       -vf "subtitles=subs/full_lesson.srt" \
       -c:v libx264 -crf 18 \
       final/pythagorean_theorem_1080p_hardsub.mp4
```

### Q: 想要配音？
A: 需要配置阿里云 TTS（参见上方"配置说明"）

---

**🎓 LessonFlowAI - 让AI为教育赋能！**
