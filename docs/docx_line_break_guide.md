# DOCX 换行问题解决方案

## 问题描述

在使用 `docx` 库生成 Word 文档时，使用 `\n` 字符串**不会**自动转换为换行。

### 错误示例

```javascript
// ❌ 这样写不会换行
new Paragraph({
  children: [
    new TextRun("第一行\n第二行\n第三行"),  // \n 不会生效
  ]
})
```

### 问题原因

`docx` 库使用 Word 的 OpenXML 格式，换行需要使用特定的 XML 元素，而不是简单的 `\n` 字符。

## 解决方案

### 方法 1：使用多个 Paragraph（推荐）

每个段落使用单独的 `Paragraph` 对象：

```javascript
// ✅ 推荐：使用多个 Paragraph
new Paragraph({ children: [new TextRun("第一行")] }),
new Paragraph({ children: [new TextRun("第二行")] }),
new Paragraph({ children: [new TextRun("第三行")] }),
```

### 方法 2：使用 TextRun 的 break 属性

在同一个 Paragraph 中使用多个 TextRun，每个 TextRun 之间添加 break：

```javascript
// ✅ 使用 break 换行
new Paragraph({
  children: [
    new TextRun("第一行"),
    new TextRun({ text: "", break: 1 }),  // 换行
    new TextRun("第二行"),
    new TextRun({ text: "", break: 1 }),  // 换行
    new TextRun("第三行"),
  ]
})
```

### 方法 3：使用多个 TextRun（适合列表）

```javascript
// ✅ 适合列表
new Paragraph({
  children: [
    new TextRun("• 项目经理：张三"),
    new TextRun({ text: "", break: 1 }),
    new TextRun("• 开发人员：李四、王五"),
    new TextRun({ text: "", break: 1 }),
    new TextRun("• 测试人员：赵六"),
  ]
})
```

## 完整示例

### ERP 计划书示例（修正版）

```javascript
const { Document, Packer, Paragraph, TextRun } = require("docx");
const fs = require("fs");

const doc = new Document({
  sections: [
    {
      children: [
        // 标题
        new Paragraph({
          children: [
            new TextRun({
              text: "项目名称：ERP 系统开发计划",
              bold: true,
              size: 32,
            }),
          ],
        }),

        // 1. 项目背景 - 使用多个 Paragraph
        new Paragraph({
          children: [
            new TextRun({ text: "1. 项目背景：", bold: true }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("企业资源规划（ERP）系统是现代企业管理的重要工具。"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("本项目旨在开发一个高效、集成的 ERP 系统。"),
          ],
        }),

        // 2. 项目团队 - 使用 break
        new Paragraph({
          children: [
            new TextRun({ text: "2. 项目团队：", bold: true }),
            new TextRun({ text: "", break: 1 }),
            new TextRun("• 项目经理：张三"),
            new TextRun({ text: "", break: 1 }),
            new TextRun("• 开发人员：李四、王五"),
            new TextRun({ text: "", break: 1 }),
            new TextRun("• 测试人员：赵六"),
          ],
        }),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("output.docx", buffer);
  console.log("✅ 文档创建成功！");
});
```

## 换行方式对比

| 方法 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **多个 Paragraph** | 语义清晰，易于理解 | 代码稍多 | 正文段落 |
| **break 属性** | 代码紧凑 | 代码可读性稍差 | 列表、联系方式 |
| **\n 字符串** | 简单 | **不生效** | ❌ 不要使用 |

## 高级技巧

### 添加多个空行

```javascript
new Paragraph({
  children: [
    new TextRun("第一行"),
    new TextRun({ text: "", break: 2 }),  // 2 个换行 = 1 个空行
    new TextRun("第二行"),
  ]
})
```

### 段落间距

```javascript
new Paragraph({
  spacing: {
    before: 200,  // 段前间距 (单位：缇 twip)
    after: 200,   // 段后间距
  },
  children: [
    new TextRun("这个段落有上下间距"),
  ]
})
```

### 列表缩进

```javascript
new Paragraph({
  indent: {
    left: 720,  // 左缩进 (单位：缇 twip, 720 = 1厘米)
  },
  children: [
    new TextRun("  • 这是一个缩进的列表项"),
  ]
})
```

## 常见问题

### Q: 为什么不能直接用 \n？

A: Word 使用 OpenXML 格式，换行需要特定的 XML 元素（`<w:br/>`），而不是简单的换行符。

### Q: break 的数字是什么意思？

A: `break: 1` 表示 1 个换行，`break: 2` 表示 2 个换行（等于 1 个空行）。

### Q: 如何选择使用哪种方法？

A:
- **正文段落**：使用多个 Paragraph
- **列表、联系方式**：使用 break
- **复杂布局**：组合使用两种方法

## 示例文件

项目中有完整的示例：
- `tests/create_erp_plan_fixed.js` - ERP 计划书（正确版本）

运行示例：
```bash
node tests/create_erp_plan_fixed.js
```

输出：`ERP_计划书.docx`

## 总结

✅ **正确做法**：
- 使用多个 Paragraph 对象
- 使用 TextRun 的 break 属性

❌ **错误做法**：
- 使用 `\n` 字符串（不会生效）
- 使用 `\n\n` 字符串（不会生效）

记住：在 docx 库中，**每个段落就是一个 Paragraph 对象**，这是最自然和清晰的做法！
