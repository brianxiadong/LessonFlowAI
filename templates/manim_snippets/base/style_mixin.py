"""
LessonFlowAI - 统一样式混入

提供统一的颜色、字体、动画样式配置，
确保课程系列视觉一致性。
"""

from manim import *
from dataclasses import dataclass
from typing import Optional


@dataclass
class StyleConfig:
    """样式配置数据类"""
    # 颜色
    background: str = "#1a1a2e"
    primary: str = "#4fc3f7"
    secondary: str = "#81c784"
    accent: str = "#ffb74d"
    text_color: str = "#ffffff"
    error: str = "#ef5350"
    muted: str = "#9e9e9e"
    
    # 字体
    title_font: str = "Source Han Sans CN"
    body_font: str = "Source Han Sans CN"
    code_font: str = "JetBrains Mono"
    
    # 字号
    title_size: int = 48
    body_size: int = 32
    small_size: int = 24
    
    # 形状
    corner_radius: float = 0.1
    stroke_width: float = 2
    box_opacity: float = 0.2
    
    # 动画
    default_duration: float = 1.0
    fast_duration: float = 0.5
    slow_duration: float = 2.0


# 预设风格
STYLE_PRESETS = {
    "tech-minimal": StyleConfig(
        background="#1a1a2e",
        primary="#4fc3f7",
        secondary="#81c784",
        accent="#ffb74d",
    ),
    "hand-drawn": StyleConfig(
        background="#faf8f5",
        primary="#2d3436",
        secondary="#6c5ce7",
        accent="#fd79a8",
        text_color="#2d3436",
    ),
    "corporate": StyleConfig(
        background="#ffffff",
        primary="#0066cc",
        secondary="#28a745",
        accent="#fd7e14",
        text_color="#333333",
    ),
    "playful": StyleConfig(
        background="#fff3e0",
        primary="#e91e63",
        secondary="#9c27b0",
        accent="#ff9800",
        text_color="#333333",
    ),
    "academic": StyleConfig(
        background="#f5f5f5",
        primary="#1565c0",
        secondary="#2e7d32",
        accent="#c62828",
        text_color="#212121",
    ),
}


class StyleMixin:
    """
    样式混入类
    
    为 Scene 提供统一的样式方法和配置。
    继承此类的 Scene 可以使用预设风格或自定义样式。
    """
    
    style: StyleConfig = STYLE_PRESETS["tech-minimal"]
    
    @classmethod
    def set_style(cls, style_name: str):
        """设置预设风格"""
        if style_name not in STYLE_PRESETS:
            raise ValueError(f"Unknown style: {style_name}. Available: {list(STYLE_PRESETS.keys())}")
        cls.style = STYLE_PRESETS[style_name]
    
    @classmethod
    def set_custom_style(cls, config: StyleConfig):
        """设置自定义风格"""
        cls.style = config
    
    def get_color(self, color_name: str) -> str:
        """获取风格颜色"""
        color_map = {
            "primary": self.style.primary,
            "secondary": self.style.secondary,
            "accent": self.style.accent,
            "text": self.style.text_color,
            "error": self.style.error,
            "muted": self.style.muted,
            "background": self.style.background,
        }
        return color_map.get(color_name, color_name)  # 如果不在映射中，直接返回原值
    
    def styled_text(
        self,
        content: str,
        style: str = "body",
        color: Optional[str] = None
    ) -> Text:
        """创建风格化文本"""
        size_map = {
            "title": self.style.title_size,
            "body": self.style.body_size,
            "small": self.style.small_size,
        }
        font_map = {
            "title": self.style.title_font,
            "body": self.style.body_font,
            "code": self.style.code_font,
        }
        
        text_color = self.get_color(color) if color else self.style.text_color
        
        return Text(
            content,
            font_size=size_map.get(style, self.style.body_size),
            font=font_map.get(style, self.style.body_font),
            color=text_color
        )
    
    def styled_box(
        self,
        width: float = 2,
        height: float = 1,
        color_name: str = "primary",
        fill: bool = True
    ) -> Rectangle:
        """创建风格化方框"""
        color = self.get_color(color_name)
        return Rectangle(
            width=width,
            height=height,
            color=color,
            fill_opacity=self.style.box_opacity if fill else 0,
            stroke_width=self.style.stroke_width,
        ).round_corners(self.style.corner_radius)
    
    def styled_arrow(
        self,
        start: np.ndarray,
        end: np.ndarray,
        color_name: str = "primary"
    ) -> Arrow:
        """创建风格化箭头"""
        color = self.get_color(color_name)
        return Arrow(
            start=start,
            end=end,
            color=color,
            stroke_width=self.style.stroke_width,
            buff=0.2
        )
    
    def styled_circle(
        self,
        radius: float = 1,
        color_name: str = "primary",
        fill: bool = True
    ) -> Circle:
        """创建风格化圆形"""
        color = self.get_color(color_name)
        return Circle(
            radius=radius,
            color=color,
            fill_opacity=self.style.box_opacity if fill else 0,
            stroke_width=self.style.stroke_width,
        )
    
    def default_animation_duration(self, speed: str = "normal") -> float:
        """获取动画时长"""
        duration_map = {
            "fast": self.style.fast_duration,
            "normal": self.style.default_duration,
            "slow": self.style.slow_duration,
        }
        return duration_map.get(speed, self.style.default_duration)
