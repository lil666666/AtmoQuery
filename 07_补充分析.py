"""补充分析：方差变化、季节/逐月趋势、Theil-Sen、Mann-Kendall、暖事件分布"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
from scipy import stats
from scipy.stats import mannwhitneyu, kruskal, theilslopes
import os

OUTPUT_DIR = r"C:\Users\y7000\Desktop\AtmoQuery_competition"

# ===== 读取数据 =====
df = pd.read_csv(os.path.join(OUTPUT_DIR, 'data_南海北部海温月数据.csv'))
df = df[(df['year'] >= 1982) & (df['year'] <= 2024)]

# 计算月气候态（1991-2020基准期）和距平
base = df[(df['year'] >= 1991) & (df['year'] <= 2020)]
clim = base.groupby('month')['sst'].mean()
df['anom'] = df.apply(lambda r: r['sst'] - clim[r['month']], axis=1)

# 分阶段
before = df[df['year'] < 2019]
after = df[df['year'] >= 2019]

print("===== 1. 2019前后方差变化 =====")
var_b = before['anom'].var()
var_a = after['anom'].var()
std_b = before['anom'].std()
std_a = after['anom'].std()
print(f"月异常方差: 前期 {var_b:.4f} → 后期 {var_a:.4f}")
print(f"月异常标准差: 前期 {std_b:.3f} → 后期 {std_a:.3f}")
# Levene检验（方差齐性）
lev_stat, lev_p = stats.levene(before['anom'], after['anom'])
print(f"Levene检验: stat={lev_stat:.2f}, p={lev_p:.4f} {'(显著)' if lev_p < 0.05 else '(不显著)'}")
print(f"方差比: {var_a/var_b:.2f}")

print("\n===== 2. Mann-Kendall趋势检验 =====")
def mk_test(x):
    """Mann-Kendall趋势检验"""
    n = len(x)
    s = 0
    for i in range(n-1):
        for j in range(i+1, n):
            s += np.sign(x[j] - x[i])
    var_s = (n*(n-1)*(2*n+5))/18
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return s, z, p

annual = df.groupby('year')['anom'].mean().reset_index()
annual = annual[annual['year'] <= 2024]

s, z, p = mk_test(annual['anom'].values)
print(f"年均距平 Mann-Kendall: S={s}, Z={z:.2f}, p={p:.4f} {'(显著增暖)' if p < 0.05 else ''}")

# 分阶段MK
s1, z1, p1 = mk_test(annual[annual['year']<2019]['anom'].values)
print(f"1982-2018 MK: Z={z1:.2f}, p={p1:.4f}")

print("\n===== 3. Theil-Sen稳健斜率 =====")
ts = theilslopes(annual['anom'].values, annual['year'].values)
print(f"年均距平 Theil-Sen斜率: {ts[0]*10:.3f}°C/10年")

# 全时段月距平趋势
print("\n===== 4. 全时段月距平趋势 =====")
x_vals = np.arange(len(df))
slope_all, intercept, r, p, se = stats.linregress(x_vals, df['anom'])
print(f"月距平线性趋势: {slope_all*120:.3f}°C/10年 (p={p:.4f})")

print("\n===== 5. 季节趋势 =====")
seasons = {'DJF': [12,1,2], 'MAM': [3,4,5], 'JJA': [6,7,8], 'SON': [9,10,11]}
season_results = {}
for name, months in seasons.items():
    sd = df[df['month'].isin(months)].copy()
    # DJF处理12月归属
    sd['season_year'] = sd['year']
    if name == 'DJF':
        sd.loc[sd['month'] == 12, 'season_year'] = sd['year'] + 1
    sa = sd.groupby('season_year')['anom'].mean().reset_index()
    sa = sa[(sa['season_year'] >= 1982) & (sa['season_year'] <= 2024)]
    sl, ic, rr, pp, se_ = stats.linregress(sa['season_year'], sa['anom'])
    b_mean = sa[sa['season_year']<2019]['anom'].mean()
    a_mean = sa[sa['season_year']>=2019]['anom'].mean()
    season_results[name] = (sl*10, pp, b_mean, a_mean, a_mean-b_mean)
    print(f"{name}: 趋势 {sl*10:.3f}°C/10年 (p={pp:.4f}), "
          f"2019前 {b_mean:.2f} → 后 {a_mean:.2f}, 差 +{a_mean-b_mean:.2f}°C")

print("\n===== 6. 逐月趋势 =====")
month_trends = []
for m in range(1, 13):
    md = df[df['month'] == m].copy()
    md = md.sort_values('year')
    sl, ic, rr, pp, se_ = stats.linregress(md['year'], md['sst'])
    month_trends.append((m, sl*10, pp))
    sig = '*' if pp < 0.05 else ''
    print(f"{m}月: {sl*10:.3f}°C/10年 (p={pp:.4f}){sig}")

print("\n===== 7. 暖异常事件分布 =====")
# 90百分位阈值（按历月）
thresh = df.groupby('month')['anom'].quantile(0.9)
df['hw_my'] = df.apply(lambda r: r['anom'] > thresh[r['month']], axis=1)

# 分布变化
print("月异常分布变化 (2019前后):")
for q in [0.5, 0.75, 0.9, 0.95, 0.99]:
    b_q = before['anom'].quantile(q)
    a_q = after['anom'].quantile(q)
    print(f"  {q*100:.0f}分位: 前期 {b_q:.2f} → 后期 {a_q:.2f} (差 {a_q-b_q:.2f})")

# 分布平移vs尾部
print(f"\n均值: 前期 {before['anom'].mean():.3f} → 后期 {after['anom'].mean():.3f}")
print(f"中位数: 前期 {before['anom'].median():.3f} → 后期 {after['anom'].median():.3f}")
print(f"上尾(P90): 前期 {before['anom'].quantile(0.9):.3f} → 后期 {after['anom'].quantile(0.9):.3f}")

# ===== 画图 =====
fig, axes = plt.subplots(3, 2, figsize=(14, 14))

# 图1: 方差变化（月异常分布箱线图）
ax1 = axes[0, 0]
data_box = [before['anom'].values, after['anom'].values]
bp = ax1.boxplot(data_box, labels=['2019前', '2019后'], patch_artist=True)
bp['boxes'][0].set_facecolor('#9E9E9E')
bp['boxes'][1].set_facecolor('#FF5722')
ax1.set_title(f'月异常分布对比 (Levene p={lev_p:.3f})')
ax1.set_ylabel('月异常 (°C)')

# 图2: 季节趋势
ax2 = axes[0, 1]
seasons_names = list(season_results.keys())
trends_s = [season_results[s][0] for s in seasons_names]
colors_s = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
bars = ax2.bar(seasons_names, trends_s, color=colors_s)
ax2.axhline(0, color='black', linewidth=0.5)
ax2.set_ylabel('趋势 (°C/10年)')
ax2.set_title('各季节月异常趋势 (1982-2024)')
for bar, t in zip(bars, trends_s):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.005,
             f'{t:.2f}', ha='center', fontsize=10)

# 图3: 逐月趋势
ax3 = axes[1, 0]
months_list = [t[0] for t in month_trends]
trends_m = [t[1] for t in month_trends]
colors_m = ['#FF5722' if t[2] < 0.05 else '#9E9E9E' for t in month_trends]
bars3 = ax3.bar(months_list, trends_m, color=colors_m)
ax3.axhline(0, color='black', linewidth=0.5)
ax3.set_xlabel('月份')
ax3.set_ylabel('趋势 (°C/10年)')
ax3.set_title('各月海温长期趋势 (红色=显著)')
ax3.set_xticks(range(1, 13))

# 图4: 分布PDF
ax4 = axes[1, 1]
bins = np.linspace(-2.5, 3, 50)
ax4.hist(before['anom'], bins=bins, alpha=0.5, color='gray', density=True, label='2019前')
ax4.hist(after['anom'], bins=bins, alpha=0.5, color='red', density=True, label='2019后')
ax4.axvline(before['anom'].mean(), color='gray', linestyle='--', label='前均值')
ax4.axvline(after['anom'].mean(), color='red', linestyle='--', label='后均值')
ax4.set_xlabel('月异常 (°C)')
ax4.set_ylabel('概率密度')
ax4.set_title('月异常概率分布变化')
ax4.legend(fontsize=8)

# 图5: 暖事件频次
ax5 = axes[2, 0]
hw_annual = df.groupby('year')['hw_my'].sum()
ax5.bar(hw_annual.index, hw_annual.values, color='skyblue')
ax5.axvline(x=2019, color='red', linestyle='--')
ax5.set_xlabel('年份')
ax5.set_ylabel('暖异常月数/年')
ax5.set_title('暖异常月数年际变化 (90分位阈值)')

# 图6: 暖事件前后对比
ax6 = axes[2, 1]
before_hw = before.merge(df[['hw_my']], left_index=True, right_index=True)
after_hw = after.merge(df[['hw_my']], left_index=True, right_index=True)
hw_b = before_hw['hw_my'].sum() / len(before_hw) * 100
hw_a = after_hw['hw_my'].sum() / len(after_hw) * 100
bars6 = ax6.bar(['2019前', '2019后'], [hw_b, hw_a],
                color=['#9E9E9E', '#FF5722'], width=0.5)
ax6.set_ylabel('暖异常月占比 (%)')
ax6.set_title('暖异常月占比对比')
for bar, v in zip(bars6, [hw_b, hw_a]):
    ax6.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
             f'{v:.1f}%', ha='center', fontsize=11)

plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, 'fig7_补充分析.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"\n✅ 图表已保存: {fig_path}")

print("\n===== 结论 =====")
print(f"1. 方差: 2019后标准差 {std_b:.3f}→{std_a:.3f}, {'增大' if std_a > std_b else '减小'}, Levene p={lev_p:.3f}")
print(f"2. 增暖方向: Mann-Kendall p={p:.4f}")
print(f"3. Theil-Sen斜率: {ts[0]*10:.3f}°C/10年")
print(f"4. 暖事件占比: {hw_b:.1f}% → {hw_a:.1f}%")