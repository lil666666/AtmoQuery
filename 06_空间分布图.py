"""空间分布：南海海温2019跃变幅度在每个格点上的分布"""
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
import os

OUTPUT_DIR = r"C:\Users\y7000\Desktop\AtmoQuery_competition"

print("1. 下载OISST v2高分辨率数据...")
url = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.mon.mean.nc"
ds = xr.open_dataset(url, decode_times=False)
sst = ds['sst']
time_units = ds.time.units
times = xr.coding.times.decode_cf_datetime(ds.time.values, time_units)
dates = pd.to_datetime([str(t) for t in times])
years = np.array([d.year for d in dates])

# 南海及周边区域
lat_lo, lat_hi = 5, 28
lon_lo, lon_hi = 100, 130
scs = sst.sel(lat=slice(lat_lo, lat_hi), lon=slice(lon_lo, lon_hi))

# 时间筛选
idx = (years >= 1982) & (years <= 2024)
scs = scs.isel(time=idx)
years_sel = years[idx]

# 分前后时期
before_idx = years_sel < 2019
after_idx = years_sel >= 2019
before = scs.isel(time=before_idx).mean(dim='time')
after = scs.isel(time=after_idx).mean(dim='time')

# 跃变幅度 = 2019后平均 - 2019前平均
change = after - before
print(f"   数据维度: {change.shape}")

# 画图
fig, ax = plt.subplots(figsize=(12, 8))

lons = scs.lon.values
lats = scs.lat.values
data = change.values

# 掩膜掉陆地（NaN）
masked = np.ma.masked_invalid(data)

vmax = 1.5
cmap = plt.cm.RdYlBu_r
norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

im = ax.pcolormesh(lons, lats, masked, cmap=cmap, norm=norm, shading='auto')

# 等高线
levels = [0.3, 0.5, 0.8, 1.0, 1.2]
cs = ax.contour(lons, lats, masked, levels=levels, colors='black', linewidths=0.5, linestyles='dashed')
ax.clabel(cs, fmt='%.1f', fontsize=8)

ax.set_xlabel('经度 (°E)')
ax.set_ylabel('纬度 (°N)')
ax.set_title('南海及周边海域 2019年前后海温跃变幅度 (°C)\n'
             '（正值为2019年后变暖，红色越深跃变越大）')
ax.grid(True, alpha=0.2)

cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('海温跃变幅度 (°C)')

plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, 'fig6_跃变空间分布.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"✅ 图表已保存: {fig_path}")

# 输出关键区域统计
print("\n===== 空间分布关键结果 =====")
# 南海北部核心区
core = change.sel(lat=slice(15, 23), lon=slice(110, 120))
print(f"南海北部核心区 (15-23N, 110-120E): 平均跃变 {core.values.mean():.2f}°C")
# 最大跃变位置
flat_idx = np.nanargmax(np.abs(data))
max_lat = lats[flat_idx // data.shape[1]]
max_lon = lons[flat_idx % data.shape[1]]
print(f"跃变幅度最大位置: 约 {max_lat:.1f}°N, {max_lon:.1f}°E")
# 华南沿岸海域
coast = change.sel(lat=slice(18, 24), lon=slice(110, 118))
print(f"华南沿岸海域 (18-24N, 110-118E): 平均跃变 {coast.values.mean():.2f}°C")
