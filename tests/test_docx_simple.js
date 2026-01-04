const { Document, Packer, Paragraph, TextRun, HeadingLevel } = require("docx");
const fs = require("fs");

const doc = new Document({
  sections: [{
    children: [
      new Paragraph({
        heading: HeadingLevel.TITLE,
        children: [new TextRun("LingNexus测试文档")]
      }),
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("介绍")]
      }),
      new Paragraph({
        children: [new TextRun("这里是关于 LingNexus 测试文档的简要介绍。")]
      }),
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("功能")]
      }),
      new Paragraph({
        children: [new TextRun("这里描述了 LingNexus 测试文档的主要功能。")]
      }),
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("总结")]
      }),
      new Paragraph({
        children: [new TextRun("这是对 LingNexus 测试文档的总结。")]
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("LingNexus测试文档.docx", buffer);
  console.log("✅ Word 文档创建成功：LingNexus测试文档.docx");
});
