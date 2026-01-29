"""
LessonFlowAI - 流程图动画模板

用于展示流程、步骤、架构图等，
支持框图、箭头连接、逐步显示。
"""

from manim import *
from ..base.grid_layout import GridLayoutScene, ANCHOR_POSITIONS
from ..base.style_mixin import StyleMixin


class FlowchartScene(GridLayoutScene, StyleMixin):
    """
    流程图场景模板
    
    用于展示流程、步骤、系统架构，支持：
    - 带标签的方框节点
    - 箭头连接
    - 逐步显示流程
    - 高亮当前步骤
    """
    
    def create_node(
        self,
        label: str,
        anchor: str,
        element_id: str,
        color_name: str = "primary",
        width: float = 2.5,
        height: float = 1
    ) -> VGroup:
        """创建流程图节点"""
        color = self.get_color(color_name)
        
        box = Rectangle(
            width=width,
            height=height,
            color=color,
            fill_opacity=self.style.box_opacity,
            stroke_width=self.style.stroke_width
        ).round_corners(self.style.corner_radius)
        
        text = Text(
            label,
            font_size=24,
            color=self.style.text_color
        )
        text.move_to(box.get_center())
        
        node = VGroup(box, text)
        self.place_at_anchor(node, anchor)
        self.register_element(element_id, node)
        
        return node
    
    def create_diamond(
        self,
        label: str,
        anchor: str,
        element_id: str,
        color_name: str = "accent",
        size: float = 1.5
    ) -> VGroup:
        """创建菱形节点（判断节点）"""
        color = self.get_color(color_name)
        
        diamond = Square(
            side_length=size,
            color=color,
            fill_opacity=self.style.box_opacity,
            stroke_width=self.style.stroke_width
        ).rotate(PI/4)
        
        text = Text(
            label,
            font_size=20,
            color=self.style.text_color
        )
        text.move_to(diamond.get_center())
        
        node = VGroup(diamond, text)
        self.place_at_anchor(node, anchor)
        self.register_element(element_id, node)
        
        return node
    
    def connect_nodes(
        self,
        from_id: str,
        to_id: str,
        element_id: str = None,
        color_name: str = "muted",
        label: str = None,
        direction: str = "auto"
    ) -> VGroup:
        """连接两个节点"""
        from_node = self.get_element(from_id)
        to_node = self.get_element(to_id)
        color = self.get_color(color_name)
        
        # 自动确定连接方向
        if direction == "auto":
            from_center = from_node.get_center()
            to_center = to_node.get_center()
            
            dx = to_center[0] - from_center[0]
            dy = to_center[1] - from_center[1]
            
            if abs(dx) > abs(dy):
                # 水平连接
                start = from_node.get_right() if dx > 0 else from_node.get_left()
                end = to_node.get_left() if dx > 0 else to_node.get_right()
            else:
                # 垂直连接
                start = from_node.get_bottom() if dy < 0 else from_node.get_top()
                end = to_node.get_top() if dy < 0 else to_node.get_bottom()
        else:
            direction_map = {
                "right": (from_node.get_right, to_node.get_left),
                "left": (from_node.get_left, to_node.get_right),
                "down": (from_node.get_bottom, to_node.get_top),
                "up": (from_node.get_top, to_node.get_bottom),
            }
            start_fn, end_fn = direction_map.get(direction, direction_map["right"])
            start, end = start_fn(), end_fn()
        
        arrow = Arrow(
            start=start,
            end=end,
            color=color,
            stroke_width=self.style.stroke_width,
            buff=0.1
        )
        
        result = VGroup(arrow)
        
        if label:
            label_text = Text(
                label,
                font_size=18,
                color=self.get_color("muted")
            )
            label_text.next_to(arrow, UP, buff=0.1)
            result.add(label_text)
        
        if element_id:
            self.register_element(element_id, result)
        
        return result
    
    def highlight_node(
        self,
        element_id: str,
        color_name: str = "accent"
    ) -> Animation:
        """高亮节点"""
        node = self.get_element(element_id)
        color = self.get_color(color_name)
        return Indicate(node, color=color, scale_factor=1.1)
    
    def pulse_node(
        self,
        element_id: str,
        color_name: str = "accent"
    ) -> Animation:
        """节点脉冲效果（表示当前活跃）"""
        node = self.get_element(element_id)
        color = self.get_color(color_name)
        
        # 获取节点的框（第一个子元素）
        box = node[0]
        
        return Succession(
            box.animate.set_stroke(color=color, width=4),
            box.animate.set_stroke(color=self.get_color("primary"), width=self.style.stroke_width),
        )


class AttentionFlowchart(FlowchartScene):
    """
    示例：Attention 机制流程图
    
    演示如何使用 FlowchartScene 模板
    """
    
    def construct(self):
        # 标题
        title = self.create_text(
            "Self-Attention 机制流程",
            anchor="top-center",
            element_id="title",
            size="large"
        )
        self.play(Write(title))
        self.wait(0.5)
        
        # 创建输入节点
        input_node = self.create_node(
            "输入 X",
            anchor="top-left",
            element_id="input",
            color_name="secondary"
        )
        
        # 创建 Q、K、V 节点
        q_node = self.create_node(
            "Query (Q)",
            anchor="middle-left",
            element_id="query",
            color_name="primary",
            width=2
        )
        k_node = self.create_node(
            "Key (K)",
            anchor="middle-center",
            element_id="key",
            color_name="primary",
            width=2
        )
        v_node = self.create_node(
            "Value (V)",
            anchor="middle-right",
            element_id="value",
            color_name="primary",
            width=2
        )
        
        # 创建注意力分数节点
        attn_node = self.create_node(
            "Attention\nScores",
            anchor="bottom-center",
            element_id="attention",
            color_name="accent",
            height=1.2
        )
        
        # 动画：逐步显示节点
        self.play(FadeIn(input_node))
        self.wait(0.5)
        
        self.play(
            FadeIn(q_node),
            FadeIn(k_node),
            FadeIn(v_node),
        )
        self.wait(0.5)
        
        # 连接输入到 Q、K、V
        arrow_xq = self.connect_nodes("input", "query", "arrow_xq")
        arrow_xk = self.connect_nodes("input", "key", "arrow_xk")
        arrow_xv = self.connect_nodes("input", "value", "arrow_xv")
        
        self.play(
            Create(arrow_xq),
            Create(arrow_xk),
            Create(arrow_xv),
        )
        self.wait(0.5)
        
        # 显示注意力分数节点
        self.play(FadeIn(attn_node))
        
        # 连接 Q、K 到 Attention
        arrow_qa = self.connect_nodes("query", "attention", "arrow_qa", direction="down")
        arrow_ka = self.connect_nodes("key", "attention", "arrow_ka", direction="down")
        
        self.play(Create(arrow_qa), Create(arrow_ka))
        
        # 高亮流程
        self.play(self.highlight_node("query"))
        self.play(self.highlight_node("key"))
        self.play(self.highlight_node("attention"))
        
        self.wait(2)
