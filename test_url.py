"""测试访问路径"""
import requests
paths = [
    "https://openi.pcl.ac.cn/lil7/AtmoQuery/src/branch/master/analysis",
    "https://openi.pcl.ac.cn/lil7/AtmoQuery/src/master/analysis",
    "https://openi.pcl.ac.cn/lil7/AtmoQuery/tree/master/analysis",
]
for p in paths:
    r = requests.get(p, timeout=10, allow_redirects=True)
    print(f"{r.status_code:3d} {p.split('/')[-1]} -> {r.url[:60]}")
