---
name: tts-voice
description: 使用阿里云 TTS 生成配音，支持字级时间戳和 SSML 控制
---

# 配音生成 Skill (Voice)

## 概述

此 Skill 负责使用阿里云智能语音交互服务生成高质量配音，支持：
- 字级时间戳（用于精准字幕对齐）
- SSML 标记（控制语速、停顿、术语发音）
- 多种音色选择
- 音频后处理（响度标准化）

## 触发条件

- 前置条件：`storyboard.json` 和 `glossary.json` 已存在
- 触发方式：
  - 自动：Orchestrator 调用
  - 手动：用户说 "生成配音" / "TTS"

## 输入

```
courses/[lesson_id]/
  storyboard.json    # 每个场景的 narration.vo_text
  glossary.json      # 术语发音表
```

## 输出

```
courses/[lesson_id]/
  audio/
    scene_001.wav
    scene_001_timestamps.json
    scene_002.wav
    scene_002_timestamps.json
    ...
  logs/
    tts_cost.log     # 费用统计
```

## 阿里云 TTS 配置

### 开通服务

1. 访问 [阿里云智能语音交互控制台](https://nls-portal.console.aliyun.com/)
2. 开通「语音合成」服务
3. 创建项目，获取 AppKey
4. 获取 AccessKey ID 和 Secret

### 环境变量配置

```bash
export ALIYUN_ACCESS_KEY_ID="your_access_key_id"
export ALIYUN_ACCESS_KEY_SECRET="your_access_key_secret"
export ALIYUN_TTS_APP_KEY="your_app_key"
```

### 可用音色

| 音色名 | 语言 | 风格 | 推荐场景 |
|--------|------|------|----------|
| zhitian_emo | 中文 | 情感女声 | 教学讲解 |
| zhiyan_emo | 中文 | 情感女声 | 故事叙述 |
| zhigui | 中文 | 男声 | 新闻播报 |
| xiaoyun | 中文 | 标准女声 | 通用 |
| kenny | 英文 | 男声 | 英语教学 |

## 执行步骤

### 步骤 1：费用预估

**重要**：在生成前先估算费用，避免意外消费。

```python
def estimate_tts_cost(storyboard: dict) -> dict:
    """
    估算 TTS 费用
    阿里云定价: 约 ¥2/万字符（以实际定价为准）
    """
    total_chars = 0
    
    for scene in storyboard["scenes"]:
        vo_text = scene.get("narration", {}).get("vo_text", "")
        total_chars += len(vo_text)
    
    # 费率（元/万字符）
    rate = 2.0
    estimated_cost = (total_chars / 10000) * rate
    
    return {
        "total_characters": total_chars,
        "estimated_cost_cny": round(estimated_cost, 2),
        "rate": f"¥{rate}/万字符"
    }
```

**输出示例**：
```
📊 TTS 费用预估
   总字符数: 2,850
   预估费用: ¥0.57
   计费标准: ¥2/万字符

确认生成? (y/n)
```

### 步骤 2：准备 SSML 文本

将普通文本转换为带 SSML 标记的文本：

```python
def prepare_ssml(text: str, glossary: dict, config: dict) -> str:
    """
    准备 SSML 文本
    - 替换术语发音
    - 添加停顿标记
    - 设置语速
    """
    ssml_text = text
    
    # 替换术语发音
    for term, info in glossary.get("terms", {}).items():
        if term in ssml_text and "ssml" in info:
            ssml_text = ssml_text.replace(term, info["ssml"])
        elif term in ssml_text and "alias" in info:
            # 使用别名替换（让 TTS 读中文）
            ssml_text = ssml_text.replace(term, info["alias"])
    
    # 在标点后添加停顿
    ssml_text = ssml_text.replace("。", '。<break time="300ms"/>')
    ssml_text = ssml_text.replace("，", '，<break time="150ms"/>')
    
    # 包装为 SSML
    speed = config.get("speed", 1.0)
    ssml = f'''<speak>
    <prosody rate="{speed}">
        {ssml_text}
    </prosody>
</speak>'''
    
    return ssml
```

**SSML 示例**：

原始文本：
```
Attention 是 Transformer 的核心机制。
```

转换后：
```xml
<speak>
    <prosody rate="1.0">
        <phoneme alphabet="ipa" ph="əˈtenʃən">Attention</phoneme> 是 
        <phoneme alphabet="ipa" ph="ˈtrænsˌfɔrmər">Transformer</phoneme> 的核心机制。
        <break time="300ms"/>
    </prosody>
</speak>
```

### 步骤 3：调用阿里云 TTS API

```python
import nls
import json
from pathlib import Path

class AliyunTTS:
    def __init__(self, access_key_id, access_key_secret, app_key):
        self.token = self._get_token(access_key_id, access_key_secret)
        self.app_key = app_key
    
    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "zhitian_emo",
        format: str = "wav",
        sample_rate: int = 16000,
        enable_subtitle: bool = True
    ) -> dict:
        """
        合成语音并返回时间戳
        """
        timestamps = []
        audio_data = bytearray()
        
        def on_data(data, *args):
            audio_data.extend(data)
        
        def on_message(message, *args):
            msg = json.loads(message)
            if "payload" in msg and "subtitles" in msg["payload"]:
                timestamps.extend(msg["payload"]["subtitles"])
        
        synthesizer = nls.NlsSpeechSynthesizer(
            token=self.token,
            appkey=self.app_key,
            on_data=on_data,
            on_message=on_message
        )
        
        synthesizer.start(
            text=text,
            voice=voice,
            format=format,
            sample_rate=sample_rate,
            enable_subtitle=enable_subtitle
        )
        
        # 保存音频
        with open(output_path, "wb") as f:
            f.write(audio_data)
        
        # 保存时间戳
        timestamp_path = output_path.replace(".wav", "_timestamps.json")
        with open(timestamp_path, "w", encoding="utf-8") as f:
            json.dump({"subtitles": timestamps}, f, ensure_ascii=False, indent=2)
        
        return {
            "audio_path": output_path,
            "timestamps_path": timestamp_path,
            "duration_ms": timestamps[-1]["end_time"] if timestamps else 0,
            "subtitle_count": len(timestamps)
        }
```

### 步骤 4：音频后处理

**响度标准化（LUFS）**：

```python
from pydub import AudioSegment
from pydub.effects import normalize

def normalize_audio(input_path: str, output_path: str, target_lufs: float = -16.0):
    """
    响度标准化
    target_lufs: 目标响度（-16 LUFS 是常见标准）
    """
    audio = AudioSegment.from_wav(input_path)
    
    # 标准化
    normalized = normalize(audio)
    
    # 导出
    normalized.export(output_path, format="wav")
    
    return output_path
```

**静音处理**：

```python
def add_silence(audio_path: str, before_ms: int = 0, after_ms: int = 500):
    """在音频前后添加静音"""
    audio = AudioSegment.from_wav(audio_path)
    
    silence_before = AudioSegment.silent(duration=before_ms)
    silence_after = AudioSegment.silent(duration=after_ms)
    
    result = silence_before + audio + silence_after
    result.export(audio_path, format="wav")
```

### 步骤 5：批量生成

```python
def generate_all_voice(lesson_path: Path, storyboard: dict, glossary: dict):
    """为所有场景生成配音"""
    
    tts = AliyunTTS(
        access_key_id=os.getenv("ALIYUN_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
        app_key=os.getenv("ALIYUN_TTS_APP_KEY")
    )
    
    audio_dir = lesson_path / "audio"
    audio_dir.mkdir(exist_ok=True)
    
    results = []
    total_cost = 0
    
    for scene in storyboard["scenes"]:
        scene_id = scene["id"]
        narration = scene.get("narration", {})
        vo_text = narration.get("vo_text", "")
        
        if not vo_text:
            continue
        
        # 准备 SSML
        ssml_text = prepare_ssml(vo_text, glossary, narration)
        
        # 合成
        output_path = str(audio_dir / f"{scene_id}.wav")
        result = tts.synthesize(
            text=ssml_text,
            output_path=output_path,
            voice=narration.get("voice", "zhitian_emo")
        )
        
        # 后处理
        normalize_audio(output_path, output_path)
        add_silence(
            output_path,
            before_ms=int(narration.get("pause_before_s", 0) * 1000),
            after_ms=int(narration.get("pause_after_s", 0.5) * 1000)
        )
        
        results.append({
            "scene_id": scene_id,
            **result
        })
        
        total_cost += len(vo_text)
    
    # 记录费用
    cost_log = lesson_path / "logs" / "tts_cost.log"
    cost_log.parent.mkdir(exist_ok=True)
    with open(cost_log, "w") as f:
        f.write(f"总字符数: {total_cost}\n")
        f.write(f"预估费用: ¥{total_cost / 10000 * 2:.2f}\n")
    
    return results
```

### 步骤 6：增量更新支持

只为 hash 变化的场景重新生成配音：

```python
for scene in storyboard["scenes"]:
    scene_id = scene["id"]
    
    # 计算 narration hash
    narration_hash = hash(json.dumps(scene.get("narration", {})))
    cached_hash = build_cache.get(scene_id, {}).get("narration_hash")
    
    audio_file = audio_dir / f"{scene_id}.wav"
    
    if narration_hash != cached_hash or not audio_file.exists():
        # 需要重新生成
        generate_voice(scene)
        print(f"🔄 重新生成配音: {scene_id}")
    else:
        print(f"⏭️ 跳过（未变更）: {scene_id}")
```

## 输出确认

```
✅ 配音生成完成！
📁 输出目录: courses/lesson_001/audio/
🎙️ 音频文件:
   - scene_001.wav (10.2s, 16kHz)
   - scene_001_timestamps.json (42 个时间点)
   - scene_002.wav (12.5s, 16kHz) 🔄 新生成
   - scene_003.wav ⏭️ 跳过

💰 费用统计:
   本次生成字符数: 1,250
   本次费用: ¥0.25
   累计费用: ¥0.57

下一步: 运行 Skill 4 (Subtitles) 生成字幕
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `InvalidToken` | Token 过期 | 重新获取 Token |
| `QuotaExhausted` | 配额用尽 | 检查账户余额或提升配额 |
| `InvalidParameter` | SSML 语法错误 | 检查 SSML 标记 |
| `AudioTooLong` | 文本过长 | 拆分为多段合成 |

## 本地测试（免费方案）

如需本地测试不消耗阿里云配额，可使用 edge-tts：

```python
# 仅用于测试，无时间戳
import edge_tts

async def test_tts(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    await communicate.save(output_path)
```

注意：edge-tts 不提供字级时间戳，正式使用需阿里云服务。
