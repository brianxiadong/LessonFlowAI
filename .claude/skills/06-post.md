---
name: video-post
description: 使用 FFmpeg 合成最终视频，包含音视频混合、字幕嵌入、片头片尾
---

# 合成出片 Skill (Post)

## 概述

此 Skill 负责将渲染好的动画视频、配音、字幕合成为最终教学视频。支持：
- 多场景视频拼接
- 音视频混合
- 字幕嵌入（软字幕/硬烧）
- 片头片尾添加
- 多规格输出（16:9, 9:16）
- 背景音乐混合

## 触发条件

- 前置条件：
  - `renders/` 目录有视频文件
  - `audio/` 目录有音频文件
  - `subs/` 目录有字幕文件
- 触发方式：
  - 自动：Orchestrator 调用
  - 手动：用户说 "合成视频" / "出片" / "post"

## 输入

```
courses/[lesson_id]/
  renders/
    scene_001.mp4
    scene_002.mp4
  audio/
    scene_001.wav
    scene_002.wav
  subs/
    full_lesson.srt
  templates/
    intro.mp4          # 片头（可选）
    outro.mp4          # 片尾（可选）
    bgm.mp3            # 背景音乐（可选）
```

## 输出

```
courses/[lesson_id]/
  final/
    lesson_001_1080p.mp4           # 无字幕版
    lesson_001_1080p_subs.mp4      # 硬烧字幕版
    lesson_001_1080p_soft.mkv      # 软字幕版
    lesson_001_vertical.mp4        # 竖屏版（9:16）
```

## 执行步骤

### 步骤 1：检查 FFmpeg

```bash
ffmpeg -version
```

如未安装：
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

### 步骤 2：拼接场景视频

创建视频列表文件 `concat_list.txt`：

```
file 'renders/scene_001.mp4'
file 'renders/scene_002.mp4'
file 'renders/scene_003.mp4'
```

执行拼接：

```bash
ffmpeg -f concat -safe 0 -i concat_list.txt \
    -c copy \
    final/lesson_raw.mp4
```

### 步骤 3：拼接音频

```bash
ffmpeg -f concat -safe 0 -i audio_list.txt \
    -c:a pcm_s16le \
    final/lesson_audio.wav
```

或使用 Python 拼接：

```python
from pydub import AudioSegment

def concat_audio(audio_files: list, output_path: str):
    """拼接多个音频文件"""
    combined = AudioSegment.empty()
    
    for audio_file in audio_files:
        audio = AudioSegment.from_wav(audio_file)
        combined += audio
    
    combined.export(output_path, format="wav")
```

### 步骤 4：音视频混合

```bash
# 替换原视频音轨
ffmpeg -i final/lesson_raw.mp4 \
    -i final/lesson_audio.wav \
    -c:v copy \
    -c:a aac -b:a 192k \
    -map 0:v:0 -map 1:a:0 \
    -shortest \
    final/lesson_mixed.mp4
```

**参数说明**：
- `-c:v copy`: 视频流直接复制（不重新编码）
- `-c:a aac`: 音频编码为 AAC
- `-b:a 192k`: 音频比特率 192kbps
- `-map 0:v:0`: 使用第一个输入的视频流
- `-map 1:a:0`: 使用第二个输入的音频流
- `-shortest`: 以较短的流为准

### 步骤 5：嵌入字幕

**方式 A：硬烧字幕（视频内嵌）**

```bash
ffmpeg -i final/lesson_mixed.mp4 \
    -vf "subtitles=subs/full_lesson.srt:force_style='FontName=Source Han Sans CN,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2'" \
    -c:v libx264 -preset medium -crf 18 \
    -c:a copy \
    final/lesson_001_1080p_subs.mp4
```

**字幕样式参数**：
- `FontName`: 字体名称
- `FontSize`: 字号
- `PrimaryColour`: 字幕颜色（BGR格式）
- `OutlineColour`: 描边颜色
- `Outline`: 描边宽度
- `MarginV`: 距底部边距

**方式 B：软字幕（可切换）**

```bash
ffmpeg -i final/lesson_mixed.mp4 \
    -i subs/full_lesson.srt \
    -c:v copy -c:a copy \
    -c:s mov_text \
    -metadata:s:s:0 language=chi \
    final/lesson_001_1080p_soft.mp4
```

或输出为 MKV（更好的字幕支持）：

```bash
ffmpeg -i final/lesson_mixed.mp4 \
    -i subs/full_lesson.srt \
    -c:v copy -c:a copy \
    -c:s srt \
    final/lesson_001_1080p_soft.mkv
```

### 步骤 6：添加片头片尾

**创建过渡效果**：

```bash
# 片头 + 主内容 + 片尾 拼接（带淡入淡出）
ffmpeg -i templates/intro.mp4 \
    -i final/lesson_mixed.mp4 \
    -i templates/outro.mp4 \
    -filter_complex "
        [0:v]fade=t=out:st=4:d=1[v0];
        [1:v]fade=t=in:st=0:d=1,fade=t=out:st=178:d=1[v1];
        [2:v]fade=t=in:st=0:d=1[v2];
        [v0][v1][v2]concat=n=3:v=1:a=0[outv];
        [0:a][1:a][2:a]concat=n=3:v=0:a=1[outa]
    " \
    -map "[outv]" -map "[outa]" \
    final/lesson_001_full.mp4
```

### 步骤 7：添加背景音乐（可选）

```bash
# 混合背景音乐（降低 BGM 音量）
ffmpeg -i final/lesson_mixed.mp4 \
    -i templates/bgm.mp3 \
    -filter_complex "
        [1:a]volume=0.1[bgm];
        [0:a][bgm]amix=inputs=2:duration=first[outa]
    " \
    -map 0:v -map "[outa]" \
    -c:v copy -c:a aac \
    final/lesson_001_with_bgm.mp4
```

### 步骤 8：生成竖屏版（9:16）

```bash
# 裁剪为竖屏，添加模糊背景
ffmpeg -i final/lesson_001_1080p.mp4 \
    -filter_complex "
        [0:v]scale=1080:1920:force_original_aspect_ratio=decrease,
        pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,
        setsar=1[v]
    " \
    -map "[v]" -map 0:a \
    -c:v libx264 -preset medium -crf 18 \
    -c:a copy \
    final/lesson_001_vertical.mp4
```

**带模糊背景的竖屏版**：

```bash
ffmpeg -i final/lesson_001_1080p.mp4 \
    -filter_complex "
        [0:v]scale=1080:-1,crop=1080:1920,boxblur=20:5[bg];
        [0:v]scale=-1:1080[fg];
        [bg][fg]overlay=(W-w)/2:(H-h)/2[v]
    " \
    -map "[v]" -map 0:a \
    final/lesson_001_vertical_blur.mp4
```

### 步骤 9：输出多种规格

```python
OUTPUT_FORMATS = {
    "1080p": {
        "resolution": "1920x1080",
        "bitrate": "5M",
        "crf": 18
    },
    "720p": {
        "resolution": "1280x720",
        "bitrate": "3M",
        "crf": 23
    },
    "480p": {
        "resolution": "854x480",
        "bitrate": "1.5M",
        "crf": 28
    }
}

def export_formats(input_video: str, output_dir: str):
    for name, config in OUTPUT_FORMATS.items():
        output_path = f"{output_dir}/lesson_{name}.mp4"
        
        cmd = [
            "ffmpeg", "-i", input_video,
            "-vf", f"scale={config['resolution'].replace('x', ':')}",
            "-c:v", "libx264",
            "-crf", str(config["crf"]),
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
        
        subprocess.run(cmd)
```

### 步骤 10：生成缩略图

```bash
# 提取第 5 秒的帧作为封面
ffmpeg -i final/lesson_001_1080p.mp4 \
    -ss 00:00:05 \
    -vframes 1 \
    final/thumbnail.jpg
```

## 完整合成脚本

```bash
#!/bin/bash
# scripts/compose_final.sh

LESSON_DIR=$1
LESSON_NAME=${2:-lesson}

if [ -z "$LESSON_DIR" ]; then
    echo "Usage: compose_final.sh <lesson_dir> [lesson_name]"
    exit 1
fi

RENDERS_DIR="$LESSON_DIR/renders"
AUDIO_DIR="$LESSON_DIR/audio"
SUBS_DIR="$LESSON_DIR/subs"
FINAL_DIR="$LESSON_DIR/final"

mkdir -p "$FINAL_DIR"

echo "========== 开始合成 =========="

# 1. 创建视频列表
ls -1 "$RENDERS_DIR"/scene_*.mp4 | sed "s/^/file '/" | sed "s/$/'/" > "$LESSON_DIR/concat_video.txt"

# 2. 拼接视频
echo "拼接视频..."
ffmpeg -y -f concat -safe 0 -i "$LESSON_DIR/concat_video.txt" \
    -c copy "$FINAL_DIR/raw.mp4"

# 3. 创建音频列表并拼接
ls -1 "$AUDIO_DIR"/scene_*.wav | sed "s/^/file '/" | sed "s/$/'/" > "$LESSON_DIR/concat_audio.txt"

echo "拼接音频..."
ffmpeg -y -f concat -safe 0 -i "$LESSON_DIR/concat_audio.txt" \
    -c:a pcm_s16le "$FINAL_DIR/audio.wav"

# 4. 混合音视频
echo "混合音视频..."
ffmpeg -y -i "$FINAL_DIR/raw.mp4" -i "$FINAL_DIR/audio.wav" \
    -c:v copy -c:a aac -b:a 192k \
    -map 0:v:0 -map 1:a:0 -shortest \
    "$FINAL_DIR/${LESSON_NAME}_1080p.mp4"

# 5. 硬烧字幕版
if [ -f "$SUBS_DIR/full_lesson.srt" ]; then
    echo "生成字幕版..."
    ffmpeg -y -i "$FINAL_DIR/${LESSON_NAME}_1080p.mp4" \
        -vf "subtitles=$SUBS_DIR/full_lesson.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF,Outline=2'" \
        -c:v libx264 -preset medium -crf 18 \
        -c:a copy \
        "$FINAL_DIR/${LESSON_NAME}_1080p_subs.mp4"
fi

# 6. 生成缩略图
echo "生成缩略图..."
ffmpeg -y -i "$FINAL_DIR/${LESSON_NAME}_1080p.mp4" \
    -ss 00:00:05 -vframes 1 \
    "$FINAL_DIR/thumbnail.jpg"

# 7. 清理临时文件
rm -f "$FINAL_DIR/raw.mp4" "$FINAL_DIR/audio.wav"
rm -f "$LESSON_DIR/concat_video.txt" "$LESSON_DIR/concat_audio.txt"

echo "========== 合成完成 =========="
echo "输出文件:"
ls -la "$FINAL_DIR"
```

## 输出确认

```
✅ 视频合成完成！
📁 输出目录: courses/lesson_001/final/
📹 视频文件:
   - lesson_001_1080p.mp4 (180s, 1920x1080, 45MB)
   - lesson_001_1080p_subs.mp4 (180s, 硬烧字幕)
   - lesson_001_1080p_soft.mkv (180s, 软字幕)
   - lesson_001_vertical.mp4 (180s, 1080x1920)
   - thumbnail.jpg (1920x1080)

📊 文件信息:
   视频编码: H.264, CRF 18
   音频编码: AAC, 192kbps
   总时长: 3分钟
   文件大小: 45MB

🎉 课程视频已就绪！
```

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 音视频不同步 | 时长不匹配 | 检查场景时长设置 |
| 字幕乱码 | 编码问题 | 确保 SRT 文件为 UTF-8 |
| 字幕位置不对 | 字幕样式参数 | 调整 MarginV 参数 |
| 视频模糊 | CRF 值过高 | 降低 CRF 值（18-23推荐） |
| 文件过大 | 比特率过高 | 使用更高 CRF 或降低分辨率 |
