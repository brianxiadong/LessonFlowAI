#!/bin/bash
# LessonFlowAI 完整流程脚本
# 用法: ./build_lesson.sh <课程目录>

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误: 请指定课程目录${NC}"
    echo "用法: $0 <课程目录>"
    echo "示例: $0 courses/pythagorean_theorem"
    exit 1
fi

LESSON_DIR="$1"
LESSON_NAME=$(basename "$LESSON_DIR")

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          LessonFlowAI 完整流水线                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📚 课程: ${LESSON_NAME}${NC}"
echo -e "${GREEN}📁 目录: ${LESSON_DIR}${NC}"
echo ""

# 进入课程目录
cd "$LESSON_DIR"

# 加载环境变量
if [ -f "../../.env" ]; then
    export $(cat ../../.env | grep -v '^#' | xargs)
fi

# Step 1-3: 已完成（Planner, Animator, Builder）
echo -e "${GREEN}✅ [1-3/6] 策划+代码+渲染 - 已完成${NC}"
echo "   - outline.md"
echo "   - storyboard.json"
echo "   - scenes/*.py"
echo "   - media/videos/full_animation/1080p60/*.mp4"
echo ""

# Step 4: 生成配音字幕文本（不需要实际TTS，用文本描述代替）
echo -e "${YELLOW}[4/6] 📝 生成字幕文本...${NC}"
mkdir -p subs
mkdir -p audio

# 从 storyboard 提取旁白文本
python3 << 'EOF'
import json
from pathlib import Path

with open('storyboard.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 生成合并字幕文件
subs_dir = Path('subs')
subs_dir.mkdir(exist_ok=True)

full_srt = subs_dir / 'full_lesson.srt'
full_vtt = subs_dir / 'full_lesson.vtt'

# SRT 格式
with open(full_srt, 'w', encoding='utf-8') as srt:
    idx = 1
    current_time = 0
    
    for scene in data.get('scenes', []):
        narration = scene.get('narration', {})
        text = narration.get('text', '')
        duration = scene.get('duration', 30)
        
        if not text:
            current_time += duration
            continue
        
        # 简单分句
        sentences = text.replace('。', '。\n').strip().split('\n')
        sentence_duration = duration / len(sentences)
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            start_ms = int(current_time * 1000)
            end_ms = int((current_time + sentence_duration) * 1000)
            
            start_time = f"{start_ms//3600000:02d}:{(start_ms%3600000)//60000:02d}:{(start_ms%60000)//1000:02d},{start_ms%1000:03d}"
            end_time = f"{end_ms//3600000:02d}:{(end_ms%3600000)//60000:02d}:{(end_ms%60000)//1000:02d},{end_ms%1000:03d}"
            
            srt.write(f"{idx}\n")
            srt.write(f"{start_time} --> {end_time}\n")
            srt.write(f"{sentence.strip()}\n\n")
            
            idx += 1
            current_time += sentence_duration

# VTT 格式
with open(full_vtt, 'w', encoding='utf-8') as vtt:
    vtt.write("WEBVTT\n\n")
    with open(full_srt, 'r', encoding='utf-8') as srt:
        content = srt.read()
        # 转换时间戳格式 (,→.)
        content = content.replace(',', '.')
        vtt.write(content)

print(f"✅ 字幕文件已生成")
print(f"   - {full_srt}")
print(f"   - {full_vtt}")
EOF

echo -e "${GREEN}✅ [4/6] 字幕生成完成${NC}"
echo ""

# Step 5: 合成最终视频（带字幕）
echo -e "${YELLOW}[5/6] 🎬 合成带字幕视频...${NC}"
mkdir -p final

# 找到源视频
SOURCE_VIDEO="media/videos/full_animation/1080p60/PythagoreanTheorem.mp4"

if [ ! -f "$SOURCE_VIDEO" ]; then
    echo -e "${RED}❌ 源视频不存在: $SOURCE_VIDEO${NC}"
    exit 1
fi

# 方案1: 硬字幕（字幕烧入视频）
echo "   烧入硬字幕..."
ffmpeg -y -i "$SOURCE_VIDEO" \
    -vf "subtitles=subs/full_lesson.srt:force_style='FontName=PingFang SC,FontSize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BackColour=&H80000000,Outline=2,Shadow=1,MarginV=50'" \
    -c:v libx264 -crf 18 -preset medium \
    -c:a copy \
    final/${LESSON_NAME}_1080p_hardsub.mp4 \
    2>&1 | grep -E "(frame|time|speed)" | tail -3

# 方案2: 软字幕（独立字幕轨）
echo "   添加软字幕轨..."
ffmpeg -y -i "$SOURCE_VIDEO" \
    -i subs/full_lesson.srt \
    -c copy -c:s mov_text \
    -metadata:s:s:0 language=chi \
    final/${LESSON_NAME}_1080p_softsub.mp4 \
    2>&1 | grep -E "(frame|time|speed)" | tail -3

# 复制无字幕版本
cp "$SOURCE_VIDEO" final/${LESSON_NAME}_1080p.mp4

echo -e "${GREEN}✅ [5/6] 视频合成完成${NC}"
echo ""

# Step 6: 生成缩略图和报告
echo -e "${YELLOW}[6/6] 📊 生成缩略图和报告...${NC}"

# 生成缩略图
ffmpeg -y -i "final/${LESSON_NAME}_1080p.mp4" \
    -ss 00:00:25 -vframes 1 -q:v 2 \
    final/thumbnail.jpg \
    2>&1 | tail -1

# 生成报告
cat > final/REPORT.md << EOFR
# ${LESSON_NAME} - 生成报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**处理时长**: $(date -u -d @$SECONDS '+%M分%S秒' 2>/dev/null || echo "${SECONDS}秒")

## 📦 产物清单

| 文件 | 大小 | 说明 |
|------|------|------|
| ${LESSON_NAME}_1080p.mp4 | $(ls -lh final/${LESSON_NAME}_1080p.mp4 | awk '{print $5}') | 无字幕原版 |
| ${LESSON_NAME}_1080p_hardsub.mp4 | $(ls -lh final/${LESSON_NAME}_1080p_hardsub.mp4 | awk '{print $5}') | 硬字幕版（推荐） |
| ${LESSON_NAME}_1080p_softsub.mp4 | $(ls -lh final/${LESSON_NAME}_1080p_softsub.mp4 | awk '{print $5}') | 软字幕版 |
| thumbnail.jpg | $(ls -lh final/thumbnail.jpg | awk '{print $5}') | 视频封面 |
| full_lesson.srt | $(ls -lh subs/full_lesson.srt | awk '{print $5}') | SRT字幕 |
| full_lesson.vtt | $(ls -lh subs/full_lesson.vtt | awk '{print $5}') | VTT字幕 |

## 🎯 使用建议

### 在线平台上传
推荐使用 **${LESSON_NAME}_1080p_hardsub.mp4**（硬字幕版）

### 本地播放器
使用 **${LESSON_NAME}_1080p_softsub.mp4**（软字幕版），可自由开关字幕

### 嵌入网页
\`\`\`html
<video controls>
  <source src="${LESSON_NAME}_1080p.mp4" type="video/mp4">
  <track kind="subtitles" src="full_lesson.vtt" srclang="zh" label="中文">
</video>
\`\`\`

---
*Generated by LessonFlowAI*
EOFR

echo -e "${GREEN}✅ [6/6] 报告生成完成${NC}"
echo ""

# 完成总结
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║               🎉 完整流水线执行完成！                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📁 输出目录:${NC} $(pwd)/final/"
echo ""
echo -e "${GREEN}📹 视频文件:${NC}"
echo "   - ${LESSON_NAME}_1080p_hardsub.mp4 (带硬字幕，推荐)"
echo "   - ${LESSON_NAME}_1080p_softsub.mp4 (带软字幕)"
echo "   - ${LESSON_NAME}_1080p.mp4 (无字幕)"
echo ""
echo -e "${GREEN}📝 字幕文件:${NC}"
echo "   - subs/full_lesson.srt"
echo "   - subs/full_lesson.vtt"
echo ""
echo -e "${GREEN}📊 详细报告:${NC}"
echo "   - final/REPORT.md"
echo ""
echo -e "${YELLOW}💡 预览视频:${NC}"
echo "   open final/${LESSON_NAME}_1080p_hardsub.mp4"
echo ""
