"""
LessonFlowAI CLI 入口
"""

import typer

app = typer.Typer(
    name="lessonflow",
    help="AI 驱动的教学视频自动生成系统"
)


@app.command()
def create(
    topic: str = typer.Argument(..., help="教学主题"),
    duration: int = typer.Option(180, "--duration", "-d", help="目标时长（秒）"),
    audience: str = typer.Option("beginner", "--audience", "-a", help="目标受众"),
    style: str = typer.Option("tech-minimal", "--style", "-s", help="视觉风格"),
):
    """创建新的教学课程"""
    typer.echo(f"🚀 开始创建课程...")
    typer.echo(f"📝 主题: {topic}")
    typer.echo(f"⏱️ 时长: {duration}秒")
    typer.echo(f"👥 受众: {audience}")
    typer.echo(f"🎨 风格: {style}")
    typer.echo("\n请使用 Claude Skills 执行完整流水线")


@app.command()
def validate(
    storyboard: str = typer.Argument(..., help="storyboard.json 文件路径")
):
    """验证分镜脚本"""
    from pathlib import Path
    import subprocess
    import sys
    
    script_path = Path(__file__).parent.parent / "scripts" / "validate_storyboard.py"
    result = subprocess.run([sys.executable, str(script_path), storyboard])
    raise typer.Exit(result.returncode)


@app.command()
def version():
    """显示版本信息"""
    from lessonflow import __version__
    typer.echo(f"LessonFlowAI v{__version__}")


def main():
    app()


if __name__ == "__main__":
    main()
