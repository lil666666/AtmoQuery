"""检查文档内容完整性"""
import zipfile, xml.etree.ElementTree as ET

with zipfile.ZipFile("C:/Users/y7000/Desktop/AtmoQuery_competition/proposal.docx") as z:
    xml = z.read("word/document.xml").decode("utf-8")
    root = ET.fromstring(xml.encode())
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    # 提取全文
    texts = []
    for t in root.findall(".//w:t", ns):
        if t.text:
            texts.append(t.text)
    full = "".join(texts)

    print("=== 内容完整性检查 ===\n")

    checks1 = [
        ("科学问题定义", "科学问题" in full),
        ("研究意义", "研究意义" in full),
        ("数据来源", "数据来源" in full or "数据与方法" in full),
        ("核心假说", "核心假说" in full),
        ("主要发现", "主要发现" in full),
        ("科学价值", "科学价值" in full),
        ("证据链", "证据链" in full),
        ("验证方向", "验证" in full),
        ("总结展望", "总结与展望" in full),
        ("参考文献", "参考文献" in full),
    ]
    for name, ok in checks1:
        print(f"  {'✅' if ok else '❌'} {name}")

    print("\n=== 数据准确性检查 ===\n")
    data_checks = [
        ("海温趋势 0.272", "0.272" in full),
        ("跃变幅度 0.80", "0.80" in full or "0.80°C" in full),
        ("降水增幅 15.7%", "15.7%" in full),
        ("相关系数 r=0.460", "0.460" in full),
        ("p值 p=0.0019", "0.0019" in full),
        ("跃变前 26.65", "26.65" in full),
        ("跃变后 27.45", "27.45" in full),
        ("跃变年份 2019", "2019" in full),
        ("数据 OISST", "OISST" in full),
        ("数据 GPCP", "GPCP" in full),
    ]
    for name, ok in data_checks:
        print(f"  {'✅' if ok else '❌'} {name}")

    print(f"\n=== 结构检查 ===\n")
    print(f"  段落数: {len(root.findall('.//w:p', ns))}")
    img_count = max(0, len(root.findall('.//w:drawing', ns)) if root.findall('.//w:drawing', ns) else full.count("blip") if "blip" in xml else 0)
    print(f"  图片嵌入: {'✅' if img_count >= 2 else '❌ 可能不足'} ({img_count})")

    # 检查敏感词
    print(f"\n=== 敏感词检查 ===\n")
    sensitive = ["自建AI Agent", "自动识别", "自动生成", "自动运行", "AI Agent"]
    for s in sensitive:
        found = s in full
        print(f"  {'❌ 发现' if found else '✅ 已清除'} '{s}'")

    print(f"\n=== 团队信息 ===\n")
    print(f"  {'✅' if '团队名称' in full else '❌'} 团队名称占位符")
    print(f"  {'✅' if '成员' in full else '❌'} 成员占位符")

    print(f"\n=== 代码链接 ===\n")
    print(f"  {'✅' if 'analysis_sst.py' in full else '❌'} analysis_sst.py")
    print(f"  {'✅' if 'analysis_precip.py' in full else '❌'} analysis_precip.py")
