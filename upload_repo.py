"""上传竞赛分析代码到OpenI仓库"""
import requests, os, base64

auth = ("lil766", "8774f768d2e2b2636269fe3ef28ed88a31168c47")
BASE = "https://openi.pcl.ac.cn/api/v1/repos/lil7/AtmoQuery/contents"
DIR = r"C:\Users\y7000\Desktop\AtmoQuery_competition"

def upload(path, content_b64, msg):
    data = {"content": content_b64, "message": msg}
    r = requests.post(f"{BASE}/{path}", json=data, auth=auth, timeout=15)
    ok = "OK" if r.status_code in (200, 201) else f"FAIL({r.status_code})"
    print(f"{path}: {ok}")
    if r.status_code not in (200, 201):
        print(f"  {r.text[:100]}")

# 1. 上传分析代码
for local_name, remote_name in [
    ("01_分析_南海海温与热浪.py", "analysis/sst_analysis.py"),
    ("02_分析_华南降水关联.py", "analysis/precip_analysis.py"),
]:
    local = os.path.join(DIR, local_name)
    if os.path.exists(local):
        with open(local, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        upload(remote_name, b64, f"upload {remote_name}")

# 2. 上传README
readme = "# AtmoQuery Competition Analysis\n\nAnalysis code for Earth Science track.\n\n## Files\n- sst_analysis.py: SST trend, marine heatwave detection, change point analysis\n- precip_analysis.py: Precipitation extraction, SST-precip correlation\n\n## Data\n- NOAA OISST v2 SST (auto-downloaded)\n- GPCP precipitation (auto-downloaded)"
upload("analysis/README.md", base64.b64encode(readme.encode()).decode(), "add readme")

# 3. 上传图表
for fname in ["fig1_南海北部海温与热浪变化.png", "fig2_华南降水与海温关联分析.png"]:
    local = os.path.join(DIR, fname)
    if not os.path.exists(local):
        local = os.path.join(DIR, fname.replace("分析_", ""))
    if os.path.exists(local):
        with open(local, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        upload(f"analysis/{fname}", b64, f"upload {fname}")

# 4. 上传关键发现
txt = os.path.join(DIR, "关键发现.txt")
if os.path.exists(txt):
    with open(txt, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    upload("analysis/findings.txt", b64, "upload findings")

print("\nDone!")
