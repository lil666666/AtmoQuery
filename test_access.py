"""测试仓库各路径是否能匿名访问"""
import requests

base = "https://openi.pcl.ac.cn"
paths = [
    "/lil7/AtmoQuery",
    "/lil7/AtmoQuery/src/master/analysis",
    "/lil7/AtmoQuery/src/branch/master/analysis",
]
for p in paths:
    url = base + p
    r = requests.get(url, timeout=10, allow_redirects=True)
    reason = "✅" if r.status_code == 200 else "❌"
    if r.status_code == 200 and "login" not in r.url and "guest" not in r.url:
        reason = "✅ ACCESSIBLE"
    elif r.status_code == 200 and ("login" in r.url or "guest" in r.url):
        reason = "❌ REDIRECTED TO LOGIN"
    print(f"{reason} {p} ({r.status_code})")
