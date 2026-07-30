import requests
auth = ("lil766", "8774f768d2e2b2636269fe3ef28ed88a31168c47")
r = requests.get("https://openi.pcl.ac.cn/api/v1/repos/lil7/AtmoQuery/contents", auth=auth, timeout=10)
if r.status_code == 200:
    for item in r.json():
        print(f"{item['name']} ({item['type']})")
else:
    print(f"{r.status_code}: {r.text[:100]}")
