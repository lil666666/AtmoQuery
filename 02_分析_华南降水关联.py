"""下载华南降水数据，分析海温跃变前后的降水变化"""
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
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== 1. 下载GPCP降水数据 =====
print("1. 下载GPCP降水数据...")
url = "https://psl.noaa.gov/thredds/dodsC/Datasets/gpcp/precip.mon.mean.nc"
ds = xr.open_dataset(url, decode_times=False)
precip = ds['precip']
time_units = ds.time.units
time_vals = ds.time.values
times = xr.coding.times.decode_cf_datetime(time_vals, time_units)
dates = pd.to_datetime([str(t) for t in times])
print(f"   数据范围: {dates[0]} ~ {dates[-1]}")

# 华南区域
sc = precip.sel(lat=slice(22, 27), lon=slice(108, 120))
sc_precip = sc.mean(dim=['lat', 'lon'])
vals = sc_precip.values.flatten()

df_p = pd.DataFrame({'time': dates, 'precip': vals})
df_p['year'] = df_p['time'].dt.year
df_p['month'] = df_p['time'].dt.month
df_p = df_p[(df_p['year'] >= 1982) & (df_p['year'] <= 2024)]
print(f"   有效数据: {len(df_p)}个月")

# ===== 2. 分析降水变化 =====
df_pre = df_p[df_p['month'].isin([4, 5, 6])]
pre_sum = df_pre.groupby('year')['precip'].sum().reset_index()
pre_sum = pre_sum[pre_sum['year'] <= 2024]
years = pre_sum['year'].values

before_mask = years < 2019
after_mask = years >= 2019

pre_before = pre_sum[before_mask]['precip'].mean()
pre_after = pre_sum[after_mask]['precip'].mean()

print(f"\n2. 降水变化:")
print(f"   跃变前: {pre_before:.1f} mm")
print(f"   跃变后: {pre_after:.1f} mm")
print(f"   变化: {pre_after - pre_before:.1f} mm ({(pre_after-pre_before)/pre_before*100:.1f}%)")

# ===== 3. 海温-降水相关性 =====
sst_data = pd.read_csv(os.path.join(OUTPUT_DIR, 'data_南海北部海温月数据.csv'))
sst_annual = sst_data.groupby('year').agg(sst_mean=('sst', 'mean'), hw_months=('hw', 'sum')).reset_index()
sst_annual = sst_annual[sst_annual['year'] <= 2024]
merged = pd.merge(sst_annual, pre_sum, on='year')

corr = merged['sst_mean'].corr(merged['precip'])
corr_p = stats.pearsonr(merged['sst_mean'], merged['precip'])[1]
print(f"\n3. 海温-降水相关性: r={corr:.3f}, p={corr_p:.4f}")

# ===== 4. 画图 =====
fig, axes = plt.subplots(3, 1, figsize=(14, 14))

# 图1: 海温
ax1 = axes[0]
sst_vals = merged['sst_mean'].values
yrs = merged['year'].values
ax1.plot(yrs, sst_vals, 'b-o', markersize=4, linewidth=1.5)
ax1.axvline(x=2019, color='green', linestyle=':', linewidth=2, label='海温跃变(2019)')
ax1.fill_between(yrs[yrs<2019], 25, 29, alpha=0.1, color='blue', label='跃变前')
ax1.fill_between(yrs[yrs>=2019], 25, 29, alpha=0.1, color='red', label='跃变后')
ax1.set_ylabel('SST (°C)')
ax1.set_title('(a) 南海北部海温年际变化')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

# 图2: 跃变前后月度降水对比
ax2 = axes[1]
clim_before = df_p[df_p['year'] < 2019].groupby('month')['precip'].mean()
clim_after = df_p[df_p['year'] >= 2019].groupby('month')['precip'].mean()
months = range(1, 13)
ax2.plot(months, clim_before.values, 'b-', linewidth=2, marker='o', label='跃变前(1982-2018)')
ax2.plot(months, clim_after.values, 'r-', linewidth=2, marker='s', label='跃变后(2019-2024)')
ax2.fill_between(months, clim_before.values, clim_after.values, alpha=0.2, color='gray')
ax2.axvspan(4, 6, alpha=0.1, color='yellow', label='前汛期')
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'])
ax2.set_ylabel('降水 (mm)')
ax2.set_title(f'(b) 华南降水月变化对比')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 图3: 前汛期降水 + 热浪频次
ax3 = axes[2]
hw_vals = merged['hw_months'].values
ax3.bar(yrs, merged['precip'].values, color='steelblue', alpha=0.7, label='前汛期降水')
ax3_twin = ax3.twinx()
ax3_twin.plot(yrs, hw_vals, 'r-', linewidth=2, marker='s', label='热浪月数')
ax3_twin.set_ylabel('热浪月数', color='red')
ax3.set_xlabel('年份')
ax3.set_ylabel('前汛期降水 (mm)')
ax3.set_title(f'(c) 华南前汛期降水 vs 南海热浪频次 (r={corr:.2f})')
ax3.legend(loc='upper left')
ax3_twin.legend(loc='upper right')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, 'fig2_华南降水与海温关联.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"\n✅ 图表保存: {fig_path}")

# ===== 5. 更新关键发现 =====
with open(os.path.join(OUTPUT_DIR, '关键发现.txt'), 'a', encoding='utf-8') as f:
    f.write(f"\n\n===== 华南降水分析 =====\n")
    f.write(f"前汛期(4-6月)降水:\n")
    f.write(f"  跃变前: {pre_before:.1f} mm\n")
    f.write(f"  跃变后: {pre_after:.1f} mm\n")
    f.write(f"  增幅: {pre_after-pre_before:.1f} mm ({ (pre_after-pre_before)/pre_before*100:.1f}%)\n")
    f.write(f"海温-降水相关系数: r={corr:.3f}, p={corr_p:.4f}\n")

df_p.to_csv(os.path.join(OUTPUT_DIR, 'data_华南降水月数据.csv'), index=False, encoding='utf-8')
print("✅ 完成!")
