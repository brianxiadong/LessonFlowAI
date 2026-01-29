---
name: subtitle-generator
description: 根据 TTS 时间戳生成精确对齐的字幕文件
---

# 字幕生成 Skill (Subtitles)

## 概述

此 Skill 负责生成与配音精确对齐的字幕文件。利用阿里云 TTS 的字级时间戳能力，实现字幕与语音的精准同步。

## 触发条件

- 前置条件：Skill 5 (Voice) 已执行，生成了音频和时间戳
- 或：用户提供 storyboard.json 中的 narration 文本（基于估算）

## 输入

```
courses/[lesson_id]/
  storyboard.json           # 旁白文本
  audio/
    scene_001.wav
    scene_001_timestamps.json  # 阿里云 TTS 输出的时间戳
```

## 输出

```
courses/[lesson_id]/
  subs/
    scene_001.srt           # SubRip 格式
    scene_001.vtt           # WebVTT 格式
    full_lesson.srt         # 完整课程字幕
```

## 执行步骤

### 步骤 1：读取时间戳数据

阿里云 TTS 返回的时间戳格式：

```json
{
  "payload": {
    "subtitles": [
      {
        "text": "今",
        "begin_time": 0,
        "end_time": 150
      },
      {
        "text": "天",
        "begin_time": 150,
        "end_time": 300
      },
      {
        "text": "我们",
        "begin_time": 300,
        "end_time": 600
      }
    ]
  }
}
```

### 步骤 2：字幕分组策略

将字级时间戳合并为句子级字幕：

**分组规则**：
1. 以标点符号（。！？，；）为分割点
2. 单条字幕不超过 20 个字符
3. 单条字幕时长 2-6 秒
4. 避免在词语中间断开

```python
def group_subtitles(word_timestamps: list, max_chars: int = 20) -> list:
    """将字级时间戳合并为句级字幕"""
    subtitles = []
    current_text = ""
    current_start = None
    
    for word in word_timestamps:
        if current_start is None:
            current_start = word["begin_time"]
        
        current_text += word["text"]
        
        # 检查是否需要断句
        should_break = (
            word["text"] in "。！？，；" or
            len(current_text) >= max_chars
        )
        
        if should_break:
            subtitles.append({
                "text": current_text.strip(),
                "start_ms": current_start,
                "end_ms": word["end_time"]
            })
            current_text = ""
            current_start = None
    
    # 处理剩余文本
    if current_text:
        subtitles.append({
            "text": current_text.strip(),
            "start_ms": current_start,
            "end_ms": word_timestamps[-1]["end_time"]
        })
    
    return subtitles
```

### 步骤 3：生成 SRT 格式

```
1
00:00:00,000 --> 00:00:02,500
今天我们来学习 Attention 机制

2
00:00:02,800 --> 00:00:05,200
它是 Transformer 的核心组件
```

**SRT 格式规范**：
- 序号从 1 开始
- 时间格式：`HH:MM:SS,mmm`（毫秒用逗号分隔）
- 每条字幕后空一行

```python
def format_srt_time(ms: int) -> str:
    """毫秒转 SRT 时间格式"""
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def generate_srt(subtitles: list) -> str:
    """生成 SRT 字幕内容"""
    lines = []
    for i, sub in enumerate(subtitles, 1):
        lines.append(str(i))
        lines.append(f"{format_srt_time(sub['start_ms'])} --> {format_srt_time(sub['end_ms'])}")
        lines.append(sub["text"])
        lines.append("")
    return "\n".join(lines)
```

### 步骤 4：生成 VTT 格式

```
WEBVTT

00:00:00.000 --> 00:00:02.500
今天我们来学习 Attention 机制

00:00:02.800 --> 00:00:05.200
它是 Transformer 的核心组件
```

**VTT 与 SRT 的区别**：
- 开头有 `WEBVTT` 标记
- 时间格式用点号 `.` 而非逗号
- 无序号

### 步骤 5：字幕样式支持（可选）

VTT 支持样式标签：

```vtt
WEBVTT

STYLE
::cue {
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 1.2em;
}

::cue(.highlight) {
  color: #ffb74d;
}

00:00:00.000 --> 00:00:02.500
今天我们来学习 <c.highlight>Attention</c> 机制
```

### 步骤 6：合并完整课程字幕

将所有场景的字幕合并，计算时间偏移：

```python
def merge_scene_subtitles(scenes: list, scene_durations: dict) -> list:
    """合并多场景字幕，计算时间偏移"""
    merged = []
    time_offset = 0
    
    for scene_id in scenes:
        scene_subs = load_subtitles(f"subs/{scene_id}.json")
        
        for sub in scene_subs:
            merged.append({
                "text": sub["text"],
                "start_ms": sub["start_ms"] + time_offset,
                "end_ms": sub["end_ms"] + time_offset
            })
        
        time_offset += scene_durations[scene_id] * 1000
    
    return merged
```

### 步骤 7：字幕校验

检查常见问题：

```python
def validate_subtitles(subtitles: list) -> list:
    """校验字幕并返回问题列表"""
    issues = []
    
    for i, sub in enumerate(subtitles):
        # 检查时长
        duration = sub["end_ms"] - sub["start_ms"]
        if duration < 500:
            issues.append(f"字幕 {i+1} 时长过短 ({duration}ms)")
        if duration > 8000:
            issues.append(f"字幕 {i+1} 时长过长 ({duration}ms)")
        
        # 检查字符数
        if len(sub["text"]) > 30:
            issues.append(f"字幕 {i+1} 字符过多 ({len(sub['text'])}字)")
        
        # 检查重叠
        if i > 0:
            prev_end = subtitles[i-1]["end_ms"]
            if sub["start_ms"] < prev_end:
                issues.append(f"字幕 {i} 与 {i+1} 时间重叠")
    
    return issues
```

## 无时间戳时的估算策略

如果 TTS 未提供时间戳（fallback 方案）：

```python
def estimate_subtitle_timing(text: str, start_time: float, speech_rate: float = 4.0) -> list:
    """
    估算字幕时间轴
    speech_rate: 每秒字数（中文约 3-5 字/秒）
    """
    # 按标点分句
    sentences = re.split(r'[。！？，；]', text)
    
    subtitles = []
    current_time = start_time
    
    for sentence in sentences:
        if not sentence.strip():
            continue
        
        duration = len(sentence) / speech_rate
        
        subtitles.append({
            "text": sentence.strip(),
            "start_ms": int(current_time * 1000),
            "end_ms": int((current_time + duration) * 1000)
        })
        
        current_time += duration + 0.3  # 0.3s 间隔
    
    return subtitles
```

## 输出确认

```
✅ 字幕生成完成！
📁 输出目录: courses/lesson_001/subs/
📄 字幕文件:
   - scene_001.srt (5 条字幕, 10.2s)
   - scene_001.vtt (5 条字幕)
   - scene_002.srt (8 条字幕, 12.5s)
   - scene_002.vtt (8 条字幕)
   - full_lesson.srt (32 条字幕, 180s)

✅ 校验通过: 无时间重叠, 无超长字幕

下一步: 运行 Skill 6 (Post) 合成最终视频
```
