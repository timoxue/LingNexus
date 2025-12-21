import requests

r = requests.get('http://localhost:8015/store/plugins')
plugins = r.json()

print(f'\n✅ 共发现 {len(plugins)} 个插件:\n')
for p in plugins:
    print(f"  🔹 {p['name']}")
    print(f"     ID: {p['plugin_id']}")
    print(f"     版本: {p['version']}")
    print(f"     描述: {p['description']}")
    print(f"     标签: {', '.join(p['tags'])}")
    print()
