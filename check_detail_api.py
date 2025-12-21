import requests
import json

plugin_id = "com.lingnexus.intel.daily-digest"
r = requests.get(f'http://localhost:8015/plugins/{plugin_id}/detail')
detail = r.json()

print(f'\n📄 插件详情数据结构:\n')
print(json.dumps(detail, indent=2, ensure_ascii=False))

print(f'\n🔍 检查 enabled 字段:')
print(f'  "enabled" in detail: {"enabled" in detail}')
print(f'  enabled 值: {detail.get("enabled", "字段不存在")}')
