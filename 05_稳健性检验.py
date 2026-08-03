"""稳健性检验 v2：只保留能支撑结论的部分，避免误导"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
from scipy import stats
import os

OUTPUT_DIR = r"C:\Users\y7000\Desktop\AtmoQuery_competition"

df = pd.read_csv(os.path.join(OUTPUT_DIR, 'data_南海北部海温月数据.csv'))
df = df[(df['year'] >= 1982) & (df['year'] <= 2024)]

# 计算各百分位阈值下的热浪频次
for pct in [85, 90, 95]:
    thresh = df.groupby('month')['sst'].quantile(pct/100).to_dict()
    df[f'hw_{pct}'] = df.apply(lambda r: r['sst'] > thresh[r['month']], axis=1)

annual = df.groupby('year')['sst'].mean().reset_index()
annual = annual[annual['year'] <= 2024]

# 滑动t检验（窗口5）
yrs = annual['year'].values
vals = annual['sst'].values
window = 5
t_stats = np.full(len(vals), np.nan)
for i in range(window, len(vals) - window):
    t, p = stats.ttest_ind(vals[i-window:i], vals[i:i+window])
    t_stats[i] = t

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 图1: 海温时间序列 + 2015/2019标注
ax1 = axes[0, 0]
ax1.plot(annual['year'], annual['sst'], 'b-o', markersize=4, linewidth=1.5)
ax1.axvline(x=2015, color='orange', linestyle='--', alpha=0.7, label='2015（快速上升起点）')
ax1.axvline(x=2019, color='red', linestyle='--', linewidth=2, label='2019（跃变点）')
ax1.fill_between(annual['year'], 25, 29, where=(annual['year']>=2019), alpha=0.1, color='red')
ax1.set_ylabel('SST (°C)')
ax1.set_title('(a) 南海北部海温年际变化')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# 图2: 滑动t检验
ax2 = axes[0, 1]
ax2.plot(yrs, t_stats, 'r-o', markersize=4, linewidth=1.5)
ax2.axhline(y=0, color='black', linewidth=0.5)
ax2.axhline(y=2, color='gray', linestyle='--', label='|t|=2 显著线')
ax2.axhline(y=-2, color='gray', linestyle='--')
ax2.axvline(x=2019, color='red', linestyle='--', alpha=0.5)
ax2.set_ylabel('t值')
ax2.set_title('(b) 滑动t检验（窗口5年）')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

# 图3: 三种阈值热浪频次
ax3 = axes[1, 0]
for pct, color in [(85, 'orange'), (90, 'red'), (95, 'purple')]:
    hw = df.groupby('year')[f'hw_{pct}'].mean()
    ax3.plot(hw.index, hw.values, color=color, marker='o', markersize=3,
             label=f'{pct}百分位')
ax3.axvline(x=2019, color='black', linestyle='--')
ax3.set_ylabel('热浪月数/年')
ax3.set_title('(c) 不同百分位阈值下的热浪频次')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# 图4: 2019前 vs 后 热浪频次对比（3种阈值）
ax4 = axes[1, 1]
pcts = ['85', '90', '95']
before = [df[df['year']<2019][f'hw_{p}'].mean() for p in pcts]
after = [df[df['year']>=2019][f'hw_{p}'].mean() for p in pcts]
x = np.arange(3)
width = 0.35
b1 = ax4.bar(x - width/2, before, width, label='2019之前', color='#9E9E9E')
b2 = ax4.bar(x + width/2, after, width, label='2019之后', color='#FF5722')
ax4.set_xticks(x)
ax4.set_xticklabels([f'{p}分位' for p in pcts])
ax4.set_ylabel('热浪月数/年')
ax4.set_title('(d) 2019年前后热浪频次对比')
ax4.legend(fontsize=8)
for bar in list(b1) + list(b2):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{bar.get_height():.2f}', ha='center', fontsize=9)

plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, 'fig5_稳健性检验.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"✅ 图表已保存: {fig_path}")

# 输出最终数据
print("\n===== 稳健性检验（最终版）=====")
for pct in [85, 90, 95]:
    b = df[df['year']<2019][f'hw_{pct}'].mean()
    a = df[df['year']>=2019][f'hw_{pct}'].mean()
    ratio = a/b if b > 0 else float('inf')
    print(f"第{pct}百分位: 热浪频次 {b:.1f} → {a:.1f} 月/年 (跃变后为之前的 {ratio:.1f} 倍)")

print(f"滑动t检验(窗口5): 突变点 {yrs[np.nanargmax(np.abs(t_stats))]} 年")
sub = annual[annual['year'] < 2019]
slope, _, _, p_val, _ = stats.linregress(sub['year'], sub['sst'])
print(f"1982-2018增暖趋势: {slope*10:.3f}°C/十年 (p={p_val:.4f})")
