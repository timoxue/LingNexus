import requests

r = requests.get('http://localhost:8015/store/plugins')
plugins = r.json()

print('\n📊 插件状态检查:\n')
for p in plugins:
    status = '✅ 已启用' if p['enabled'] else '❌ 已禁用'
    print(f"  {p['name']}: {status}")
    print(f"     ID: {p['plugin_id']}")
    print(f"     enabled 字段值: {p['enabled']}")
    print()
