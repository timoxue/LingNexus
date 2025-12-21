import requests
import json

plugin_id = "com.lingnexus.intel.news-quick-search"
r = requests.get(f'http://localhost:8015/plugins/{plugin_id}/detail')
detail = r.json()

print('\n🔍 检查 input_schema 结构:\n')
print(f'input_schema 存在: {"input_schema" in detail}')

if 'input_schema' in detail:
    input_schema = detail['input_schema']
    print(f'\ninput_schema 类型: {type(input_schema)}')
    print(f'\ninput_schema 内容:')
    print(json.dumps(input_schema, indent=2, ensure_ascii=False))
    
    print(f'\n检查 properties 字段:')
    print(f'  "properties" in input_schema: {"properties" in input_schema}')
    
    if 'properties' in input_schema:
        print(f'  properties 类型: {type(input_schema["properties"])}')
        print(f'  properties keys: {list(input_schema["properties"].keys())}')
    else:
        print('  ❌ 缺少 properties 字段！')
        print(f'  input_schema 的 keys: {list(input_schema.keys())}')
