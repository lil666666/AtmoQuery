"""检查并设置仓库为公开"""
import requests
auth = ("lil766", "8774f768d2e2b2636269fe3ef28ed88a31168c47")

# 检查仓库
r = requests.get("https://openi.pcl.ac.cn/api/v1/repos/lil7/AtmoQuery", auth=auth, timeout=10)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Name: {data['name']}")
    print(f"Private: {data['private']}")
    if data["private"]:
        r2 = requests.patch("https://openi.pcl.ac.cn/api/v1/repos/lil7/AtmoQuery",
            json={"private": False}, auth=auth, timeout=10)
        print(f"Set public: {r2.status_code}")
        if r2.status_code == 200:
            print("✅ 已设置为公开仓库")
        else:
            print(f"Failed: {r2.text[:100]}")
    else:
        print("✅ 已公开")

    # 检查analysis目录
    r3 = requests.get("https://openi.pcl.ac.cn/api/v1/repos/lil7/AtmoQuery/contents/analysis", auth=auth, timeout=10)
    print(f"\nAnalysis目录: {r3.status_code}")
    if r3.status_code == 200:
        for item in r3.json():
            print(f"  {item['name']} ({item['type']})")
