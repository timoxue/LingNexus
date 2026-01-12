#!/usr/bin/env python3
"""
Docx Skill Tools - Agent 可调用的工具函数

这些函数可以被 AgentScope 的 Agent 通过 toolkit 调用。
"""
import sys
import os
from pathlib import Path
from typing import Optional

# 添加 skill 目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入 AgentScope 的 ToolResponse
try:
    from agentscope.tool import ToolResponse
except ImportError:
    # 如果不在 agentscope 环境中，定义一个简单的响应类
    class ToolResponse(str):
        pass


def create_new_docx(filename: str = "document.docx") -> str:
    """
    创建一个新的空 Word 文档 (.docx)

    Args:
        filename: 文件名，例如 "erp.docx" 或 "document.docx"

    Returns:
        str: 成功消息和文件路径

    Example:
        >>> result = create_new_docx("erp.docx")
        >>> print(result)
        "成功创建文件: /path/to/erp.docx"

    Agent Usage:
        Agent 可以直接调用此函数: create_new_docx(filename="erp.docx")
    """
    try:
        # 检查文件扩展名
        if not filename.endswith('.docx'):
            filename = filename + '.docx' if '.' not in filename else filename.rsplit('.', 1)[0] + '.docx'

        # 确定输出路径（当前工作目录）
        output_path = Path.cwd() / filename

        # 方法 1: 使用 docx 库（最简单）
        try:
            from docx import Document
            doc = Document()
            doc.save(output_path)
            return f"✓ 成功创建空 Word 文档: {output_path}"
        except ImportError:
            # 方法 2: 使用 python-docx 模块
            pass

        # 方法 2: 使用最小 OOXML 结构创建空文档
        import zipfile
        from io import BytesIO

        # 创建最小的 OOXML 结构
        # [Content_Types].xml
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

        # _rels/.rels
        rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

        # word/document.xml
        document = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:pPr>
                <w:jc w:val="both"/>
            </w:pPr>
        </w:p>
        <w:sectPr>
            <w:pgSz w:w="12240" w:h="15840"/>
            <w:pgMar w:top="1440" w:right="1800" w:bottom="1440" w:left="1800" w:header="720" w:footer="720" w:gutter="0"/>
        </w:sectPr>
    </w:body>
</w:document>'''

        # word/_rels/document.xml.rels
        document_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''

        # word/styles.xml
        styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:docDefaults>
        <w:rPrDefault>
            <w:rPr>
                <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                <w:sz w:val="22"/>
                <w:szCs w:val="22"/>
            </w:rPr>
        </w:rPrDefault>
    </w:docDefaults>
</w:styles>'''

        # 创建 ZIP 文件（.docx 本质上是 ZIP）
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as docx:
            docx.writestr('[Content_Types].xml', content_types)
            docx.writestr('_rels/.rels', rels)
            docx.writestr('word/document.xml', document)
            docx.writestr('word/_rels/document.xml.rels', document_rels)
            docx.writestr('word/styles.xml', styles)

        return f"✓ 成功创建空 Word 文档: {output_path}\n文件已保存在当前工作目录"

    except Exception as e:
        return f"✗ 创建文档失败: {str(e)}"


def create_docx_with_text(filename: str, text_content: str = "") -> str:
    """
    创建一个包含文本内容的 Word 文档

    Args:
        filename: 文件名
        text_content: 文档内容（纯文本）

    Returns:
        str: 成功消息和文件路径
    """
    try:
        from docx import Document

        if not filename.endswith('.docx'):
            filename = filename + '.docx' if '.' not in filename else filename.rsplit('.', 1)[0] + '.docx'

        output_path = Path.cwd() / filename
        doc = Document()

        if text_content:
            doc.add_paragraph(text_content)

        doc.save(output_path)
        return f"✓ 成功创建 Word 文档: {output_path}\n内容: '{text_content[:50]}...' if len(text_content) > 50 else text_content"

    except ImportError:
        return "✗ python-docx 库未安装，请运行: pip install python-docx"
    except Exception as e:
        return f"✗ 创建文档失败: {str(e)}"


def list_docx_files() -> str:
    """
    列出当前目录中的所有 .docx 文件

    Returns:
        str: 文件列表
    """
    try:
        docx_files = list(Path.cwd().glob("*.docx"))
        if not docx_files:
            return "当前目录中没有 .docx 文件"

        result = "当前目录中的 .docx 文件:\n"
        for f in sorted(docx_files):
            size = f.stat().st_size
            result += f"  - {f.name} ({size} bytes)\n"

        return result.strip()

    except Exception as e:
        return f"✗ 列出文件失败: {str(e)}"


# 测试代码
if __name__ == "__main__":
    print("测试 docx 工具...")

    result1 = create_new_docx("test_empty.docx")
    print(result1)

    result2 = create_docx_with_text("test_with_text.docx", "这是一个测试文档")
    print(result2)

    result3 = list_docx_files()
    print(result3)
