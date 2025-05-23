#!/usr/bin/env python3
"""
快速测试修复后的R1检测
"""

import re


def test_basic_patterns():
    """测试基本的R1模式匹配"""

    test_titles = [
        "Multi-step R1 Reasoning for Complex Problems",
        "R1 Model: A New Approach to Language Understanding",
        "Improved R1 Architecture for Better Performance",
        "Chain-of-Thought R1: Reasoning Step by Step",
        "Evaluating R1 Performance on Complex Tasks",
        "Understanding R1: A Comprehensive Analysis",
        "R1 and Beyond: Next Generation Reasoning",
    ]

    # 修复后的R1模式
    r1_patterns = [
        r"\bR1\b",  # 独立的R1 (大写) - 最重要！
        r"\br1\b",  # 独立的r1 (小写)
        r"\bdeepseek[-_]?r1\b",  # DeepSeek-R1, DeepSeek_R1
        r"\br1[-_]?\d+[bm]?\b",  # R1-7B, R1_32B, R1-8B等
        r"\b\w+[-_]r1\b",  # xxx-R1, xxx_r1
        r"\b\w+[-_]R1\b",  # xxx-R1, xxx_R1
        r"\br1[-_](?!zero|like|based|type|style|similar|inspired)\w+\b",  # R1-xxx (排除描述性)
        r"\bR1[-_](?!zero|like|based|type|style|similar|inspired)\w+\b",  # R1-xxx (排除描述性)
        r"\b\w+r1\b",  # xxxR1, mathR1等
        r"\b\w+R1\b",  # xxxR1, MathR1等
    ]

    print("🧪 测试基本R1模式匹配")
    print("=" * 60)

    for title in test_titles:
        found = False
        matched_pattern = None

        for pattern in r1_patterns:
            if re.search(pattern, title.lower(), re.IGNORECASE):
                found = True
                matched_pattern = pattern
                break

        status = "✅" if found else "❌"
        print(f"{status} {title}")
        if found:
            print(f"   匹配模式: {matched_pattern}")
        print()


def test_exclusion_patterns():
    """测试排除模式"""

    bad_titles = [
        "GUI-G1: Understanding R1-Zero-Like Training for Visual Grounding in GUI Agents",
        "R1-based Approaches to Natural Language Processing",
        "R1-inspired Architecture for Computer Vision",
        "Methods Similar to R1 for Reasoning",
        "R1-type Models in Machine Learning",
        "R1-style Training for Language Models",
    ]

    # 排除模式
    exclude_patterns = [
        r"r1[-_\s]*zero[-_\s]*like",  # R1-Zero-Like
        r"r1[-_\s]*based",  # R1-based
        r"r1[-_\s]*type",  # R1-type
        r"r1[-_\s]*style",  # R1-style
        r"r1[-_\s]*inspired",  # R1-inspired
        r"r1[-_\s]*similar",  # R1-similar
        r"like[-_\s]+r1",  # like R1
        r"similar[-_\s]+to[-_\s]+r1",  # similar to R1
        r"similar[-_\s]+r1",  # similar R1
    ]

    print("🚫 测试排除模式")
    print("=" * 60)

    for title in bad_titles:
        excluded = False
        matched_exclude = None

        for pattern in exclude_patterns:
            if re.search(pattern, title.lower(), re.IGNORECASE):
                excluded = True
                matched_exclude = pattern
                break

        status = "✅" if excluded else "❌"
        print(f"{status} {title}")
        if excluded:
            print(f"   排除模式: {matched_exclude}")
        print()


if __name__ == "__main__":
    test_basic_patterns()
    print("\n" + "=" * 80 + "\n")
    test_exclusion_patterns()
