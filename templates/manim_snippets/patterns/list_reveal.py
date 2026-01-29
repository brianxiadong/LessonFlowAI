"""
LessonFlowAI - 列表逐项显示模板

用于展示要点列表、步骤说明等，
支持逐项动画、图标标记、编号列表。
"""

from manim import *
from ..base.grid_layout import GridLayoutScene
from ..base.style_mixin import StyleMixin


class ListRevealScene(GridLayoutScene, StyleMixin):
    """
    列表显示场景模板
    
    用于展示要点列表，支持：
    - 逐项渐入动画
    - 编号/图标标记
    - 高亮当前项
    - 分组显示
    """
    
    def create_bullet_list(
        self,
        items: list,
        anchor: str = "middle-left",
        element_id: str = "list",
        bullet_style: str = "circle",  # "circle", "number", "arrow", "check"
        spacing: float = 0.8
    ) -> VGroup:
        """创建项目列表"""
        
        bullet_chars = {
            "circle": "●",
            "arrow": "→",
            "check": "✓",
            "star": "★",
        }
        
        list_group = VGroup()
        
        for i, item_text in enumerate(items):
            # 项目符号或编号
            if bullet_style == "number":
                bullet = self.styled_text(f"{i+1}.", style="body", color="primary")
            else:
                bullet = Text(
                    bullet_chars.get(bullet_style, "●"),
                    font_size=24,
                    color=self.get_color("primary")
                )
            
            # 项目文本
            text = self.styled_text(item_text, style="body")
            
            # 组合
            item = VGroup(bullet, text).arrange(RIGHT, buff=0.3)
            list_group.add(item)
        
        # 垂直排列
        list_group.arrange(DOWN, buff=spacing, aligned_edge=LEFT)
        
        # 放置到锚点
        self.place_at_anchor(list_group, anchor)
        self.register_element(element_id, list_group)
        
        return list_group
    
    def reveal_items(
        self,
        list_group: VGroup,
        interval: float = 0.5,
        animation_type: str = "fade"  # "fade", "write", "grow"
    ) -> list:
        """获取逐项显示的动画列表"""
        animations = []
        
        for item in list_group:
            if animation_type == "fade":
                anim = FadeIn(item, shift=RIGHT * 0.3)
            elif animation_type == "write":
                anim = Write(item)
            elif animation_type == "grow":
                anim = GrowFromCenter(item)
            else:
                anim = FadeIn(item)
            
            animations.append(anim)
        
        return animations
    
    def highlight_item(
        self,
        list_group: VGroup,
        index: int,
        color_name: str = "accent"
    ) -> AnimationGroup:
        """高亮指定项"""
        # 淡化其他项
        animations = []
        for i, item in enumerate(list_group):
            if i == index:
                animations.append(item.animate.set_opacity(1))
                animations.append(Indicate(item, color=self.get_color(color_name)))
            else:
                animations.append(item.animate.set_opacity(0.3))
        
        return AnimationGroup(*animations)
    
    def create_checklist(
        self,
        items: list,
        anchor: str = "middle-left",
        element_id: str = "checklist"
    ) -> VGroup:
        """创建待办清单样式列表"""
        list_group = VGroup()
        
        for item_text in items:
            # 方框
            checkbox = Square(
                side_length=0.3,
                color=self.get_color("muted"),
                stroke_width=2
            )
            
            # 文本
            text = self.styled_text(item_text, style="body")
            
            item = VGroup(checkbox, text).arrange(RIGHT, buff=0.3)
            list_group.add(item)
        
        list_group.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        self.place_at_anchor(list_group, anchor)
        self.register_element(element_id, list_group)
        
        return list_group
    
    def check_item(
        self,
        list_group: VGroup,
        index: int
    ) -> AnimationGroup:
        """勾选指定项"""
        item = list_group[index]
        checkbox = item[0]
        
        checkmark = Text(
            "✓",
            font_size=24,
            color=self.get_color("secondary")
        ).move_to(checkbox.get_center())
        
        return AnimationGroup(
            checkbox.animate.set_color(self.get_color("secondary")),
            FadeIn(checkmark, scale=1.5)
        )


class TransformerKeyPointsList(ListRevealScene):
    """
    示例：Transformer 关键要点
    """
    
    def construct(self):
        # 标题
        title = self.create_text(
            "Transformer 核心要点",
            anchor="top-center",
            element_id="title",
            size="large"
        )
        self.play(Write(title))
        self.wait(0.5)
        
        # 要点列表
        points = [
            "Self-Attention 机制",
            "位置编码 (Positional Encoding)",
            "多头注意力 (Multi-Head)",
            "前馈神经网络 (FFN)",
            "残差连接 + LayerNorm",
        ]
        
        point_list = self.create_bullet_list(
            points,
            anchor="middle-center",
            element_id="points",
            bullet_style="number"
        )
        
        # 逐项显示
        animations = self.reveal_items(point_list)
        for anim in animations:
            self.play(anim, run_time=0.5)
            self.wait(0.3)
        
        self.wait(0.5)
        
        # 高亮第一项
        self.play(self.highlight_item(point_list, 0))
        self.wait(1)
        
        # 恢复
        for item in point_list:
            item.set_opacity(1)
        self.play(*[item.animate.set_opacity(1) for item in point_list])
        
        self.wait(2)
