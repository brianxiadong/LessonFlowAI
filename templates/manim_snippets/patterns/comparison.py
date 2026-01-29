"""
LessonFlowAI - 对比图动画模板

用于展示两个概念/方法的对比，
支持左右布局、渐进对比、差异高亮。
"""

from manim import *
from ..base.grid_layout import GridLayoutScene
from ..base.style_mixin import StyleMixin


class ComparisonScene(GridLayoutScene, StyleMixin):
    """
    对比图场景模板
    
    用于展示概念对比，支持：
    - 左右分栏布局
    - 特征点对比
    - 差异高亮
    - 优缺点列表
    """
    
    def create_comparison_title(
        self,
        left_title: str,
        right_title: str,
        vs_text: str = "VS"
    ) -> VGroup:
        """创建对比标题"""
        left = self.styled_text(left_title, style="title", color="primary")
        left.move_to([-3.5, 2.5, 0])
        
        vs = self.styled_text(vs_text, style="body", color="muted")
        vs.move_to([0, 2.5, 0])
        
        right = self.styled_text(right_title, style="title", color="secondary")
        right.move_to([3.5, 2.5, 0])
        
        group = VGroup(left, vs, right)
        self.register_element("comparison_title", group)
        
        return group
    
    def create_feature_row(
        self,
        left_text: str,
        right_text: str,
        row_index: int,
        element_id: str,
        highlight: str = None  # "left", "right", None
    ) -> VGroup:
        """创建对比特征行"""
        y_pos = 1 - row_index * 1.2
        
        # 左侧特征
        left_color = "accent" if highlight == "left" else "text"
        left = self.styled_text(left_text, style="body", color=left_color)
        left.move_to([-3.5, y_pos, 0])
        
        # 分隔线
        separator = DashedLine(
            start=[0, y_pos + 0.4, 0],
            end=[0, y_pos - 0.4, 0],
            color=self.get_color("muted"),
            stroke_opacity=0.3
        )
        
        # 右侧特征
        right_color = "accent" if highlight == "right" else "text"
        right = self.styled_text(right_text, style="body", color=right_color)
        right.move_to([3.5, y_pos, 0])
        
        group = VGroup(left, separator, right)
        self.register_element(element_id, group)
        
        return group
    
    def create_pros_cons(
        self,
        side: str,  # "left" or "right"
        pros: list,
        cons: list,
        element_id: str
    ) -> VGroup:
        """创建优缺点列表"""
        x_pos = -3.5 if side == "left" else 3.5
        
        items = VGroup()
        y_offset = 1
        
        # 优点
        for pro in pros:
            item = VGroup(
                Text("✓", font_size=24, color=self.get_color("secondary")),
                self.styled_text(pro, style="small")
            ).arrange(RIGHT, buff=0.2)
            item.move_to([x_pos, y_offset, 0])
            items.add(item)
            y_offset -= 0.6
        
        y_offset -= 0.3  # 额外间距
        
        # 缺点
        for con in cons:
            item = VGroup(
                Text("✗", font_size=24, color=self.get_color("error")),
                self.styled_text(con, style="small")
            ).arrange(RIGHT, buff=0.2)
            item.move_to([x_pos, y_offset, 0])
            items.add(item)
            y_offset -= 0.6
        
        self.register_element(element_id, items)
        return items
    
    def draw_divider(self) -> Line:
        """绘制中间分隔线"""
        divider = Line(
            start=[0, 2, 0],
            end=[0, -3, 0],
            color=self.get_color("muted"),
            stroke_width=2
        )
        self.register_element("divider", divider)
        return divider


class RNNvsTransformerComparison(ComparisonScene):
    """
    示例：RNN vs Transformer 对比
    """
    
    def construct(self):
        # 标题
        title = self.create_comparison_title("RNN", "Transformer")
        self.play(Write(title))
        
        # 分隔线
        divider = self.draw_divider()
        self.play(Create(divider))
        self.wait(0.5)
        
        # 特征对比
        features = [
            ("顺序处理", "并行处理", "right"),
            ("短程依赖", "长程依赖", "right"),
            ("参数共享", "位置编码", None),
            ("训练较慢", "训练更快", "right"),
            ("显存占用小", "显存占用大", "left"),
        ]
        
        rows = []
        for i, (left, right, highlight) in enumerate(features):
            row = self.create_feature_row(
                left, right, i, f"row_{i}", highlight
            )
            rows.append(row)
            self.play(FadeIn(row), run_time=0.5)
            self.wait(0.3)
        
        # 高亮总结
        conclusion = self.styled_text(
            "Transformer 更适合大规模并行训练",
            style="body",
            color="accent"
        )
        conclusion.move_to([0, -2.8, 0])
        
        self.play(Write(conclusion))
        self.wait(2)
