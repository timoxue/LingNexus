const { Document, Packer, Paragraph, TextRun } = require("docx");
const fs = require("fs");

// 创建 ERP 文档
const doc = new Document({
  creator: "Claude",
  title: "ERP 系统开发计划书",
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

        // 1. 项目背景
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
            new TextRun("本项目旨在开发一个高效、集成的 ERP 系统，提升企业的运营效率和管理水平。"),
          ],
        }),

        // 2. 项目目标
        new Paragraph({
          children: [
            new TextRun({ text: "2. 项目目标：", bold: true }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 实现财务、采购、销售、库存等核心模块的集成管理。"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 提高数据准确性和实时性，支持决策分析。"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 优化业务流程，提高工作效率。"),
          ],
        }),

        // 3. 项目时间表
        new Paragraph({
          children: [
            new TextRun({ text: "3. 项目时间表：", bold: true }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 第一阶段（1-2周）：需求分析与设计"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 第二阶段（3-4周）：核心模块开发"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 第三阶段（5-6周）：系统集成与测试"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 第四阶段（7-8周）：上线与培训"),
          ],
        }),

        // 4. 项目团队
        new Paragraph({
          children: [
            new TextRun({ text: "4. 项目团队：", bold: true }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 项目经理：张三"),
            new TextRun({ text: "", break: 1 }),  // 换行
            new TextRun("• 开发人员：李四、王五"),
            new TextRun({ text: "", break: 1 }),
            new TextRun("• 测试人员：赵六"),
          ],
        }),

        // 5. 预算
        new Paragraph({
          children: [
            new TextRun({ text: "5. 预算：", bold: true }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 总预算：￥200,000"),
            new TextRun({ text: "", break: 1 }),
            new TextRun("• 分配："),
            new TextRun({ text: "", break: 1 }),
            new TextRun("  - 需求分析（￥30,000）"),
            new TextRun({ text: "", break: 1 }),
            new TextRun("  - 开发（￥100,000）"),
            new TextRun({ text: "", break: 1 }),
            new TextRun("  - 测试（￥30,000）"),
            new TextRun({ text: "", break: 1 }),
            new TextRun("  - 上线与培训（￥40,000）"),
          ],
        }),

        // 6. 风险管理
        new Paragraph({
          children: [
            new TextRun({ text: "6. 风险管理：", bold: true }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 技术风险：采用成熟的技术框架，定期进行代码审查。"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 时间风险：合理安排时间表，预留缓冲时间。"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("• 成本风险：严格控制预算，避免不必要的开支。"),
          ],
        }),

        // 7. 项目里程碑
        new Paragraph({
          children: [
            new TextRun({ text: "7. 项目里程碑：", bold: true }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("✓ 完成需求分析"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("✓ 完成核心模块开发"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("✓ 完成系统集成与测试"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun("✓ 完成上线与培训"),
          ],
        }),
      ],
    },
  ],
});

// 保存文档
Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("ERP_计划书.docx", buffer);
  console.log("✅ 文档 'ERP_计划书.docx' 创建成功！");
});
