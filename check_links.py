"""验证代码链接是否有效"""
import requests

urls = [
    "https://openi.pcl.ac.cn/lil7/AtmoQuery/raw/branch/master/analysis_sst.py",
    "https://openi.pcl.ac.cn/lil7/AtmoQuery/raw/branch/master/analysis_precip.py",
]
for url in urls:
    r = requests.get(url, timeout=10, allow_redirects=True)
    name = url.split("/")[-1]
    if r.status_code == 200 and len(r.text) > 100:
        print(f"✅ {name}: {r.status_code}, {len(r.text)} 字节")
    else:
        print(f"❌ {name}: {r.status_code}")
        if r.status_code != 200:
            print(f"   {r.url[:80]}")
