import json

with open('data/pharma_news.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'\n📰 测试数据库中的新闻 (共 {len(data)} 条):\n')

for i, item in enumerate(data, 1):
    print(f'{i}. {item.get("title", "无标题")}')
    # 检查是否包含 PD-1
    item_str = json.dumps(item, ensure_ascii=False).lower()
    if 'pd-1' in item_str or 'pd1' in item_str:
        print('   ✅ 包含 PD-1 相关内容')
    print()
