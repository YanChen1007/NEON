#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 10:45:32 2026

@author: chenyan
"""

import pandas as pd
import matplotlib.pyplot as plt

# 文件
file = "/Users/chenyan/Desktop/Project/NEON_Tem/HARV/HARV_T_vertical_profile.csv"

df = pd.read_csv(file)

# 时间
df["startDateTime"] = pd.to_datetime(df["startDateTime"])

# 提取年月
df["year"] = df["startDateTime"].dt.year
df["month"] = df["startDateTime"].dt.month

# 只保留6-8月
jja = df[df["month"].isin([6,7,8])]


# 高度信息 (m)
heights = {
    "Tair_L1": 0.19,
    "Tair_L2": 5.29,
    "Tair_L3": 16.26,
    "Tair_L4": 25.45,
    "Tair_L5": 29.60
}


# 每年JJA平均
annual = (
    jja
    .groupby("year")[list(heights.keys())]
    .mean()
)


# 画图
plt.figure(figsize=(6,8))

for year, row in annual.iterrows():
    plt.plot(
        row.values,
        list(heights.values()),
        marker="o",
        label=str(year)
    )

plt.xlabel("Air temperature (°C)")
plt.ylabel("Height (m)")
plt.title("HARV JJA mean air temperature profile")

plt.legend(
    bbox_to_anchor=(1.05,1),
    loc="upper left",
    fontsize=8
)

plt.grid(True)
plt.tight_layout()

plt.savefig(
    "/glade/work/yanc/Downloads/NEON_Tem/HARV_JJA_temperature_profile.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()







#each
import pandas as pd
import matplotlib.pyplot as plt
import os

file = "/Users/chenyan/Desktop/Project/NEON_Tem/HARV/HARV_T_vertical_profile.csv"

df = pd.read_csv(file)

df["startDateTime"] = pd.to_datetime(df["startDateTime"])

df["year"] = df["startDateTime"].dt.year
df["month"] = df["startDateTime"].dt.month


heights = {
    "Tair_L1": 0.19,
    "Tair_L2": 5.29,
    "Tair_L3": 16.26,
    "Tair_L4": 25.45,
    "Tair_L5": 29.60
}


outdir = "/Users/chenyan/Desktop/Project/NEON_Tem"
os.makedirs(outdir, exist_ok=True)


# 每一年画一张图
for year in sorted(df["year"].unique()):

    yearly = df[df["year"] == year]

    plt.figure(figsize=(5,7))
    colors = {

    6: "blue",

    7: "orange",

    8: "red"

    }

    # 每个月一条线
    for month in [6, 7, 8]:

        monthly = yearly[yearly["month"] == month]

        if len(monthly) == 0:
            continue

        # 月平均
        mean_temp = monthly[list(heights.keys())].mean()

        plt.plot(
            mean_temp.values,
            list(heights.values()),
            marker="o",
            color=colors[month],
            label=f"{month}"
        )

    plt.xlabel("Air temperature (°C)")
    plt.ylabel("Height (m)")
    plt.title(f"HARV monthly temperature profile {year}")

    plt.legend(title="Month")
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        f"{outdir}/HARV_monthly_temperature_profile_{year}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("Saved", year)
    
    
    
    
    
    
    
    
    
    
    
# model and obs comparison
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


# ==========================
# Read observation (NEON)
# ==========================

obs_file = "/Users/chenyan/Desktop/Project/NEON_Tem/SERC/SERC_T_vertical_profile.csv"

obs = pd.read_csv(obs_file)

obs["startDateTime"] = pd.to_datetime(obs["startDateTime"])
obs["month"] = obs["startDateTime"].dt.month
obs["year"] = obs["startDateTime"].dt.year

# only 2021 summer

obs = obs[

    (obs["year"] == 2023) &

    (obs["month"].isin([6,7,8]))

]



obs_heights = {
    "Tair_L1": 0.19,
    "Tair_L2": 5.29,
    "Tair_L3": 16.26,
    "Tair_L4": 25.45,
    "Tair_L5": 29.60
}


# ==========================
# Read model
# ==========================

folder = "/Users/chenyan/Desktop/Project/SERC/output"

files = [
    os.path.join(folder, "SERC66_2023-06_profile.out"),
    os.path.join(folder, "SERC66_2023-07_profile.out"),
    os.path.join(folder, "SERC66_2023-08_profile.out")
]

profiles = []

for f in files:

    month = int(f.split("-")[-1].split("_")[0])

    df = pd.read_csv(
        f,
        delim_whitespace=True,
        comment="#",
        header=None
    )

    df.columns = [
        "curr_calday",
        "zs_profile",
        "zero_1",
        "zero_2",
        "zero_3",
        "zero_4",
        "missing_1",
        "missing_2",
        "missing_3",
        "missing_4",
        "missing_5",
        "missing_6",
        "missing_7",
        "missing_8",
        "missing_9",
        "missing_10",
        "missing_11",
        "missing_12",
        "missing_13",
        "missing_14",
        "missing_15",
        "missing_16",
        "missing_17",
        "missing_18",
        "wind_profile",
        "tair",
        "qair"
    ]

    df["month"] = month

    profiles.append(df)


model = pd.concat(profiles, ignore_index=True)

model = model.replace(-999, np.nan)

model["tair"] = model["tair"] - 273.15



# ==========================
# Plot comparison
# ==========================

colors = {
    6:"tab:blue",
    7:"tab:orange",
    8:"tab:red"
}

labels = {
    6:"June",
    7:"July",
    8:"August"
}


fig, ax = plt.subplots(figsize=(5,7))


for m in [6,7,8]:

    # ---- Model ----
    model_mean = (
        model[model["month"]==m]
        .groupby("zs_profile")["tair"]
        .mean()
        .reset_index()
    )

    ax.plot(
        model_mean["tair"],
        model_mean["zs_profile"],
        color=colors[m],
        linewidth=2,
        label=f"{labels[m]} model"
    )


    # ---- Observation ----
    obs_mean = (
        obs[obs["month"]==m]
        [list(obs_heights.keys())]
        .mean()
    )

    ax.plot(
        obs_mean.values,
        list(obs_heights.values()),
        color=colors[m],
        linestyle="--",
        marker="o",
        linewidth=2,
        label=f"{labels[m]} observation"
    )


ax.set_xlabel("Air temperature (°C)")
ax.set_ylabel("Height (m)")

ax.set_xlim(10,25)

ax.grid(True)

ax.legend(fontsize=8)

plt.title(
    "HARV 2021 summer canopy temperature profile\nModel vs NEON observation"
)

plt.tight_layout()

plt.show()


#model up tp 40m
from matplotlib.lines import Line2D

# ==========================
# Plot comparison
# ==========================

fig, ax = plt.subplots(figsize=(5,7))

for m in [6,7,8]:

    # ---- Model ----
    model_mean = (
        model[model["month"]==m]
        .groupby("zs_profile")["tair"]
        .mean()
        .reset_index()
    )

    # model height <=40 m
    model_mean = model_mean[model_mean["zs_profile"] <= 40]

    ax.plot(
        model_mean["tair"],
        model_mean["zs_profile"],
        color=colors[m],
        linewidth=2,
        linestyle="-"
    )


    # ---- Observation ----
    obs_mean = (
        obs[obs["month"]==m]
        [list(obs_heights.keys())]
        .mean()
    )

    ax.plot(
        obs_mean.values,
        list(obs_heights.values()),
        color=colors[m],
        linestyle="--",
        marker="o",
        linewidth=2
    )


# ==========================
# Axis
# ==========================

ax.set_xlabel("Air temperature (°C)")
ax.set_ylabel("Height (m)")

ax.set_ylim(0,40)
ax.set_xlim(10,25)

ax.grid(True)


# ==========================
# Legends
# ==========================

# color legend (months)
month_legend = [
    Line2D([0],[0], color=colors[6], lw=3, label="June"),
    Line2D([0],[0], color=colors[7], lw=3, label="July"),
    Line2D([0],[0], color=colors[8], lw=3, label="August")
]


# line style legend
type_legend = [
    Line2D([0],[0], color="black", lw=2, linestyle="-", label="Model"),
    Line2D([0],[0], color="black", lw=2, linestyle="--",
           marker="o", label="Observation")
]


legend1 = ax.legend(
    handles=month_legend,
    title="Month",
    loc="upper right"
)

ax.add_artist(legend1)

ax.legend(
    handles=type_legend,
    title="Data",
    loc="upper left"
)

ax.set_xlim(18,30)

plt.title(
    "SERC 2023 summer canopy temperature profile\nModel vs NEON observation"
)

plt.tight_layout()
plt.show()