#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 23:45:44 2026

@author: chenyan
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 14:48:06 2025

@author: chenyan
"""
#CTSM
%matplotlib qt5
import glob
from netCDF4 import Dataset, num2date
import numpy as np
from datetime import datetime
import pandas as pd
import xarray as xr

# file_list = sorted(glob.glob("/Users/chenyan/Desktop/CESM/test0803/ENF/RMNP/RHconstant100/*03600.nc"))
# file_list = sorted(glob.glob("/Users/chenyan/Desktop/CESM/test0803/ENF/ABBY/TBOTminus5/*03600.nc"))
file_list = sorted(glob.glob("/Users/chenyan/Desktop/Project/TALL/transient/*3600.nc"))
ds = xr.open_dataset(file_list[0])
print(file_list)
print(len(file_list))
print("Variables:", ds.data_vars)

gpp_all = []
h2osoi_all = []
tbot_all = []
levsoi_all = []
time_all = []
AR_all = []
HR_all = []
Qh_all = []
EFLX_LH_TOT_all = []
ELAI_all = []
FCEV_all = []
FCTR_all = []
FGEV_all = []
TAF_all = []

for file in file_list:
    with Dataset(file, 'r') as ds:
        var_keys = ds.variables.keys()
        # if all(var in var_keys for var in ['GPP','time']):
        # if all(var in var_keys for var in ['QVEGT','QVEGE','QSOIL','QDRAI_XS','QFLX_SNOW_DRAIN','QFLX_SNOW_DRAIN_ICE','AR','VCMX25T','Vcmx25Z','GPP', 'H2OSOI', 'TBOT', 'ELAI','TAF','VEGWP','GSSHA','GSSUN','levsoi','time','EFLX_LH_TOT','Qh','QDRAI','QOVER','QDRAI_PERCH']):
        # if all(var in var_keys for var in ['GPP', 'H2OSOI', 'SOILPSI','BTRANMN','SMP','TBOT', 'TAF','VEGWP','GSSHA','GSSUN','levsoi','time']):
        if all(var in var_keys for var in ['GPP', 'H2OSOI', 'TBOT','levsoi','AR','HR', 'Qh','EFLX_LH_TOT','ELAI','FCEV','FCTR','FGEV','TAF','time']):
        # if all(var in var_keys for var in ['FPSN', 'H2OSOI', 'VEGWP', 'GSSHA', 'GSSUN', 'levsoi', 'time']):
            time_vals = ds.variables['time'][:]
            time_units = ds.variables['time'].units
            calendar = ds.variables['time'].calendar if 'calendar' in ds.variables['time'].ncattrs() else 'standard'
            if len(time_vals) == 0:
               print(f"⚠️ time 变量为空: {file}")
               continue

            time_dates = num2date(time_vals, units=time_units, calendar=calendar)

            # 筛选2018-2023时间
            valid_idx = [i for i, d in enumerate(time_dates) if 2018 <= d.year < 2024]
            # valid_idx = [i for i, d in enumerate(time_dates) if 2018 <= d.year <= 2023 and d.month in [6, 7, 8]]
            # valid_idx = [i for i, d in enumerate(time_dates) if 2018 <= d.year < 2024 and d.month in [6, 7, 8] and 7 <= d.hour <= 16]

            if not valid_idx:
                print(f"⚠️ No valid time steps in 2018–2023 in {file}")
                continue

            gpp = ds.variables['GPP'][valid_idx]
            h2osoi = ds.variables['H2OSOI'][valid_idx]
            tbot = ds.variables['TBOT'][valid_idx]
            levsoi = ds.variables['levsoi'][:]  # 土壤层一般不变，直接取
            AR = ds.variables['AR'][valid_idx]
            HR = ds.variables['HR'][valid_idx]
            Qh = ds.variables['Qh'][valid_idx]
            EFLX_LH_TOT = ds.variables['EFLX_LH_TOT'][valid_idx]
            ELAI = ds.variables['ELAI'][valid_idx]
            FCEV = ds.variables['FCEV'][valid_idx]
            FCTR = ds.variables['FCTR'][valid_idx]
            FGEV = ds.variables['FGEV'][valid_idx]
            TAF = ds.variables['TAF'][valid_idx]

            gpp_all.append(gpp)
            h2osoi_all.append(h2osoi)
            tbot_all.append(tbot)
            levsoi_all.append(levsoi)
            AR_all.append(AR)
            HR_all.append(HR)
            Qh_all.append(Qh)
            EFLX_LH_TOT_all.append(EFLX_LH_TOT)
            ELAI_all.append(ELAI)
            FCEV_all.append(FCEV)
            FCTR_all.append(FCTR)
            FGEV_all.append(FGEV)
            TAF_all.append(TAF)
            # QFLX_SNOW_DRAIN_ICE_all.append(QFLX_SNOW_DRAIN_ICE)
            # QSOIL_all.append(QSOIL)
            # QVEGE_all.append(QVEGE)
            # QVEGT_all.append(QVEGT)
            # SH_all.append(SH)
            # LH_all.append(LH)
            # ELAI_all.append(ELAI)
            # BTRAN_all.append(BTRAN)
            # VCMX25T_all.append(VCMX25T)
            # Vcmx25Z_all.append(Vcmx25Z)
            # AR_all.append(AR)
            # PRECT_all.append(PRECT)
            # SOILPSI_all.append(SOILPSI)
            # BTRANMN_all.append(BTRANMN)
            # SMP_all.append(SMP)
            
            time_all.extend([time_dates[i] for i in valid_idx])
        else:
            print(f"❌ Missing variables in {file}")

print(f"Loaded {len(gpp_all)} files with valid data from 2018–2023.")

# 拼接时间和变量
gpp_all = np.concatenate(gpp_all, axis=0)
h2osoi_all = np.concatenate(h2osoi_all, axis=0)
tbot_all = np.concatenate(tbot_all, axis=0)
levsoi_all = np.concatenate(levsoi_all, axis=0)
TAF_all = np.concatenate(TAF_all, axis=0)
AR_all = np.concatenate(AR_all, axis=0)
HR_all = np.concatenate(HR_all, axis=0)
Qh_all = np.concatenate(Qh_all, axis=0)
EFLX_LH_TOT_all = np.concatenate(EFLX_LH_TOT_all, axis=0)
ELAI_all = np.concatenate(ELAI_all, axis=0)
FCEV_all = np.concatenate(FCEV_all, axis=0)
FCTR_all = np.concatenate(FCTR_all, axis=0)
FGEV_all = np.concatenate(FGEV_all, axis=0)
time_all = np.array(time_all)

# 时间排序及去重（防止重复时间）
unique_times, unique_indices = np.unique(time_all, return_index=True)
unique_sorted_indices = np.sort(unique_indices)
time_all_unique_sorted = time_all[unique_sorted_indices]
gpp_all_unique_sorted = gpp_all[unique_indices]
h2osoi_all_unique_sorted = h2osoi_all[unique_indices]
tbot_all_unique_sorted = tbot_all[unique_indices]
TAF_all_unique_sorted = TAF_all[unique_indices]
TAF_all_unique_sorted = TAF_all_unique_sorted.ravel()
AR_all = np.array(AR_all)
AR_all_unique_sorted = AR_all[unique_indices][:, 0]
type(VEGWP_all)
# VEGWP_all_unique_sorted = VEGWP_all_unique_sorted.ravel()
HR_all_unique_sorted = HR_all[unique_indices]
HR_all_unique_sorted = HR_all_unique_sorted.ravel()
Qh_all_unique_sorted = Qh_all[unique_indices]
Qh_all_unique_sorted = Qh_all_unique_sorted.ravel()
EFLX_LH_TOT_all_unique_sorted = EFLX_LH_TOT_all[unique_indices]
EFLX_LH_TOT_all_unique_sorted = EFLX_LH_TOT_all_unique_sorted.ravel()
ELAI_all_unique_sorted = ELAI_all[unique_indices]
ELAI_all_unique_sorted = ELAI_all_unique_sorted.ravel()
FCEV_all_unique_sorted = FCEV_all[unique_indices]
FCEV_all_unique_sorted = FCEV_all_unique_sorted.ravel()
FCTR_all_unique_sorted = FCTR_all[unique_indices]
FCTR_all_unique_sorted = FCTR_all_unique_sorted.ravel()
FGEV_all_unique_sorted = FGEV_all[unique_indices]
FGEV_all_unique_sorted = FGEV_all_unique_sorted.ravel()

print(f"原始时间点数: {len(time_all)}, 去重后时间点数: {len(time_all_unique_sorted)}")

tbot_all_unique_sorted = np.ravel(tbot_all_unique_sorted)  # 变成 (100,)
# 或者
gpp_all_unique_sorted = gpp_all_unique_sorted.flatten()
tbot_all_unique_sorted = tbot_all_unique_sorted.squeeze()
h2osoi_avg12_all_unique_sorted = np.concatenate(h2osoi_avg12, axis=0)
h2osoi_avg12_all_unique_sorted.shape
TAF_all_unique_sorted = TAF_all_unique_sorted.squeeze()
AR_all_unique_sorted = AR_all_unique_sorted.squeeze()
HR_all_unique_sorted = HR_all_unique_sorted.squeeze()
Qh_all_unique_sorted = Qh_all_unique_sorted.squeeze()
EFLX_LH_TOT_all_unique_sorted = EFLX_LH_TOT_all_unique_sorted.squeeze()
ELAI_all_unique_sorted = ELAI_all_unique_sorted.squeeze()
FCEV_all_unique_sorted = FCEV_all_unique_sorted.squeeze()
FCTR_all_unique_sorted = FCTR_all_unique_sorted.squeeze()
FGEV_all_unique_sorted = FGEV_all_unique_sorted.squeeze()

# 如果时间点数多于标准小时数，说明有重复或更高频率，进行重采样平均
if len(time_all_unique_sorted) > expected_hours:
    print(f"时间点过多，进行重采样成小时数据")

    # 构造DataFrame方便重采样
    df = pd.DataFrame({
        'datetime': pd.to_datetime(time_all_unique_sorted),
        'GPP': gpp_all_unique_sorted,
        'H2OSOI': h2osoi_all_unique_sorted,
        'TBOT': tbot_all_unique_sorted,
        'TAF': TAF_all_unique_sorted,
        'TLAI': TLAI_all_unique_sorted,
        'ELAI': ELAI_all_unique_sorted
    })
    df.set_index('datetime', inplace=True)

    # 以小时重采样并平均
    df_hourly = df.resample('1H').mean()

    print(f"重采样后时间点数: {len(df_hourly)}")
    print(df_hourly.head())

else:
    print("时间点数量正常，无需重采样")

levsoi_top12 = levsoi_all[:12]
h2osoi_top12 = h2osoi_all_unique_sorted[:,: 12]                   # shape: (time, 7)
weights = levsoi_top12 / levsoi_top12.sum()
weights = weights.data  # 取出底层的 numpy array，去掉 mask
# weights = weights / weights.sum()  # 再归一化一次确保和为1
h2osoi_avg12 = np.average(h2osoi_top12, axis=1, weights=weights)   # shape: (time,)
print(h2osoi_top12.shape)

levsoi_top12 = levsoi_all[:12]
h2osoi_top12 = h2osoi_all_unique_sorted[:,: 12]                   # shape: (time, 7)
weights = levsoi_top12 / levsoi_top12.sum()
weights = weights.data  # 取出底层的 numpy array，去掉 mask
# weights = weights / weights.sum()  # 再归一化一次确保和为1
h2osoi_avg12 = np.average(h2osoi_top12, axis=1, weights=weights)   # shape: (time,)
print(h2osoi_top12.shape)


h2osoi_layerNEONST = h2osoi_all_unique_sorted[:, :, 0]
print(h2osoi_all_unique_sorted.shape)

time_flat = pd.to_datetime(time_all)
#SP
type(time_all[0])

#12 layers H2OSOI
h2osoi = np.squeeze(h2osoi_top12)  
h2osoi_dict = {}
for i in range(12):
    h2osoi_dict[f'H2OSOI{i+1}'] = h2osoi[:, i]

h2osoi_dict_prefixed = {f"H2OSOI{i+1}": v for i, (k, v) in enumerate(h2osoi_dict.items())}

df_TALL = pd.DataFrame({
    'datetime': pd.to_datetime(time_flat),
    'GPP': gpp_all_unique_sorted,
    'H2OSOI12TOT': h2osoi_avg12_all_unique_sorted,
    'TAF': TAF_all_unique_sorted,
    'AR': AR_all_unique_sorted,
    'QOVER': QOVER_all_unique_sorted,
    'HR': HR_all_unique_sorted,
    'Qh': Qh_all_unique_sorted,
    'EFLX_LH_TOT': EFLX_LH_TOT_all_unique_sorted,
    'ELAI': ELAI_all_unique_sorted,
    'FCEV': FCEV_all_unique_sorted,
    'FCTR': FCTR_all_unique_sorted,
    'FGEV': FGEV_all_unique_sorted,
    **h2osoi_dict_prefixed
})


df_TALL = df_TALL.set_index('datetime')
df_TALL = df_TALL.resample('H').mean()
# df['datetime'] = pd.to_datetime(df['datetime'])
# df = df.set_index('datetime')
# print(df.index.min(), df.index.max())
# df_TALL.index = df_TALL.index.tz_localize('UTC').tz_convert('America/New_york')
df_TALL.index = df_TALL.index.tz_localize('UTC').tz_convert('America/Chicago')
mask = (df_TALL.index >= '2018-01-01') & (df_TALL.index <= '2023-12-31 16:00:00')
df_TALL = df_TALL.loc[mask].copy()

df_GRSM_Default["LUE"] = df_GRSM_Default["GPP"]  / df_NEONGRSM["ELAI"]
df_GRSM_NEONST["LUE"] = df_NEONGRSM["GPP"]/ df_NEONGRSM["ELAI"]
df_GRSM_NEONSTRH100["LUE"] = df_GRSM_NEONSTRH100["GPP"]/ df_GRSM_NEONSTRH100["ELAI"]
df_GRSM_NEONSTTminus2["LUE"] = df_GRSM_NEONSTTminus2["GPP"]/ df_GRSM_NEONSTRH100["ELAI"]

dfTBOTminus5["TBOT"] = dfTBOTminus5["TBOT"] -273.15
dfdefault["TAF"] = dfdefault["TAF"] -273.15

df_check = pd.DataFrame({
    'time': time_flat,
    'QDRAI': QDRAI_all_unique_sorted
})
print(df_check.head(20))

import numpy as np

# 相对湿度固定为 70% = 0.7
RH = 1

# 转换温度
Tc = df_selected["TBOT"] - 273.15  

# 饱和水汽压 (kPa)
es = 0.6108 * np.exp((17.27 * Tc) / (Tc + 237.3))

# 实际水汽压 (kPa)
ea = es * RH  

# VPD (kPa)
df_selected["VPD"] = es - ea

print(df_selected[["TBOT", "VPD"]].head())


import matplotlib.pyplot as plt

fig, ax1 = plt.subplots(figsize=(12, 6))

# 左轴：GPP
ax1.plot(df.index, df["GPP"], color='tab:green', linestyle='-')
ax1.set_xlabel('Date')
ax1.set_ylabel('Hourly GPP', color='tab:green')
ax1.tick_params(axis='y', labelcolor='tab:green')
ax1.set_ylim(0,0.000045)
# 右轴：TBOT
ax2 = ax1.twinx()
ax2.plot(df_new1.index, df_new1["VPD"], color='tab:blue', linestyle='--')
ax2.set_ylabel('VPD', color='tab:red')
ax2.tick_params(axis='y', labelcolor='tab:red')
ax2.set_ylim(0,10)
plt.grid(True)
plt.tight_layout()
plt.show()

NEON_sample = NEON_sample[(NEON_sample.index >= '2020-06-03') & (NEON_sample.index <= '2020-06-17')]
df = df[(df.index >= '2020-06-03') & (df.index <= '2020-06-17 23:59:59')]

# 筛选时间段：2023-06-06 到 2023-06-12
mask = (df['datetime'] >= '2018-01-01') & (df['datetime'] <= '2024-12-31')
df_selected = df.loc[mask].copy()
df['hour'] = df['datetime'].dt.hour
import matplotlib.pyplot as plt
# 初始化 anomaly 列
for col in ['GPP', 'TBOT', 'H2OSOI']:
    # 按小时计算 mean 和 std
    hourly_stats = df.groupby('hour')[col].agg(['mean', 'std']).rename(columns={'mean': 'mean_val', 'std': 'std_val'})
    df = df.merge(hourly_stats, left_on='hour', right_index=True)
    
    # 标准化 anomaly
    df[f'{col}_anom'] = (df[col] - df['mean_val']) / df['std_val']
    
    # 清理临时列
    df.drop(['mean_val', 'std_val'], axis=1, inplace=True)
    
fig, axs = plt.subplots(3, 2, figsize=(15, 10), sharex=True)
variables = ['GPP', 'TBOT', 'H2OSOI']

for i, var in enumerate(variables):
    # 原始时间序列
    axs[i, 0].plot(df_selected['datetime'], df_selected[var], label=var)
    axs[i, 0].set_ylabel(var)
    axs[i, 0].set_title(f'{var} Time Series')
    axs[i, 0].grid(True)

    # hourly-based standardized anomaly
    axs[i, 1].plot(df_selected['datetime'], df_selected[f'{var}_anom'], color='orange', label=f'{var} Anomaly')
    axs[i, 1].axhline(0, color='gray', linestyle='--', linewidth=1)
    axs[i, 1].set_ylabel('Anomaly')
    axs[i, 1].set_title(f'{var} Hourly-based Standardized Anomaly')
    axs[i, 1].grid(True)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
df['date'] = df['datetime'].dt.date
df['hour'] = df['datetime'].dt.hour
print(df.groupby(['date', 'hour']).size().unstack().head())
df_selected['datetime_hour'] = df_selected['datetime'].dt.floor('H')
import matplotlib.pyplot as plt


# 选择感兴趣时间段（如：2023-06-06 到 2023-06-12）
mask = (df['datetime'] >= '2023-06-06') & (df['datetime'] <= '2023-06-12')
df_selected = df.loc[mask].copy()

# 开始绘图
fig, axs = plt.subplots(3, 2, figsize=(16, 10), sharex=True)
variables = ['GPP', 'TBOT', 'H2OSOI']

for i, var in enumerate(variables):
    # 左侧：原始时间序列
    axs[i, 0].plot(df_plot['datetime_hour'], df_selected[var], color='steelblue')
    axs[i, 0].set_title(f"{var} Time Series")
    axs[i, 0].set_ylabel(var)
    axs[i, 0].grid(True)

    # 右侧：标准化 anomaly 时间序列
    axs[i, 1].plot(df_plot['datetime_hour'], df_plot[f'{var}_anom'], color='darkorange')
    axs[i, 1].axhline(0, color='gray', linestyle='--', linewidth=1)
    axs[i, 1].set_title(f"{var} Hourly-based Standardized Anomaly")
    axs[i, 1].set_ylabel("Anomaly")
    axs[i, 1].grid(True)

# x轴共享 + 优化格式
axs[2, 0].set_xlabel("datetime_hour")
axs[2, 1].set_xlabel("datetime_hour")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
print(df_selected.shape)
NEON_sample = NEON_sample[(NEON_sample['datetime_hour'] >= '2023-06-06') & (NEON_sample['datetime_hour'] <= '2023-06-12')]
print(df['datetime_hour'].min(), df['datetime_hour'].max())
df_plot = df_selected.groupby('datetime_hour').mean().reset_index()

df = pd.DataFrame({
    'time': time_all_unique_sorted,
    'gpp': gpp_all_unique_sorted
})
df['month'] = df['time'].dt.month
df['day'] = df['time'].dt.day
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))
plt.plot(time_all_unique_sorted, gpp_anom, label='GPP Standardized Anomaly', color='darkgreen')
plt.axhline(0, color='gray', linestyle='--', linewidth=1)
plt.xlabel('Time')
plt.ylabel('Standardized Anomaly')
plt.title('GPP Standardized Anomaly (2018–2023)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.legend()
plt.show()

# 你可以接着用 df_hourly 进行后续分析或保存

# 示例保存
# df_hourly.to_csv("model_output_hourly_2018_2023.csv")

#NEON VPD TBOT
from netCDF4 import Dataset, num2date
import numpy as np
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import glob
%matplotlib qt5

ds = Dataset("/Users/chenyan/Desktop/CESM/testnew/1/ABBY/NEON_ABBY/ABBY_Eve/ABBY.nc", "r")
print(ds.variables.keys())  
time_var = ds.variables['time']
time_all = num2date(time_var[:], units=time_var.units, calendar='standard')
time_all = np.array(time_all)

# 先创建掩码
start_date = datetime(2018, 1, 1)
end_date = datetime(2024, 12, 31)

mask = np.array([(d >= start_date) and (d <= end_date) for d in time_all])

# mask = np.array([
#     (2018 <= d.year < 2024) and (d.month in [6, 7, 8]) and (7 <= d.hour <= 16)
#     for d in time_all
# ])
# 应用掩码筛选时间
# mask = np.array([(d.year >= 2023 and d.year <= 2023 and d.month in [6, 7, 8]) for d in time_all])

time_selected = time_all[mask]

# 如果时间点数不是偶数，直接丢弃最后一个时间点及掩码对应的最后一个True
if len(time_selected) % 2 != 0:
    # 找到掩码中最后一个 True 的索引
    true_indices = np.where(mask)[0]
    last_true_index = true_indices[-1]

    # 把最后一个 True 变成 False，丢弃对应数据
    mask[last_true_index] = False

    # 重新筛选时间
    time_selected = time_all[mask]

target_vars = ['GPP', 'VPD']
NEONevahourly_data = {}

for varname in target_vars:
    if varname not in ds.variables:
        print(f"⚠️ 变量 {varname} 不存在，跳过")
        continue

    var = ds.variables[varname][:]
    var_selected = var[mask]

    # 再检查长度
    if len(var_selected) % 2 != 0:
        # 这里通常不会再发生，但万一出现，截断最后一个
        var_selected = var_selected[:-1]

    # 按2个半小时合并成1小时平均
    var_hourly = var_selected.reshape(-1, 2).mean(axis=1)

    NEONevahourly_data[varname] = var_hourly
    print(f"✅ 处理完成: {varname}, 小时长度: {len(var_hourly)}")

# 小时时间戳
time_hourly = time_selected[::2]
print(f"小时时间点数: {len(time_hourly)}")
print(f"{varname} 原始形状: {var.shape}, 筛选后形状: {var_selected.shape}, 合并后小时数据形状: {var_hourly.shape}")

#NEON_atm TBOT RH
ds1 = Dataset("/Users/chenyan/Desktop/CESM/testnew/1/ABBY/NEON_ABBY/ABBY_Atm/ABBY_atm.nc", "r")
print(ds1.variables.keys())  
time_var = ds1.variables['time']
time_all = num2date(time_var[:], units=time_var.units, calendar='standard')
time_all = np.array(time_all)

# 先创建掩码
mask = np.array([(d.year >= 2018 and d.year <= 2023 and d.month in [6, 7, 8]) for d in time_all])
# mask = np.array([
#     (2018 <= d.year < 2024) and (d.month in [6, 7, 8]) and (7 <= d.hour <= 16)
#     for d in time_all
# ])
# 应用掩码筛选时间
time_selected = time_all[mask]

# 如果时间点数不是偶数，直接丢弃最后一个时间点及掩码对应的最后一个True
if len(time_selected) % 2 != 0:
    # 找到掩码中最后一个 True 的索引
    true_indices = np.where(mask)[0]
    last_true_index = true_indices[-1]

    # 把最后一个 True 变成 False，丢弃对应数据
    mask[last_true_index] = False

    # 重新筛选时间
    time_selected = time_all[mask]

target_vars = ['RH', 'TBOT']
NEONatmhourly_data = {}

for varname in target_vars:
    if varname not in ds1.variables:
        print(f"⚠️ 变量 {varname} 不存在，跳过")
        continue

    var = ds1.variables[varname][:]
    var_selected = var[mask]

    # 再检查长度
    if len(var_selected) % 2 != 0:
        # 这里通常不会再发生，但万一出现，截断最后一个
        var_selected = var_selected[:-1]

    # 按2个半小时合并成1小时平均
    var_hourly = var_selected.reshape(-1, 2).mean(axis=1)

    NEONatmhourly_data[varname] = var_hourly
    print(f"✅ 处理完成: {varname}, 小时长度: {len(var_hourly)}")

# 小时时间戳
time_hourly = time_selected[::2]
print(f"小时时间点数: {len(time_hourly)}")
print(f"{varname} 原始形状: {var.shape}, 筛选后形状: {var_selected.shape}, 合并后小时数据形状: {var_hourly.shape}")

# 创建 DataFrame
df = pd.DataFrame({
    'time': time_hourly,
    'GPP': NEONevahourly_data.get('GPP'),
    'VPD': NEONevahourly_data.get('VPD'),
    'RH': NEONatmhourly_data.get('RH'),
    'TBOT': NEONatmhourly_data.get('TBOT'),
})

import matplotlib.pyplot as plt

plt.figure(figsize=(16, 10))

# 子图 1：GPP
plt.subplot(4, 1, 1)
plt.plot(df.index, df['GPP'], color='green')
plt.title('Hourly GPP')
plt.ylabel('GPP')
plt.grid(True)

# 子图 2：VPD
plt.subplot(4, 1, 2)
plt.plot(df.index, df['VPD'], color='orange')
plt.title('Hourly VPD')
plt.ylabel('VPD (kPa)')
plt.grid(True)

# 子图 3：RH
plt.subplot(4, 1, 3)
plt.plot(df.index, df['RH'], color='blue')
plt.title('Hourly Relative Humidity')
plt.ylabel('RH (%)')
plt.grid(True)

# 子图 4：TBOT
plt.subplot(4, 1, 4)
plt.plot(df.index, df['TBOT'], color='red')
plt.title('Hourly Air Temperature')
plt.ylabel('Temperature (K)')
plt.xlabel('Time')
plt.grid(True)

plt.tight_layout()
plt.show()


# 可选：将时间列设置为索引
df.set_index('time', inplace=True)

# 打印前几行检查
print(df.head())


#Ameriflux NEON SWC
import pandas as pd

# === Step 1: 读取 CSV 文件 ===
file_path = "/Users/chenyan/Desktop/CESM/AMF_US-xAB_BASE-BADM_10-5/AMF_US-xAB_BASE_HH_10-5.csv"

# 使用 -9999 表示缺失值
dfSWA = pd.read_csv(file_path, skiprows=2, na_values=-9999)

# === Step 2: 转换时间列为 datetime 类型 ===
dfSWA['TIMESTAMP_START'] = pd.to_datetime(dfSWA['TIMESTAMP_START'], format='%Y%m%d%H%M')

# 设置时间为索引
dfSWA.set_index('TIMESTAMP_START', inplace=True)

# === Step 3: 选择土壤水分列 ===
swc_cols = [
    'SWC_1_1_1', 'SWC_1_2_1', 'SWC_1_3_1', 'SWC_1_4_1',
    'SWC_1_5_1', 'SWC_1_6_1', 'SWC_1_7_1', 'SWC_1_8_1'
]
df_swc = dfSWA[swc_cols]

# === Step 4: 按小时重采样并求平均 ===
df_hourly = df_swc.resample('H').mean()

# === Step 5: 筛选 2018–2023 年的 6、7、8 月 ===
df_filtered = df_hourly[
    (df_hourly.index.year >= 2018) & (df_hourly.index.year <= 2023) &
    (df_hourly.index.month.isin([6, 7, 8]))
]

# === Step 6: 计算基于深度的加权平均土壤水分 ===
depths = [-0.06, -0.16, -0.26, -0.36, -0.56, -0.86, -1.16, -1.96]
weights = pd.Series([abs(d) for d in depths], index=swc_cols)

df_filtered['SWC_weighted_avg'] = df_filtered[swc_cols].apply(
    lambda row: row.multiply(weights).sum(skipna=True) / weights[row.notna()].sum(),
    axis=1
)

# === Step 6: 可选——保存为新文件 ===
output_path = "SWC_hourly_summer_2018_2023.csv"
df_filtered.to_csv(output_path)

print("✅ 处理完成，输出保存为：", output_path)


# heatmap
import matplotlib.ticker as mticker

class OOMFormatter(mticker.ScalarFormatter):
    def __init__(self, order=0, fmt="%1.1f", offset=True, mathText=True):
        self.oom = order
        self.fmt = fmt
        mticker.ScalarFormatter.__init__(self, useOffset=offset, useMathText=mathText)

    def _set_order_of_magnitude(self):
        self.orderOfMagnitude = self.oom

    def _set_format(self):
        self.format = self.fmt
        if self._useMathText:
            self.format = r'$\mathdefault{%s}$' % self.format

# Calculate the count and mean value of GPP/PAR within each interval
df_merged = df_merged["VPD_obs"] / 10
df_merged = df_merged["GPP_precipt2019"]
CTSM_gpp_all = gpp_all_unique_sorted
CTSM_tbot_all = tbot_all_unique_sorted - 273.15
CTSM_h2osoi_avg12_all = h2osoi_avg12

CTSM_tbot_all = np.squeeze(CTSM_tbot_all)
CTSM_gpp_all = np.squeeze(CTSM_gpp_all)
CTSM_h2osoi_avg12_all = np.squeeze(CTSM_h2osoi_avg12_all)
NEON_gpp = np.squeeze(NEON_gpp) * 12.01e-6
import pandas as pd

# 确保所有数组长度一致，假设都是 (N,)
print(len(NEON_gpp),len(NEON_VPD_all), len(NEON_gpp), len(CTSM_gpp_all), len(CTSM_tbot_all), len(CTSM_h2osoi_avg12_all))

# 假设你有对应的时间数组 time_all，长度也应该是 N
# 如果没有，替换成对应的时间变量名

df1 = pd.DataFrame({
    'time': time_all_unique_sorted,               # datetime64[ns] 类型
    'NEON_VPD_kPa': NEON_VPD_all,  # 已除以10的VPD，单位 kPa
    'NEON_GPP': NEON_gpp,          # 观测GPP
    'CTSM_GPP': CTSM_gpp_all,      # 模型GPP
    'CTSM_Tbot_C': CTSM_tbot_all,  # 地表温度摄氏度
    'CTSM_H2OSOI_avg12': CTSM_h2osoi_avg12_all  # 土壤水分加权平均
})

df1 = df1.dropna(subset=['CTSM_GPP', 'NEON_GPP'])  # 去除NaN
df1 = df1[(df1['CTSM_GPP'] != 0) & (df1['NEON_GPP'] != 0)]  # 去除为0的

df1 = df1.dropna(subset=['CTSM_GPP', 'NEON_GPP'])[(df1['CTSM_GPP'] != 0) & (df1['NEON_GPP'] != 0)]
df1 = df1[df1['NEON_GPP'] >= 0]

#NEON SWC 2m Corrected
import pandas as pd
import numpy as np

# === 第一步：读取 smois 数据 ===
smois = pd.read_csv("/Users/chenyan/Desktop/CESM/misc_inputs/ABBY_smois.csv")

# 假设时间列名为 'time'，转换为 datetime（如果尚未）
smois['time'] = pd.to_datetime(smois['startDateTime'])  # 替换成你的时间列名

# 设置时间为 index
smois = smois.set_index('time')

# 8 层土壤水分变量
cols = [
    'correctedVSWCMean_501',
    'correctedVSWCMean_502',
    'correctedVSWCMean_503',
    'correctedVSWCMean_504',
    'correctedVSWCMean_505',
    'correctedVSWCMean_506',
    'correctedVSWCMean_507',
    'correctedVSWCMean_508'
]

# 层厚度 (单位：米)，按层中心深度估算
weights = np.array([0.10, 0.10, 0.10, 0.20, 0.30, 0.30, 0.80, 1.00])

# === 第二步：计算加权平均土壤水分 ===
vswc = smois[cols].values  # shape: (time, 8)
weighted = np.average(vswc, axis=1, weights=weights)

# 添加为新列
smois['weighted_soil_moisture'] = weighted

# === 第三步：重采样为 hourly 平均 ===
smois_hourly = smois['weighted_soil_moisture'].resample('H').mean()

# === 第四步：根据 df1['time'] 对齐 ===
# 假设 df1['time'] 是 datetime64 类型
df1['NEON_SWC'] = smois_hourly.reindex(df1['time'].values, method='nearest').values



print(df.head())
print("GPP min:", float(CTSM_gpp_all.min()))
print("GPP max:", float(CTSM_gpp_all.max()))

print("h2osoi min:", float(CTSM_h2osoi_avg12_all.min()))
print("h2osoi max:", float(CTSM_h2osoi_avg12_all.max()))

print("tbot min:", float(CTSM_tbot_all.min()))
print("tbot max:", float(CTSM_tbot_all.max()))

print("VPD min:", float(NEON_VPD_all.min()))
print("VPD max:", float(NEON_VPD_all.max()))

df_mergedYELL["GPP_obs"] = df_mergedYELL["GPP_obs"] * 12e-6
df_mergedYELL = df_mergedYELL[df_mergedYELL['FSDS_obs'] >= 50].copy()
df_mergedYELL['LUE_default1023'] = df_mergedYELL['GPP_default1023'] / (df_mergedYELL['FSDS_obs'] * 0.48)
df_mergedYELL['LUE_obs'] = df_mergedYELL['GPP_obs'] / (df_mergedYELL['FSDS_obs'] * 0.48)
df_mergedYELL['LUE_prect00005'] = df_mergedYELL['GPP_prect00005'] / (df_mergedYELL['FSDS_obs'] * 0.48)
# df_merged["VEGWP_obs_MPa"] = df_merged["VEGWP_obs"] * 9.81e-6
df_mergedYELL["VEGWP_prect00005_MPa"] = df_mergedYELL["VEGWP_prect00005"] * 9.81e-6
df_mergedYELL["VEGWP_default1023_MPa"] = df_mergedYELL["VEGWP_default1023"] * 9.81e-6
df_mergedYELL['TBOT_obs'] = df_mergedYELL['TBOT_obs'] - 273.15
df_mergedYELL['VPD_obs'] = df_mergedYELL['VPD_obs'] / 10

mask = (df_mergedYELL.index >= '2021-06-01') & (df_mergedYELL.index <= '2021-08-31 23:59:59')
df_mergedYELLselect = df_mergedYELL.loc[mask].copy()
df_mergedYELLselect = df_mergedYELL[df_mergedYELL['FSDS_obs'] > 50]
# df_filteredsummer = df_filtered.loc[mask].copy()
df_merged["VEGWP_MPa"] = df_filteredsummer["VEGWP_default"] * 9.81e-6

CTSM_tbot_all = np.squeeze(CTSM_tbot_all)
CTSM_gpp_all = np.squeeze(CTSM_gpp_all)
CTSM_h2osoi_avg12_all = np.squeeze(CTSM_h2osoi_avg12_all)
NEON_VPD_all = np.squeeze(NEON_VPD_all)
x_tick_intervals = [0.1556,  0.1558, 0.156, 0.1562, 0.1564, 0.1566, 0.1568,0.157 ]
x_tick_intervals = [0.150, 0.155, 0.160, 0.165, 0.170, 0.175]
x_tick_intervals = [0.08, 0.085, 0.090, 0.095]
y_tick_intervals = [0,0.2,0.4,0.6,0.8,1.0,1.2,1.4,1.6,1.8,2.0,2.2,2.4,2.6,2.8,3.0,3.2,3.4,3.6]
x_tick_intervals = [0.18,  0.20, 0.22, 0.24, 0.26 ]
x_tick_intervals = [ -7,-6, -5,-4, -3,-2,-1,0]
y_tick_intervals = [0,0.5,1,1.5,2,2.5,3]
y_tick_intervals = [0,4,8,12,16,20,24,28,32]
y_tick_intervals = [0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5]
y_tick_intervals = [0.32,0.34,0.36,0.38,0.4,0.42,0.44]
y_tick_intervals = [0.39,0.41,0.43,0.45,0.47]
y_tick_intervals = np.arange(0.39, 0.46 + 0.001, 0.01).tolist()
print("NEON_VPD_all shape:", NEON_VPD_all.shape)
print("CTSM_tbot_all shape:", CTSM_tbot_all.shape)
print("CTSM_gpp_all shape:", CTSM_gpp_all.shape)
df_merged["GPP_obs"]= df_merged["GPP_obs"] * 12e-6

import seaborn as sns
import matplotlib.pyplot as plt
count_values = []
mean_values = []

for x_start, x_end in zip(x_tick_intervals[:-1], x_tick_intervals[1:]):
    for i, (y_start, y_end) in enumerate(zip(y_tick_intervals[:-1], y_tick_intervals[1:])):
        if i == len(y_tick_intervals) - 2:  # Last interval includes upper bound
            mask = (df_mergedYELLselect['H2OSOI_prect00005'] >= x_start) & (df_mergedYELLselect['H2OSOI_prect00005'] < x_end) & (df_mergedYELLselect['VPD_obs']>= y_start) & (df_mergedYELLselect['VPD_obs']<= y_end)
        else:
            mask = (df_mergedYELLselect['H2OSOI_prect00005'] >= x_start) & (df_mergedYELLselect['H2OSOI_prect00005'] < x_end) & (df_mergedYELLselect['VPD_obs']>= y_start) & (df_mergedYELLselect['VPD_obs']< y_end)
        
        gpp = df_mergedYELLselect["LUE_prect00005"][mask.ravel()]
        count_gpp = len(gpp)
        mean_gpp = gpp.mean() if count_gpp > 0 else np.nan
        count_values.append(count_gpp)
        mean_values.append(mean_gpp)

# for x_start, x_end in zip(x_tick_intervals[:-1], x_tick_intervals[1:]):
#     for y_start, y_end in zip(y_tick_intervals[:-1], y_tick_intervals[1:]):
#         mask = (data1['Tmax'] >= x_start) & (data1['Tmax'] < x_end) & (data1['vpd'] >= y_start) & (data1['vpd'] < y_end)
#         # mask = (data1['vpd'] >= x_start) & (data1['vpd'] < x_end) & (data1['SWA'] >= y_start) & (data1['SWA'] < y_end)
#         gpp_par_values = data1.loc[mask, 'LUE']
#         count_gpp_par = len(gpp_par_values)
#         mean_gpp_par = gpp_par_values.mean() if count_gpp_par > 0 else np.nan
#         count_values.append(count_gpp_par)
#         mean_values.append(mean_gpp_par)

# Reshape count and mean values into matrices for the heatmap
count_matrix = np.array(count_values).reshape(len(x_tick_intervals) - 1, len(y_tick_intervals) - 1)
mean_matrix = np.array(mean_values).reshape(len(x_tick_intervals) - 1, len(y_tick_intervals) - 1)


count_matrix = np.array(count_values, dtype=float).reshape(len(x_tick_intervals) - 1, len(y_tick_intervals) - 1)
mean_matrix = np.array(mean_values).reshape(len(x_tick_intervals) - 1, len(y_tick_intervals) - 1)


mask = count_matrix < 5

count_matrix[mask] = np.nan
mean_matrix[mask] = np.nan

# Create a custom color palette based on the mean GPP/PAR values
cmap = sns.color_palette("coolwarm", as_cmap=True)
annot_kws = {
    'fontsize': 12,  # Set the font size for the annotation values
    'fontweight': 'bold',  # Set font weight (optional)
}

# Create the heatmap with custom colors and set extent
plt.figure(figsize=(12, 10))
# heatmap = sns.heatmap(mean_matrix, cmap=cmap, annot=count_matrix, fmt='.0f', vmin=0, vmax=5.0e-06, cbar_kws={'label': 'Mean GPP/PAR g MJ-1'}, annot_kws=annot_kws)

# heatmap = sns.heatmap(mean_matrix, cmap=cmap, annot=count_matrix, fmt='.0f',
#                       vmin=5.0e-5, vmax=10.0e-5, cbar_kws={'label': 'Mean GPP/PAR g MJ-1'})
# #same timestep
heatmap = sns.heatmap(mean_matrix, cmap=cmap, annot=count_matrix, fmt='.0f',
                      vmin=0, vmax=0.0000015, cbar_kws={'label': 'Mean GPP/PAR g MJ-1'})

cbar = heatmap.collections[0].colorbar

# 自定义刻度位置，比如分成5档
# ticks = [6.8e-5, 7.4e-5, 8.0e-5, 8.6e-5, 9.2e-5, 9.8e-5, 1.0e-4]
ticks = np.linspace(0, 0.0000015, num=6).tolist()
cbar.set_ticks(ticks)
print("mean_matrix min:", np.nanmin(mean_matrix))
print("mean_matrix max:", np.nanmax(mean_matrix))
# 用科学计数法显示刻度标签
cbar = heatmap.collections[0].colorbar
cbar.set_ticks(ticks)
cbar.ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1e}'))
cbar.ax.tick_params(labelsize=14)

# Set the x and y-axis tick positions and labels with specific font size
plt.yticks(np.arange(len(x_tick_intervals) - 1) + 0.5, [f'{x:.3f}-{x_next:.2f}' for x, x_next in zip(x_tick_intervals[:-1], x_tick_intervals[1:])], fontsize=20,rotation='horizontal')
plt.xticks(np.arange(len(y_tick_intervals) - 1) + 0.5, [f'{y:.1f}-{y_next:.1f}' for y, y_next in zip(y_tick_intervals[:-1], y_tick_intervals[1:])], fontsize=20,rotation='vertical')

heatmap.invert_yaxis()

# Set the x and y-axis labels
# plt.xlabel('VPD (kPa)', fontsize=40)
# plt.xlabel('Temperature', fontsize=40)
# plt.ylabel('Leaf Water Potential', fontsize=40)
plt.ylabel('Soil Moisture', fontsize=40)

plt.xlabel('VPD (kPa)', fontsize=40)

# # Change the font size of colorbar tick labels
# cbar = heatmap.collections[0].colorbar  # Get the colorbar
# # cbar.formatter = OOMFormatter(order=-10, fmt="%1.1f", mathText=False)
# cbar.update_ticks()
# cbar.ax.tick_params(labelsize=30)
# cbar.set_label('LUE', fontsize=30)
# # formatter = ScalarFormatter()
# # formatter.set_powerlimits((-9, -9))  # Set limits for scientific notation
# # formatter.set_scientific(True)  # Enable scientific notation
# # cbar.formatter = formatter
# cbar.update_ticks()
# cbar.ax.tick_params(labelsize=30)

# cbar.ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))
# cbar.ax.tick_params(labelsize=40)
cbar.set_label('LUE', fontsize=40,labelpad=30)

plt.tight_layout()
plt.show()



df_SERCDaily = df_SERC.resample("D").mean()

df_TALLDaily = df_TALL.resample("D").mean()
df_NEONTALLDaily = df_NEONTALL.resample("D").mean()

print(df_SERCDaily.index.min(), df_SERCDaily.index.max())

print(df_SERCDaily.index.tz)
df_TALLDaily.index = df_TALLDaily.index.tz_convert("America/Chicago").tz_localize(None)
fig, ax1 = plt.subplots(figsize=(14, 5))

ax1.plot(df_TALLDaily.index, df_TALLDaily["GPP"], color="orange")
# ax1.plot(df_SERCDaily.index, df_SERCDaily["GPP"], color="orange")

# ax1.set_ylim(-10,0)
# ax1.set_ylabel("Temperature (℃)", color="black", fontsize=15)
# ax1.set_ylabel("SM", color="black", fontsize=15)
# ax1.set_ylabel("Leaf Water Potential", color="black", fontsize=15)
ax1.set_ylabel("GPP", color="black", fontsize=15)
# ax1.tick_params(axis="y", labelcolor="orange")
# ax1.legend(loc="upper left", fontsize=15)
# ax1.tick_params(axis="both", labelsize=15)
ax2 = ax1.twinx()
# ax2.plot(df_SERCDaily.index, df_SERCDaily["FCEV"]+df_SERCDaily["FCTR"]+df_SERCDaily["FGEV"], color="green")
ax2.plot(df_NEONTALLDaily.index, df_NEONTALLDaily["GPP"], color="gray", label = "SH")
# ax2.plot(df_SERCDaily.index, df_SERCDaily["Qh"], color="purple", label = "SH")
# ax2.legend(loc="upper right")
# ax2.set_ylabel("Soil Moisture mm3/mm3", color="Black")
ax2.set_ylabel("SM", color="Black",fontsize=15)
# ax2.tick_params(axis="y", labelcolor="Gray")
# plt.ylim(0,0.0002)
# 标题
# plt.title("GPP_obs vs VPD_obs")
fig.tight_layout()
plt.show()
