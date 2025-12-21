import requests

print('\n📡 测试 API 调用链路:\n')

# 测试 1: Plugin Runtime (8015)
print('1️⃣ 测试 Plugin Runtime (8015):')
try:
    r1 = requests.get('http://localhost:8015/store/plugins', timeout=5)
    print(f'   ✅ 状态码: {r1.status_code}')
    print(f'   ✅ 插件数量: {len(r1.json())}')
except Exception as e:
    print(f'   ❌ 错误: {e}')

print()

# 测试 2: Plugin Store Backend (8020)
print('2️⃣ 测试 Plugin Store Backend (8020):')
try:
    r2 = requests.get('http://localhost:8020/api/plugins', timeout=5)
    print(f'   ✅ 状态码: {r2.status_code}')
    print(f'   ✅ 插件数量: {len(r2.json())}')
except Exception as e:
    print(f'   ❌ 错误: {e}')

print()

# 测试 3: 前端能否访问 Backend
print('3️⃣ 测试前端 API 路径 (前端调用的地址):')
print('   前端配置应该调用: http://localhost:8020/api/plugins')
