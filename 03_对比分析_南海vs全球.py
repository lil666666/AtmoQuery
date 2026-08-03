"""南海 vs 全球平均 vs 东海：增暖速率对比 + 2019跃变检测（用ERSST v5，下载快）"""
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
from scipy import stats
import os

OUTPUT_DIR = r"C:\Users\y7000\Desktop\AtmoQuery_competition"

# ===== 下载数据 =====
print("1. 下载ERSST v5海温数据...")
url = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc"
ds = xr.open_dataset(url, decode_times=False)
sst = ds['sst']

time_units = ds.time.units
times = xr.coding.times.decode_cf_datetime(ds.time.values, time_units)
dates = pd.to_datetime([str(t) for t in times])

# ERSST纬度从北到南
print(f"   纬度范围: {sst.lat.values[0]:.1f} ~ {sst.lat.values[-1]:.1f}")

def region_mean(lat_lo, lat_hi, lon_lo, lon_hi):
    """计算区域平均月海温（lat_lo<lat_hi，自动处理排序）"""
    d = sst.sel(lat=slice(max(lat_lo, lat_hi), min(lat_lo, lat_hi)), lon=slice(lon_lo, lon_hi)).mean(dim=['lat', 'lon'])
    vals = d.values.flatten()
    df = pd.DataFrame({'time': dates, 'sst': vals})
    df['year'] = df['time'].dt.year
    df['month'] = df['time'].dt.month
    df = df[(df['year'] >= 1982) & (df['year'] <= 2024)]
    df = df.dropna()
    return df

print("   加载南海北部 (15-23N, 110-120E)...")
scs = region_mean(15, 23, 110, 120)
print("   加载东海 (25-33N, 120-130E)...")
ecs = region_mean(25, 33, 120, 130)
print("   加载全球海洋 (60S-60N)...")
# ERSST经度是0-358，直接全选
glob = region_mean(-60, 60, 0, 360)

# ===== 计算年均值和趋势 =====
def annual_stats(df):
    a = df.groupby('year').agg(sst_mean=('sst', 'mean')).reset_index()
    return a[a['year'] <= 2024]

scs_a = annual_stats(scs)
ecs_a = annual_stats(ecs)
glob_a = annual_stats(glob)

def trend(data):
    slope, intercept, r, p, se = stats.linregress(data['year'], data['sst_mean'])
    return slope, p

slope_scs, p_scs = trend(scs_a)
slope_ecs, p_ecs = trend(ecs_a)
slope_glob, p_glob = trend(glob_a)

print("\n2. 增暖速率对比:")
print(f"   南海北部: {slope_scs*10:.3f}°C/十年 (p={p_scs:.4f})")
print(f"   东海:     {slope_ecs*10:.3f}°C/十年 (p={p_ecs:.4f})")
print(f"   全球海洋: {slope_glob*10:.3f}°C/十年 (p={p_glob:.4f})")
print(f"   南海/全球 比值: {slope_scs/slope_glob:.2f} 倍")

# ===== 2019年前后跃变 =====
print("\n3. 2019年前后跃变:")
for name, data in [("南海北部", scs_a), ("东海", ecs_a), ("全球海洋", glob_a)]:
    before = data[data['year'] < 2019]['sst_mean'].mean()
    after = data[data['year'] >= 2019]['sst_mean'].mean()
    print(f"   {name}: 2019前 {before:.2f}°C, 2019后 {after:.2f}°C, 跃变 +{after-before:.2f}°C")

# ===== 画图 =====
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# 图1: 三区域海温年际变化
ax1 = axes[0]
ax1.plot(scs_a['year'], scs_a['sst_mean'], 'b-', linewidth=2, label='南海北部 (15-23N)')
ax1.plot(ecs_a['year'], ecs_a['sst_mean'], 'g-', linewidth=1.5, alpha=0.8, label='东海 (25-33N)')
ax1.plot(glob_a['year'], glob_a['sst_mean'], 'k--', linewidth=1.5, label='全球海洋 (60S-60N)')
ax1.axvline(x=2019, color='red', linestyle=':', linewidth=2)
ax1.set_ylabel('SST (°C)')
ax1.set_title('南海北部 vs 东海 vs 全球海洋 海温年际变化 (1982-2024)')
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)

# 图2: 增暖速率柱状对比
ax2 = axes[1]
regions = ['南海北部', '东海', '全球海洋']
slopes = [slope_scs*10, slope_ecs*10, slope_glob*10]
colors = ['#2196F3', '#4CAF50', '#9E9E9E']
bars = ax2.bar(regions, slopes, width=0.5, color=colors)
ax2.set_ylabel('增暖速率 (°C/十年)')
ax2.set_title(f'增暖速率对比 (南海为全球平均的 {slope_scs/slope_glob:.1f} 倍)')
for bar, s in zip(bars, slopes):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
             f'{s:.3f}', ha='center', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 图3: 2019年前后各区域跃变幅度
ax3 = axes[2]
changes = []
for data in [scs_a, ecs_a, glob_a]:
    before = data[data['year'] < 2019]['sst_mean'].mean()
    after = data[data['year'] >= 2019]['sst_mean'].mean()
    changes.append(after - before)
bars2 = ax3.bar(regions, changes, width=0.5, color=['#FF5722', '#FF9800', '#BDBDBD'])
ax3.set_ylabel('2019年前后跃变幅度 (°C)')
ax3.set_title('2019年前后各区域海温跃变幅度对比')
for bar, c in zip(bars2, changes):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'+{c:.2f}', ha='center', fontsize=11, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, 'fig3_南海vs全球对比.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"\n✅ 图表已保存: {fig_path}")

# 保存数据
scs_a.to_csv(os.path.join(OUTPUT_DIR, 'data_南海_年.csv'), index=False)
ecs_a.to_csv(os.path.join(OUTPUT_DIR, 'data_东海_年.csv'), index=False)
glob_a.to_csv(os.path.join(OUTPUT_DIR, 'data_全球_年.csv'), index=False)
print("✅ 数据已保存")
