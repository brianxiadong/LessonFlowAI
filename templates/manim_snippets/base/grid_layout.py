"""
LessonFlowAI - Manim 网格布局基类

提供 3x3 网格布局系统，所有元素必须锚定到网格位置，避免元素位置随意。
"""

from manim import *
from typing import Literal

# 3x3 网格锚点位置定义
GRID_ANCHORS = {
    # 行名: (y坐标)
    "top": 2.5,
    "middle": 0,
    "bottom": -2.5,
    # 列名: (x坐标)
    "left": -4.5,
    "center": 0,
    "right": 4.5,
}

# 组合锚点映射
ANCHOR_POSITIONS = {
    "top-left": (GRID_ANCHORS["left"], GRID_ANCHORS["top"], 0),
    "top-center": (GRID_ANCHORS["center"], GRID_ANCHORS["top"], 0),
    "top-right": (GRID_ANCHORS["right"], GRID_ANCHORS["top"], 0),
    "middle-left": (GRID_ANCHORS["left"], GRID_ANCHORS["middle"], 0),
    "middle-center": (GRID_ANCHORS["center"], GRID_ANCHORS["middle"], 0),
    "middle-right": (GRID_ANCHORS["right"], GRID_ANCHORS["middle"], 0),
    "bottom-left": (GRID_ANCHORS["left"], GRID_ANCHORS["bottom"], 0),
    "bottom-center": (GRID_ANCHORS["center"], GRID_ANCHORS["bottom"], 0),
    "bottom-right": (GRID_ANCHORS["right"], GRID_ANCHORS["bottom"], 0),
}

AnchorType = Literal[
    "top-left", "top-center", "top-right",
    "middle-left", "middle-center", "middle-right",
    "bottom-left", "bottom-center", "bottom-right"
]


class GridLayoutScene(Scene):
    """
    带网格布局的基础场景类
    
    所有 LessonFlowAI 生成的场景都应继承此类，
    确保元素位置可控、统一。
    """
    
    # 默认配置
    CONFIG = {
        "show_grid": False,  # 调试时可开启网格显示
        "margin": 0.5,
        "background_color": "#1a1a2e",
    }
    
    def setup(self):
        """场景初始化"""
        super().setup()
        self.elements = {}  # 元素注册表，用于按 ID 查找
        
        if self.CONFIG.get("show_grid", False):
            self._draw_grid()
    
    def _draw_grid(self):
        """绘制调试网格（仅开发时使用）"""
        grid_lines = VGroup()
        
        # 垂直线
        for x in [GRID_ANCHORS["left"], GRID_ANCHORS["center"], GRID_ANCHORS["right"]]:
            line = DashedLine(
                start=[x, -3.5, 0],
                end=[x, 3.5, 0],
                color=GRAY,
                stroke_opacity=0.3
            )
            grid_lines.add(line)
        
        # 水平线
        for y in [GRID_ANCHORS["top"], GRID_ANCHORS["middle"], GRID_ANCHORS["bottom"]]:
            line = DashedLine(
                start=[-6, y, 0],
                end=[6, y, 0],
                color=GRAY,
                stroke_opacity=0.3
            )
            grid_lines.add(line)
        
        # 锚点标记
        for name, pos in ANCHOR_POSITIONS.items():
            dot = Dot(pos, color=YELLOW, radius=0.05)
            label = Text(name, font_size=12, color=GRAY).next_to(dot, DOWN, buff=0.1)
            grid_lines.add(dot, label)
        
        self.add(grid_lines)
    
    def get_anchor_position(self, anchor: AnchorType) -> np.ndarray:
        """获取锚点的绝对坐标"""
        return np.array(ANCHOR_POSITIONS[anchor])
    
    def place_at_anchor(self, mobject: Mobject, anchor: AnchorType) -> Mobject:
        """将元素放置到指定锚点"""
        position = self.get_anchor_position(anchor)
        mobject.move_to(position)
        return mobject
    
    def register_element(self, element_id: str, mobject: Mobject):
        """注册元素到查找表"""
        self.elements[element_id] = mobject
    
    def get_element(self, element_id: str) -> Mobject:
        """按 ID 获取元素"""
        if element_id not in self.elements:
            raise KeyError(f"Element '{element_id}' not found. Available: {list(self.elements.keys())}")
        return self.elements[element_id]
    
    def create_text(
        self, 
        content: str, 
        anchor: AnchorType = "middle-center",
        element_id: str = None,
        size: str = "medium",
        color: str = WHITE
    ) -> Text:
        """创建文本元素并放置到锚点"""
        font_sizes = {"small": 24, "medium": 36, "large": 48}
        text = Text(content, font_size=font_sizes.get(size, 36), color=color)
        self.place_at_anchor(text, anchor)
        
        if element_id:
            self.register_element(element_id, text)
        
        return text
    
    def create_formula(
        self,
        latex: str,
        anchor: AnchorType = "middle-center",
        element_id: str = None,
        size: str = "medium",
        color: str = WHITE
    ) -> MathTex:
        """创建 LaTeX 公式元素"""
        scale_map = {"small": 0.7, "medium": 1.0, "large": 1.3}
        formula = MathTex(latex, color=color).scale(scale_map.get(size, 1.0))
        self.place_at_anchor(formula, anchor)
        
        if element_id:
            self.register_element(element_id, formula)
        
        return formula
    
    def create_box(
        self,
        label: str = None,
        anchor: AnchorType = "middle-center",
        element_id: str = None,
        color: str = BLUE,
        width: float = 2,
        height: float = 1,
        fill_opacity: float = 0.2
    ) -> VGroup:
        """创建带标签的方框"""
        box = Rectangle(
            width=width,
            height=height,
            color=color,
            fill_opacity=fill_opacity
        )
        
        group = VGroup(box)
        
        if label:
            text = Text(label, font_size=24, color=color)
            text.move_to(box.get_center())
            group.add(text)
        
        self.place_at_anchor(group, anchor)
        
        if element_id:
            self.register_element(element_id, group)
        
        return group
    
    def create_arrow_between(
        self,
        from_id: str,
        to_id: str,
        element_id: str = None,
        color: str = WHITE,
        style: str = "solid"
    ) -> Arrow:
        """在两个元素之间创建箭头"""
        from_elem = self.get_element(from_id)
        to_elem = self.get_element(to_id)
        
        if style == "dashed":
            arrow = DashedLine(
                start=from_elem.get_center(),
                end=to_elem.get_center(),
                color=color
            )
            # 添加箭头尖端
            tip = ArrowTriangleFilledTip(color=color)
            arrow.add_tip(tip)
        else:
            arrow = Arrow(
                start=from_elem.get_center(),
                end=to_elem.get_center(),
                color=color,
                buff=0.3
            )
        
        if element_id:
            self.register_element(element_id, arrow)
        
        return arrow
    
    def get_bounding_boxes(self) -> dict:
        """
        获取所有注册元素的边界盒信息
        用于质量检测（边界检查、重叠检测）
        """
        boxes = {}
        for elem_id, mobject in self.elements.items():
            boxes[elem_id] = {
                "center": mobject.get_center().tolist(),
                "width": mobject.width,
                "height": mobject.height,
                "left": mobject.get_left()[0],
                "right": mobject.get_right()[0],
                "top": mobject.get_top()[1],
                "bottom": mobject.get_bottom()[1],
            }
        return boxes
    
    def check_bounds(self, margin: float = 0.5) -> list:
        """
        检查元素是否越界
        返回越界元素列表
        """
        violations = []
        screen_bounds = {
            "left": -7 + margin,
            "right": 7 - margin,
            "top": 4 - margin,
            "bottom": -4 + margin,
        }
        
        for elem_id, mobject in self.elements.items():
            if mobject.get_left()[0] < screen_bounds["left"]:
                violations.append({"id": elem_id, "issue": "out_of_left_bound"})
            if mobject.get_right()[0] > screen_bounds["right"]:
                violations.append({"id": elem_id, "issue": "out_of_right_bound"})
            if mobject.get_top()[1] > screen_bounds["top"]:
                violations.append({"id": elem_id, "issue": "out_of_top_bound"})
            if mobject.get_bottom()[1] < screen_bounds["bottom"]:
                violations.append({"id": elem_id, "issue": "out_of_bottom_bound"})
        
        return violations
    
    def check_overlaps(self, threshold: float = 0.3) -> list:
        """
        检查元素重叠
        返回重叠元素对列表
        """
        overlaps = []
        elem_ids = list(self.elements.keys())
        
        for i, id1 in enumerate(elem_ids):
            for id2 in elem_ids[i+1:]:
                m1, m2 = self.elements[id1], self.elements[id2]
                
                # 简单的边界盒重叠检测
                h_overlap = not (m1.get_right()[0] < m2.get_left()[0] or 
                                m2.get_right()[0] < m1.get_left()[0])
                v_overlap = not (m1.get_top()[1] < m2.get_bottom()[1] or 
                                m2.get_top()[1] < m1.get_bottom()[1])
                
                if h_overlap and v_overlap:
                    overlaps.append({"elements": [id1, id2], "issue": "overlap"})
        
        return overlaps
