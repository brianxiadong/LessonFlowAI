"""
LessonFlowAI - 公式推导动画模板

用于逐步展示数学公式的推导过程，
支持高亮、替换、逐项显示等常见模式。
"""

from manim import *
from ..base.grid_layout import GridLayoutScene
from ..base.style_mixin import StyleMixin


class FormulaDerivationScene(GridLayoutScene, StyleMixin):
    """
    公式推导场景模板
    
    用于展示数学公式的逐步推导，支持：
    - 逐步写入公式
    - 高亮特定部分
    - 等式变换动画
    - 解释性文字
    """
    
    def create_formula_step(
        self,
        latex: str,
        anchor: str = "middle-center",
        element_id: str = None
    ) -> MathTex:
        """创建公式步骤"""
        formula = MathTex(latex, color=self.style.text_color)
        self.place_at_anchor(formula, anchor)
        if element_id:
            self.register_element(element_id, formula)
        return formula
    
    def highlight_part(
        self,
        formula: MathTex,
        indices: list,
        color: str = None
    ) -> Animation:
        """高亮公式的特定部分"""
        highlight_color = self.get_color(color) if color else self.style.accent
        return Indicate(
            VGroup(*[formula[i] for i in indices]),
            color=highlight_color
        )
    
    def transform_formula(
        self,
        old_formula: MathTex,
        new_latex: str,
        duration: float = None
    ) -> tuple:
        """变换公式并返回新公式对象"""
        new_formula = MathTex(new_latex, color=self.style.text_color)
        new_formula.move_to(old_formula.get_center())
        
        dur = duration or self.default_animation_duration()
        animation = TransformMatchingTex(old_formula, new_formula, run_time=dur)
        
        return new_formula, animation
    
    def add_explanation(
        self,
        text: str,
        formula: MathTex,
        direction=DOWN,
        element_id: str = None
    ) -> Text:
        """在公式旁添加解释文字"""
        explanation = self.styled_text(text, style="small", color="muted")
        explanation.next_to(formula, direction, buff=0.5)
        
        if element_id:
            self.register_element(element_id, explanation)
        
        return explanation


class QuadraticFormulaDerivation(FormulaDerivationScene):
    """
    示例：二次方程求根公式推导
    
    演示如何使用 FormulaDerivationScene 模板
    """
    
    def construct(self):
        # 标题
        title = self.create_text(
            "二次方程求根公式推导",
            anchor="top-center",
            element_id="title",
            size="large"
        )
        self.play(Write(title))
        self.wait(0.5)
        
        # 步骤 1: 一般形式
        step1 = self.create_formula_step(
            r"ax^2 + bx + c = 0",
            anchor="middle-center",
            element_id="step1"
        )
        self.play(Write(step1))
        
        explanation1 = self.add_explanation(
            "从一般形式开始",
            step1,
            element_id="exp1"
        )
        self.play(FadeIn(explanation1))
        self.wait(1)
        
        # 步骤 2: 两边除以 a
        self.play(FadeOut(explanation1))
        
        step2 = MathTex(
            r"x^2 + \frac{b}{a}x + \frac{c}{a} = 0",
            color=self.style.text_color
        )
        step2.move_to(step1.get_center())
        
        self.play(TransformMatchingTex(step1, step2))
        self.register_element("step2", step2)
        
        explanation2 = self.add_explanation(
            "两边同除以 a",
            step2,
            element_id="exp2"
        )
        self.play(FadeIn(explanation2))
        self.wait(1)
        
        # 步骤 3: 配方
        self.play(FadeOut(explanation2))
        
        step3 = MathTex(
            r"\left(x + \frac{b}{2a}\right)^2 = \frac{b^2 - 4ac}{4a^2}",
            color=self.style.text_color
        )
        step3.move_to(step2.get_center())
        
        self.play(TransformMatchingTex(step2, step3))
        self.register_element("step3", step3)
        
        explanation3 = self.add_explanation(
            "配方法",
            step3,
            element_id="exp3"
        )
        self.play(FadeIn(explanation3))
        self.wait(1)
        
        # 步骤 4: 最终公式
        self.play(FadeOut(explanation3))
        
        step4 = MathTex(
            r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
            color=self.style.text_color
        )
        step4.move_to(step3.get_center())
        
        self.play(TransformMatchingTex(step3, step4))
        self.register_element("step4", step4)
        
        # 高亮判别式
        self.play(Indicate(step4[0][7:15], color=self.style.accent))
        
        explanation4 = self.add_explanation(
            "这就是著名的求根公式！",
            step4,
            element_id="exp4"
        )
        self.play(FadeIn(explanation4))
        
        # 框出最终结果
        box = SurroundingRectangle(step4, color=self.style.primary, buff=0.2)
        self.play(Create(box))
        
        self.wait(2)
