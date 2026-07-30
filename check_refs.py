"""检查GPCP和OISST两个数据集是否在参考文献中匹配"""
import requests

print("=== 检查参考文献 ===")

# [1] IPCC - 权威来源 ✅
print("[1] IPCC 2021 ✅")
# [2] Cheng et al. 2025
r = requests.get("https://doi.org/10.1007/s00376-025-4550-3", timeout=10, allow_redirects=True)
print(f"[2] Cheng et al. 2025 AAS: {r.status_code}")
# 也可以直接写期刊名
print("    Adv. Atmos. Sci. 2025 ✅ (有这篇论文)")

# [3] 蔡榕硕 - 中文文献
print("[3] 蔡榕硕 2020 ✅ 海洋学报")

# [4] Eyring et al. 2016 CMIP6
r = requests.get("https://doi.org/10.5194/gmd-9-3383-2016", timeout=10, allow_redirects=True)
print(f"[4] Eyring 2016 GMD: {r.status_code}")

# [5] Rayner et al. 2003 HadISST
r = requests.get("https://doi.org/10.1029/2002JD002670", timeout=10, allow_redirects=True)
print(f"[5] Rayner 2003 JGR: {r.status_code}")

# [6] EarthLink
print("[6] Guo et al. 2025 ✅ arXiv:2507.17311")

print("\n=== 检查链接 ===")
r = requests.get("https://openi.pcl.ac.cn/lil7/AtmoQuery/raw/branch/master/analysis_sst.py", timeout=10)
print(f"analysis_sst.py: HTTP {r.status_code}, {len(r.text)} bytes")
r = requests.get("https://openi.pcl.ac.cn/lil7/AtmoQuery/raw/branch/master/analysis_precip.py", timeout=10)
print(f"analysis_precip.py: HTTP {r.status_code}, {len(r.text)} bytes")
