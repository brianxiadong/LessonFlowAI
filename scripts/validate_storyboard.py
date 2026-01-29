#!/usr/bin/env python3
"""
LessonFlowAI - Storyboard 验证脚本

验证 storyboard.json 是否符合 Schema 规范
"""

import json
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("❌ 请先安装 jsonschema: pip install jsonschema")
    sys.exit(1)


def load_json(path: Path) -> dict:
    """加载 JSON 文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_storyboard(storyboard_path: Path, schema_path: Path = None) -> list:
    """
    验证 storyboard.json
    返回错误列表，空列表表示验证通过
    """
    errors = []
    
    # 加载文件
    try:
        storyboard = load_json(storyboard_path)
    except json.JSONDecodeError as e:
        return [f"JSON 解析错误: {e}"]
    except FileNotFoundError:
        return [f"文件不存在: {storyboard_path}"]
    
    # 加载 Schema
    if schema_path is None:
        schema_path = Path(__file__).parent.parent / "schema" / "storyboard.schema.json"
    
    try:
        schema = load_json(schema_path)
    except FileNotFoundError:
        return [f"Schema 文件不存在: {schema_path}"]
    
    # JSON Schema 验证
    validator = Draft7Validator(schema)
    for error in validator.iter_errors(storyboard):
        errors.append(f"Schema 错误 [{error.json_path}]: {error.message}")
    
    if errors:
        return errors
    
    # 业务规则验证
    errors.extend(validate_business_rules(storyboard))
    
    return errors


def validate_business_rules(storyboard: dict) -> list:
    """验证业务规则"""
    errors = []
    
    meta = storyboard.get("meta", {})
    scenes = storyboard.get("scenes", [])
    
    # 规则 1: 检查总时长
    target_duration = meta.get("duration_target_s", 180)
    total_duration = sum(s.get("duration_s", 0) for s in scenes)
    
    tolerance = target_duration * 0.1  # 10% 容差
    if abs(total_duration - target_duration) > tolerance:
        errors.append(
            f"总时长 ({total_duration}s) 与目标时长 ({target_duration}s) 差异超过 10%"
        )
    
    # 规则 2: 检查场景 ID 唯一性
    scene_ids = [s.get("id") for s in scenes]
    duplicates = [id for id in scene_ids if scene_ids.count(id) > 1]
    if duplicates:
        errors.append(f"场景 ID 重复: {set(duplicates)}")
    
    # 规则 3: 检查元素引用
    for scene in scenes:
        scene_id = scene.get("id", "unknown")
        elements = scene.get("visual", {}).get("elements", [])
        element_ids = {e.get("id") for e in elements}
        
        # 检查箭头引用
        for elem in elements:
            if elem.get("type") == "arrow":
                from_id = elem.get("from")
                to_id = elem.get("to")
                
                if from_id and from_id not in element_ids:
                    errors.append(
                        f"场景 {scene_id}: 箭头 '{elem.get('id')}' 引用了不存在的元素 '{from_id}'"
                    )
                if to_id and to_id not in element_ids:
                    errors.append(
                        f"场景 {scene_id}: 箭头 '{elem.get('id')}' 引用了不存在的元素 '{to_id}'"
                    )
        
        # 检查动画目标
        for step in scene.get("animation", {}).get("steps", []):
            targets = step.get("target", [])
            if isinstance(targets, str):
                targets = [targets]
            
            for target in targets:
                if target not in element_ids and step.get("action") != "wait":
                    errors.append(
                        f"场景 {scene_id}: 动画引用了不存在的元素 '{target}'"
                    )
    
    # 规则 4: 检查 must_show 元素
    for scene in scenes:
        scene_id = scene.get("id", "unknown")
        elements = scene.get("visual", {}).get("elements", [])
        element_ids = {e.get("id") for e in elements}
        
        must_show = scene.get("checks", {}).get("must_show", [])
        for elem_id in must_show:
            if elem_id not in element_ids:
                errors.append(
                    f"场景 {scene_id}: must_show 包含不存在的元素 '{elem_id}'"
                )
    
    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_storyboard.py <storyboard.json> [schema.json]")
        sys.exit(1)
    
    storyboard_path = Path(sys.argv[1])
    schema_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"🔍 验证: {storyboard_path}")
    
    errors = validate_storyboard(storyboard_path, schema_path)
    
    if errors:
        print(f"\n❌ 验证失败，发现 {len(errors)} 个问题:\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        sys.exit(1)
    else:
        print("\n✅ 验证通过！")
        
        # 输出统计信息
        storyboard = load_json(storyboard_path)
        scenes = storyboard.get("scenes", [])
        total_duration = sum(s.get("duration_s", 0) for s in scenes)
        total_elements = sum(len(s.get("visual", {}).get("elements", [])) for s in scenes)
        
        print(f"\n📊 统计信息:")
        print(f"   场景数: {len(scenes)}")
        print(f"   总时长: {total_duration}s ({total_duration // 60}分{total_duration % 60}秒)")
        print(f"   总元素数: {total_elements}")


if __name__ == "__main__":
    main()
