"""上传文件到仓库根目录（确保公开可见）"""
import requests, base64, os

auth = ("lil766", "8774f768d2e2b2636269fe3ef28ed88a31168c47")
BASE = "https://openi.pcl.ac.cn/api/v1/repos/lil7/AtmoQuery/contents"
DIR = r"C:\Users\y7000\Desktop\AtmoQuery_competition"

files = [
    ("analysis_sst.py", os.path.join(DIR, "01_分析_南海海温与热浪.py"), "SST analysis code"),
    ("analysis_precip.py", os.path.join(DIR, "02_分析_华南降水关联.py"), "Precipitation analysis code"),
]

for name, local, msg in files:
    if not os.path.exists(local):
        continue
    with open(local, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    data = {"content": b64, "message": msg}
    r = requests.post(f"{BASE}/{name}", json=data, auth=auth, timeout=15)
    ok = "OK" if r.status_code in (200, 201) else f"FAIL({r.status_code})"
    print(f"{name}: {ok}")

# 验证
print("\n验证根目录文件:")
r = requests.get("https://openi.pcl.ac.cn/api/v1/repos/lil7/AtmoQuery/contents", auth=auth, timeout=10)
if r.status_code == 200:
    for item in r.json():
        print(f"  {item['name']} ({item['type']})")
