#!/usr/bin/env python3
"""
测试R1模型检测的精确性
"""

import re


def is_r1_model_paper(title, summary="", debug=True):
    """测试版本的R1模型检测函数"""

    full_text = f"{title} {summary}".lower()
    title_lower = title.lower()

    if debug:
        print(f"\n🔍 检查: {title}")

    # R1模式检测 - 修复：添加独立R1模式
    r1_patterns = [
        r"\bR1\b",  # 独立的R1 (大写) - 最重要的模式！
        r"\br1\b",  # 独立的r1 (小写)
        r"\bdeepseek-r1\b",  # DeepSeek-R1
        r"\bdeepseek_r1\b",  # DeepSeek_R1
        r"\br1-\d+[bm]?\b",  # R1-7B, R1-32B
        r"\b\w+-r1\b",  # xxx-r1 (简化)
        r"\b\w+-R1\b",  # xxx-R1 (简化)
        r"\br1-(?!zero|like|based|type|style)\w+\b",  # R1-xxx (排除描述性)
        r"\bR1-(?!zero|like|based|type|style)\w+\b",  # R1-xxx (排除描述性)
        r"\b\w+r1\b",  # xxxr1 (简化)
        r"\b\w+R1\b",  # xxxR1 (简化)
    ]

    # 检查R1模式
    has_r1_pattern = False
    matched_pattern = None
    for pattern in r1_patterns:
        if re.search(pattern, full_text, re.IGNORECASE):
            has_r1_pattern = True
            matched_pattern = pattern
            if debug:
                print(f"  ✓ 匹配模式: {pattern}")
            break

    if not has_r1_pattern:
        if debug:
            print(f"  ✗ 未找到R1模式")
        return False

    # 排除明确的非模型用法 - 修复：增强生物学模式
    exclude_patterns = [
        r"r1[-_\s]*zero[-_\s]*like",  # R1-Zero-Like
        r"r1[-_\s]*based",  # R1-based
        r"r1[-_\s]*type",  # R1-type
        r"r1[-_\s]*style",  # R1-style
        r"r1[-_\s]*inspired",  # R1-inspired
        r"r1[-_\s]*similar",  # R1-similar
        r"like[-_\s]+r1",  # like R1
        r"similar[-_\s]+to[-_\s]+r1",  # similar to R1
        r"inspired[-_\s]+by[-_\s]+r1",  # inspired by R1
        r"against.*r1",  # against R1
        r"attack.*r1",  # attack R1
        r"vulnerability.*r1",  # vulnerability R1
        r"r1.*receptor",  # biological R1 receptor
        r"r1\s+regulation",  # R1 regulation (修复)
        r"regulation.*r1",  # regulation R1 (修复)
        r"r1.*gene",  # R1 gene
        r"gene.*r1",  # gene R1
        r"r1.*protein",  # R1 protein
        r"protein.*r1",  # protein R1
        r"r1.*cell",  # R1 cell
        r"cell.*r1",  # cell R1
        r"vitamin.*r1",  # vitamin R1
        r"r1.*vitamin",  # R1 vitamin
        r"r1.*deficiency",  # R1 deficiency
        r"deficiency.*r1",  # deficiency R1
        r"biological.*r1",  # biological R1
        r"r1.*biological",  # R1 biological
        r"cellular.*r1",  # cellular R1
        r"r1.*cellular",  # R1 cellular
    ]

    for exclude in exclude_patterns:
        if re.search(exclude, full_text, re.IGNORECASE):
            if debug:
                print(f"  ✗ 被排除模式拒绝: {exclude}")
            return False

    # 如果标题中包含R1，通常是模型名
    if re.search(r"\br1\b", title_lower, re.IGNORECASE):
        if debug:
            print(f"  ✓ 标题包含R1 - 可能是模型名")
        return True

    # 检查模型指示词
    model_indicators = [
        r"r1\s+(model|architecture|network|agent|system)",
        r"(model|architecture|network|agent|system)\s+r1",
        r"proposed?\s+r1",
        r"introducing?\s+r1",
        r"r1\s+(can|will|does|achieve|perform|demonstrate)",
        r"r1\s+(outperform|exceed|surpass)",
        r"using\s+r1",
        r"r1.*reasoning",
        r"reasoning.*r1",
        r"r1.*performance",
        r"performance.*r1",
    ]

    for indicator in model_indicators:
        if re.search(indicator, full_text, re.IGNORECASE):
            if debug:
                print(f"  ✓ 找到模型指示词: {indicator}")
            return True

    # 宽松模式：特定R1变体
    lenient_patterns = [
        r"\bdeepseek[-_]?r1\b",  # DeepSeek-R1 变体
        r"\br1[-_]?\d+[bm]?\b",  # R1-7B 等
    ]

    for pattern in lenient_patterns:
        if re.search(pattern, full_text, re.IGNORECASE):
            if debug:
                print(f"  ✓ 宽松模式接受: {pattern}")
            return True

    if debug:
        print(f"  ✗ 没有足够证据证明是R1模型")
    return False


def test_cases():
    """测试用例"""
    test_data = [
        # 应该接受的R1模型论文
        (
            "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
            "",
            True,
        ),
        ("R1-Bench: A Comprehensive Benchmark for Reasoning", "", True),
        (
            "Multi-step R1 Reasoning for Complex Problems",
            "We propose R1 model for reasoning",
            True,
        ),
        ("R1 Model: A New Approach to Language Understanding", "", True),
        ("Improved R1 Architecture for Better Performance", "", True),
        ("Chain-of-Thought R1: Reasoning Step by Step", "", True),
        ("R1-7B: A Large Language Model", "", True),
        ("MathR1: Mathematical Reasoning with R1", "", True),
        (
            "Evaluating R1 Performance on Complex Tasks",
            "R1 model demonstrates superior performance",
            True,
        ),
        # 应该拒绝的非R1模型论文
        (
            "GUI-G1: Understanding R1-Zero-Like Training for Visual Grounding in GUI Agents",
            "",
            False,
        ),
        ("The R1 receptor in biological systems", "", False),
        ("Vitamin R1 deficiency studies", "", False),
        ("R1 regulation in cellular processes", "", False),
        ("Some random paper about deep learning", "", False),
        ("Attacking R1 Models: A Security Analysis", "", False),
        ("R1-based Approaches to Natural Language Processing", "", False),
        ("R1-inspired Architecture for Computer Vision", "", False),
        ("Methods Similar to R1 for Reasoning", "", False),
        ("R1-type Models in Machine Learning", "", False),
        ("R1-style Training for Language Models", "", False),
        ("Vulnerability Analysis of R1 Systems", "", False),
        # 边界情况
        (
            "Understanding R1: A Comprehensive Analysis",
            "R1 is a powerful reasoning model",
            True,
        ),
        ("Benchmarking Against R1 Models", "We compare our method against R1", False),
        (
            "R1 and Beyond: Next Generation Reasoning",
            "R1 model has shown great results",
            True,
        ),
    ]

    print("🧪 R1模型检测测试")
    print("=" * 80)

    correct = 0
    total = len(test_data)

    for title, summary, expected in test_data:
        result = is_r1_model_paper(title, summary, debug=False)
        status = "✅" if result == expected else "❌"

        print(f"{status} {title}")
        if result != expected:
            print(f"   预期: {expected}, 实际: {result}")
            print(f"   >>> 需要调试:")
            is_r1_model_paper(title, summary, debug=True)
        else:
            correct += 1
        print()

    print(f"📊 测试结果: {correct}/{total} ({correct / total * 100:.1f}%) 正确")

    if correct == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  需要进一步调优")


if __name__ == "__main__":
    test_cases()
