#!/usr/bin/env python3
"""
LessonFlowAI - 阿里云 TTS 封装

封装阿里云智能语音交互服务，支持：
- 语音合成
- 字级时间戳
- SSML 标记
- 动态 Token 刷新（使用 AK/SK）
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# 尝试导入阿里云 SDK
try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    ALIYUN_CORE_SDK_AVAILABLE = True
except ImportError:
    ALIYUN_CORE_SDK_AVAILABLE = False

try:
    import nls
    ALIYUN_NLS_SDK_AVAILABLE = True
except ImportError:
    ALIYUN_NLS_SDK_AVAILABLE = False

if not ALIYUN_CORE_SDK_AVAILABLE or not ALIYUN_NLS_SDK_AVAILABLE:
    print("⚠️ 阿里云 SDK 未完整安装，TTS 功能不可用")
    print("   安装命令: pip install alibabacloud-nls aliyun-python-sdk-core==2.15.1")


@dataclass
class TTSConfig:
    """TTS 配置"""
    voice: str = "zhitian_emo"  # 音色
    format: str = "wav"  # 输出格式
    sample_rate: int = 16000  # 采样率
    volume: int = 50  # 音量 (0-100)
    speech_rate: int = 0  # 语速 (-500 到 500)
    pitch_rate: int = 0  # 音调 (-500 到 500)
    enable_subtitle: bool = True  # 是否返回时间戳


class AliyunTTS:
    """阿里云 TTS 服务封装"""
    
    # Token 缓存（类级别，避免重复获取）
    _cached_token: str = None
    _cached_token_expire_time: int = 0
    
    def __init__(
        self,
        access_key_id: str = None,
        access_key_secret: str = None,
        app_key: str = None,
        region: str = "cn-shanghai"
    ):
        """
        初始化 TTS 服务
        
        参数可以从环境变量读取：
        - ALIYUN_ACCESS_KEY_ID (必需)
        - ALIYUN_ACCESS_KEY_SECRET (必需)
        - ALIYUN_TTS_APP_KEY (可选，如果不提供则使用默认 appkey)
        
        Token 会使用 AK/SK 动态刷新，无需手动管理
        """
        self.access_key_id = access_key_id or os.getenv("ALIYUN_ACCESS_KEY_ID")
        self.access_key_secret = access_key_secret or os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        self.app_key = app_key or os.getenv("ALIYUN_TTS_APP_KEY")
        self.region = region
        
        if not all([self.access_key_id, self.access_key_secret]):
            raise ValueError(
                "缺少阿里云配置。请设置环境变量:\n"
                "  ALIYUN_ACCESS_KEY_ID (必需)\n"
                "  ALIYUN_ACCESS_KEY_SECRET (必需)\n"
                "  ALIYUN_TTS_APP_KEY (可选)"
            )
    
    def _get_token(self) -> str:
        """
        获取访问 Token（使用 AK/SK 动态刷新）
        
        Token 有效期内会复用缓存，过期前自动刷新
        """
        # Token 有效期内直接返回（提前 5 分钟刷新）
        if (AliyunTTS._cached_token and 
            time.time() < AliyunTTS._cached_token_expire_time - 300):
            return AliyunTTS._cached_token
        
        if not ALIYUN_CORE_SDK_AVAILABLE:
            raise RuntimeError("阿里云核心 SDK 未安装: pip install aliyun-python-sdk-core==2.15.1")
        
        client = AcsClient(
            self.access_key_id,
            self.access_key_secret,
            self.region
        )
        
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')
        
        try:
            response = client.do_action_with_exception(request)
            result = json.loads(response)
            
            AliyunTTS._cached_token = result["Token"]["Id"]
            AliyunTTS._cached_token_expire_time = result["Token"]["ExpireTime"]
            
            print(f"✅ Token 刷新成功，有效期至: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(AliyunTTS._cached_token_expire_time))}")
            
            return AliyunTTS._cached_token
        except Exception as e:
            raise RuntimeError(f"获取 Token 失败: {e}")
    
    def get_token_info(self) -> dict:
        """获取当前 Token 信息"""
        token = self._get_token()
        return {
            "token": token[:20] + "..." if token else None,
            "expire_time": AliyunTTS._cached_token_expire_time,
            "expire_time_str": time.strftime('%Y-%m-%d %H:%M:%S', 
                                             time.localtime(AliyunTTS._cached_token_expire_time)) if AliyunTTS._cached_token_expire_time else None,
            "remaining_seconds": int(AliyunTTS._cached_token_expire_time - time.time()) if AliyunTTS._cached_token_expire_time else 0
        }
    
    def synthesize(
        self,
        text: str,
        output_path: str,
        config: TTSConfig = None
    ) -> dict:
        """
        合成语音
        
        Args:
            text: 要合成的文本（支持 SSML）
            output_path: 输出音频文件路径
            config: TTS 配置
        
        Returns:
            dict: 包含 audio_path, timestamps_path, duration_ms 等信息
        """
        if not ALIYUN_NLS_SDK_AVAILABLE:
            raise RuntimeError("阿里云 NLS SDK 未安装: pip install alibabacloud-nls")
        
        config = config or TTSConfig()
        token = self._get_token()
        
        # 如果没有提供 app_key，使用默认值（需要从阿里云控制台获取）
        appkey = self.app_key
        if not appkey:
            raise ValueError(
                "合成语音需要 APP_KEY。请在阿里云智能语音控制台创建项目获取:\n"
                "  https://nls-portal.console.aliyun.com/\n"
                "  然后设置环境变量 ALIYUN_TTS_APP_KEY"
            )
        
        # 存储合成结果
        audio_data = bytearray()
        timestamps = []
        
        def on_data(data, *args):
            """接收音频数据"""
            audio_data.extend(data)
        
        def on_message(message, *args):
            """接收消息（包含时间戳）"""
            try:
                msg = json.loads(message)
                if "payload" in msg and "subtitles" in msg["payload"]:
                    timestamps.extend(msg["payload"]["subtitles"])
            except json.JSONDecodeError:
                pass
        
        def on_error(message, *args):
            """错误处理"""
            raise RuntimeError(f"TTS 错误: {message}")
        
        # 创建合成器
        synthesizer = nls.NlsSpeechSynthesizer(
            url="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1",
            token=token,
            appkey=appkey,
            on_data=on_data,
            on_message=on_message,
            on_error=on_error
        )
        
        # 开始合成
        synthesizer.start(
            text=text,
            voice=config.voice,
            aformat=config.format,
            sample_rate=config.sample_rate,
            volume=config.volume,
            speech_rate=config.speech_rate,
            pitch_rate=config.pitch_rate,
            enable_subtitle=config.enable_subtitle
        )
        
        # 保存音频
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(audio_data)
        
        # 保存时间戳
        timestamps_path = output_path.with_suffix(".timestamps.json")
        with open(timestamps_path, "w", encoding="utf-8") as f:
            json.dump({"subtitles": timestamps}, f, ensure_ascii=False, indent=2)
        
        # 计算时长
        duration_ms = timestamps[-1]["end_time"] if timestamps else 0
        
        return {
            "audio_path": str(output_path),
            "timestamps_path": str(timestamps_path),
            "duration_ms": duration_ms,
            "subtitle_count": len(timestamps),
            "character_count": len(text)
        }
    
    @staticmethod
    def estimate_cost(text: str, rate_per_10k_chars: float = 2.0) -> dict:
        """
        估算 TTS 费用
        
        Args:
            text: 要合成的文本
            rate_per_10k_chars: 每万字符费率（元）
        
        Returns:
            dict: 包含字符数和预估费用
        """
        char_count = len(text)
        cost = (char_count / 10000) * rate_per_10k_chars
        
        return {
            "character_count": char_count,
            "estimated_cost_cny": round(cost, 2),
            "rate": f"¥{rate_per_10k_chars}/万字符"
        }


def prepare_ssml(
    text: str,
    glossary: dict = None,
    speed: float = 1.0,
    pause_after_period: int = 300,
    pause_after_comma: int = 150
) -> str:
    """
    将普通文本转换为 SSML 格式
    
    Args:
        text: 原始文本
        glossary: 术语表（包含发音信息）
        speed: 语速倍率
        pause_after_period: 句号后停顿（毫秒）
        pause_after_comma: 逗号后停顿（毫秒）
    
    Returns:
        str: SSML 格式文本
    """
    ssml_text = text
    
    # 替换术语发音
    if glossary:
        terms = glossary.get("terms", {})
        for term, info in terms.items():
            if term in ssml_text:
                if "ssml" in info:
                    # 使用预定义的 SSML 标记
                    ssml_text = ssml_text.replace(term, info["ssml"])
                elif "alias" in info:
                    # 使用别名（让 TTS 读中文）
                    ssml_text = ssml_text.replace(term, info["alias"])
    
    # 添加标点停顿
    ssml_text = ssml_text.replace("。", f'。<break time="{pause_after_period}ms"/>')
    ssml_text = ssml_text.replace("！", f'！<break time="{pause_after_period}ms"/>')
    ssml_text = ssml_text.replace("？", f'？<break time="{pause_after_period}ms"/>')
    ssml_text = ssml_text.replace("，", f'，<break time="{pause_after_comma}ms"/>')
    ssml_text = ssml_text.replace("；", f'；<break time="{pause_after_comma}ms"/>')
    
    # 包装为完整 SSML
    ssml = f'''<speak>
    <prosody rate="{speed}">
        {ssml_text}
    </prosody>
</speak>'''
    
    return ssml


# 示例使用
if __name__ == "__main__":
    import sys
    
    # 测试 Token 获取
    print("=" * 50)
    print("🔐 测试 Token 动态刷新")
    print("=" * 50)
    
    try:
        tts = AliyunTTS()
        token_info = tts.get_token_info()
        print(f"✅ Token 获取成功!")
        print(f"   Token: {token_info['token']}")
        print(f"   过期时间: {token_info['expire_time_str']}")
        print(f"   剩余有效期: {token_info['remaining_seconds']} 秒")
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"❌ Token 获取失败: {e}")
        sys.exit(1)
    
    print()
    
    # 费用估算示例
    sample_text = "今天我们来学习 Transformer 的核心机制：Self-Attention。"
    cost = AliyunTTS.estimate_cost(sample_text)
    print(f"📊 费用估算:")
    print(f"   字符数: {cost['character_count']}")
    print(f"   预估费用: ¥{cost['estimated_cost_cny']}")
    print(f"   计费标准: {cost['rate']}")
    
    # SSML 转换示例
    glossary = {
        "terms": {
            "Transformer": {
                "alias": "Transformer模型",
                "ssml": '<sub alias="Transformer模型">Transformer</sub>'
            },
            "Self-Attention": {
                "alias": "自注意力机制"
            }
        }
    }
    
    ssml = prepare_ssml(sample_text, glossary)
    print(f"\n📝 SSML 输出:")
    print(ssml)
    
    # 检查 APP_KEY 是否配置
    print()
    print("=" * 50)
    print("📋 配置状态")
    print("=" * 50)
    if tts.app_key:
        print(f"✅ APP_KEY 已配置: {tts.app_key[:10]}...")
        print("   可以进行语音合成")
    else:
        print("⚠️ APP_KEY 未配置")
        print("   Token 动态刷新正常，但语音合成需要 APP_KEY")
        print("   请访问: https://nls-portal.console.aliyun.com/ 创建项目获取")
