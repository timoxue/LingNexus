import asyncio
from shared.storage.es_client import ESClient
from shared.storage.es_query_medical import query_news_by_topic

async def test_search():
    es_client = ESClient(backend="local_file")
    
    print('\n🔍 测试 1: 搜索 "PD-1"')
    results = await query_news_by_topic(es_client, topic="PD-1", keywords=None, top_k=10)
    print(f'   结果数量: {len(results)}')
    for i, item in enumerate(results, 1):
        print(f'   {i}. {item.get("title", "无标题")}')
    
    print('\n🔍 测试 2: 搜索 "pd-1" (小写)')
    results = await query_news_by_topic(es_client, topic="pd-1", keywords=None, top_k=10)
    print(f'   结果数量: {len(results)}')
    for i, item in enumerate(results, 1):
        print(f'   {i}. {item.get("title", "无标题")}')
    
    print('\n🔍 测试 3: 使用 keywords')
    results = await query_news_by_topic(es_client, topic="癌症", keywords=["PD-1"], top_k=10)
    print(f'   结果数量: {len(results)}')
    for i, item in enumerate(results, 1):
        print(f'   {i}. {item.get("title", "无标题")}')
    
    print('\n🔍 测试 4: 空 keywords (应该搜索所有)')
    results = await query_news_by_topic(es_client, topic="药物", keywords=[], top_k=10)
    print(f'   结果数量: {len(results)}')

asyncio.run(test_search())
