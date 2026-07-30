"""检查仓库公开状态和修复"""
import requests
auth = ("lil766", "8774f768d2e2b2636269fe3ef28ed88a31168c47")
base = "https://openi.pcl.ac.cn/api/v1/repos/lil7/AtmoQuery"

# 获取完整仓库信息
r = requests.get(base, auth=auth, timeout=10)
if r.status_code == 200:
    d = r.json()
    print(f"Name: {d['name']}")
    print(f"Private: {d['private']}")
    print(f"Permisson: {d.get('permissions', {}).get('push', '?')}")
    for k in ['private', 'is_private', 'visibility', 'internal']:
        if k in d:
            print(f"  {k}: {d[k]}")

# 尝试设为完全公开
payload = {"private": False}
r2 = requests.patch(base, json=payload, auth=auth, timeout=10)
print(f"\nPatch: {r2.status_code}")
if r2.status_code == 200:
    print("OK")
else:
    print(r2.text[:200])
