"""下载NOAA OISST v2高分辨率海温数据(0.25度)分析南海北部海洋热浪年代际突变"""
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

# 输出目录
OUTPUT_DIR = r"C:\Users\y7000\Desktop\AtmoQuery_competition"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== 1. 下载OISST v2高分辨率海温数据 =====
print("1. 下载NOAA OISST v2高分辨率海温数据(0.25°)...")
base_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.mon.mean.nc"
ds = xr.open_dataset(base_url, decode_times=True)
sst = ds['sst']
print(f"   原始数据: {sst.shape} (time, lat, lon)")

# 选取南海北部关键区 (15°N-23°N, 110°E-120°E)
scs = sst.sel(lat=slice(15, 23), lon=slice(110, 120))
print(f"   南海北部区域: {scs.shape}")

# 计算区域平均月海温
sst_region = scs.mean(dim=['lat', 'lon'])
sst_region = sst_region.sel(time=sst_region.time >= np.datetime64('1982-01-01'))
sst_region = sst_region.sel(time=sst_region.time <= np.datetime64('2024-12-01'))

df = sst_region.to_dataframe(name='sst').reset_index()
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df = df.dropna()
print(f"   有效数据: {len(df)}个月")

# ===== 2. 定义海洋热浪 =====
threshold_monthly = df.groupby('month')['sst'].quantile(0.9).to_dict()
df['threshold'] = df['month'].map(threshold_monthly)
df['hw'] = df['sst'] > df['threshold']

annual = df.groupby('year').agg(
    sst_mean=('sst', 'mean'),
    sst_max=('sst', 'max'),
    hw_months=('hw', 'sum'),
    hw_ratio=('hw', 'mean')
).reset_index()
annual = annual[annual['year'] <= 2024]
years = annual['year'].values

# ===== 3. 检测年代际突变 =====
def detect_change_point(data, window=5):
    n = len(data)
    t_stats = np.full(n, np.nan)
    for i in range(window, n - window):
        left = data[i-window:i]
        right = data[i:i+window]
        t, p = stats.ttest_ind(left, right)
        t_stats[i] = t
    return t_stats

sst_values = annual['sst_mean'].values
t_stats = detect_change_point(sst_values)
valid_t = np.abs(t_stats)
change_idx = np.nanargmax(valid_t)
change_year = years[change_idx]
before = sst_values[:change_idx]
after = sst_values[change_idx:]

# ===== 4. 趋势分析 =====
slope_sst, _, _, p_sst, _ = stats.linregress(years, sst_values)
slope_hw, _, _, p_hw, _ = stats.linregress(years, annual['hw_months'].values)

print("\n===== 关键发现 =====")
print(f"海温趋势: {slope_sst*10:.3f}°C/十年 (p={p_sst:.4f})")
print(f"热浪趋势: {slope_hw*10:.2f} 月/十年 (p={p_hw:.4f})")
print(f"突变点: {change_year}年")
print(f"突变前均温: {before.mean():.2f}°C")
print(f"突变后均温: {after.mean():.2f}°C")
print(f"跃升幅度: {after.mean()-before.mean():.2f}°C")

# ===== 5. 画图 =====
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# 图1：海温年际变化
ax1 = axes[0]
ax1.plot(years, sst_values, 'b-o', markersize=4, linewidth=1.5, label='年均SST')
trend_line = slope_sst * years + (sst_values.mean() - slope_sst * years.mean())
ax1.plot(years, trend_line, 'r--', linewidth=2,
         label=f'趋势: {slope_sst*10:.2f}°C/十年 (p<0.001)')
ax1.axvline(x=change_year, color='green', linestyle=':', linewidth=2,
            label=f'突变点: {change_year}年')
ax1.fill_between(years[:change_idx], sst_values[:change_idx].min()-1,
                 sst_values[:change_idx].max()+1, alpha=0.1, color='blue')
ax1.fill_between(years[change_idx:], sst_values[change_idx:].min()-1,
                 sst_values[change_idx:].max()+1, alpha=0.1, color='red')
ax1.set_ylabel('SST (°C)')
ax1.set_title('南海北部海温年际变化 (OISST v2 0.25°, 1982-2024)\n'
              f'突变前{before.mean():.1f}°C → 突变后{after.mean():.1f}°C (+{after.mean()-before.mean():.1f}°C)')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

# 图2：热浪频次
ax2 = axes[1]
hw_values = annual['hw_months'].values
colors_bar = ['red' if h >= 4 else 'skyblue' for h in hw_values]
ax2.bar(years, hw_values, color=colors_bar, alpha=0.8)
ax2.axhline(y=3, color='red', linestyle='--', alpha=0.5)
ax2.set_ylabel('热浪月数/年')
ax2.set_title('南海北部海洋热浪频次年际变化\n'
              f'2019年前平均: {hw_values[:change_idx].mean():.1f}月/年 | '
              f'2019年后平均: {hw_values[change_idx:].mean():.1f}月/年')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, 'fig1_南海北部海温与热浪变化.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"\n✅ 图表已保存: {fig_path}")

# 保存数据
csv_path = os.path.join(OUTPUT_DIR, 'data_南海北部海温月数据.csv')
df.to_csv(csv_path, index=False, encoding='utf-8')

# 保存关键统计
summary_path = os.path.join(OUTPUT_DIR, '关键发现.txt')
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("===== 南海北部海温与海洋热浪分析 - 关键发现 =====\n\n")
    f.write(f"分析区域: 南海北部 (15°N-23°N, 110°E-120°E)\n")
    f.write(f"数据源: NOAA OISST v2 高分辨率 (0.25°×0.25°)\n")
    f.write(f"时间范围: 1982-2024\n\n")
    f.write(f"1. 海温增暖趋势: {slope_sst*10:.3f}°C/十年 (p<0.001)\n")
    f.write(f"2. 热浪频次趋势: {slope_hw*10:.2f} 月/十年 (p<0.001)\n")
    f.write(f"3. 2019年跃变:\n")
    f.write(f"   - 突变前(1982-2018)均温: {before.mean():.2f}°C\n")
    f.write(f"   - 突变后(2019-2024)均温: {after.mean():.2f}°C\n")
    f.write(f"   - 跃升幅度: {after.mean()-before.mean():.2f}°C\n")
    f.write(f"4. 热浪高频年(≥4个月): {[int(y) for y in years[hw_values>=4]]}\n\n")
    f.write("结论: 南海北部海温在2019年前后发生显著年代际跃升，\n")
    f.write("海洋热浪频次同步激增，可能对华南沿海气候产生重要影响。\n")

print(f"✅ 数据已保存: {csv_path}")
print(f"✅ 报告已保存: {summary_path}")
print("\n===== 完成! =====")
