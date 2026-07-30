"""清理旧项目文件，只保留竞赛相关内容"""
import requests, base64

auth = ("lil766", "8774f768d2e2b2636269fe3ef28ed88a31168c47")
BASE = "https://openi.pcl.ac.cn/api/v1/repos/lil7/AtmoQuery/contents"

# 要删除的旧文件
to_delete = [
    "main.py",
    "app.py",
    "requirements.txt",
    "README.md",
    "weather_data.csv",  # 空目录
    "data/weather_data.csv",
    "data",
    "knowledge/weather_cases.md",
    "knowledge",
]

for path in to_delete:
    # OpenI删除文件需要先获取SHA
    r = requests.get(f"{BASE}/{path}", auth=auth, timeout=10)
    if r.status_code == 200:
        sha = r.json().get("sha", "")
        if sha:
            r2 = requests.delete(f"{BASE}/{path}",
                json={"message": f"cleanup {path}", "sha": sha},
                auth=auth, timeout=15)
            status = "OK" if r2.status_code in (200, 201, 204) else f"FAIL({r2.status_code})"
            print(f"删除 {path}: {status}")
        else:
            # 可能是目录
            r2 = requests.delete(f"{BASE}/{path}",
                json={"message": f"cleanup {path}"},
                auth=auth, timeout=15)
            status = "OK" if r2.status_code in (200, 201, 204) else f"SKIP({r2.status_code})"
            print(f"删除 {path}: {status}")
    else:
        print(f"跳过 {path}: 不存在")

print("\n验证剩余文件:")
r = requests.get(f"{BASE}", auth=auth, timeout=10)
if r.status_code == 200:
    for item in r.json():
        out = f"  {item['name']} ({item['type']})"
        if item["name"] != "analysis":
            out += " ⚠️ 可能是旧文件"
        print(out)
