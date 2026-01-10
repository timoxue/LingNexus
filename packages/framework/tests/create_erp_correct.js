const { Document, Packer, Paragraph, TextRun, HeadingLevel } = require('docx');
const fs = require('fs');

// ✅ 正确的文档创建方式
const doc = new Document({
  creator: "Agent",
  title: "ERP系统实施计划",
  sections: [{
    children: [
      // 标题
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [
          new TextRun({
            text: "ERP系统实施计划",
            bold: true,
            size: 32
          })
        ]
      }),

      // 正文 - 每段一个 Paragraph
      new Paragraph({
        children: [
          new TextRun("本计划旨在概述ERP系统的实施过程。")
        ]
      }),

      new Paragraph({
        children: [
          new TextRun("主要步骤包括需求分析、系统设计、开发测试以及最终的部署上线。")
        ]
      }),

      new Paragraph({
        children: [
          new TextRun("整个过程中，团队协作与有效的时间管理至关重要。")
        ]
      }),
    ]
  }]
});

// 导出文档
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('ERP_correct.docx', buffer);
  console.log('✅ 文档创建成功！文件名: ERP_correct.docx');
}).catch(err => {
  console.error('❌ 创建文档失败:', err);
});
