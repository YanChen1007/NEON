#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 10:02:40 2026

@author: chenyan
"""

import pandas as pd
files = [
    "/Users/chenyan/Desktop/Project/SERC/output/SERC66_2018-08_aux.out",
    "/Users/chenyan/Desktop/Project/SERC/output/SERC66_2018-08_flux.out",
    "/Users/chenyan/Desktop/Project/SERC/output/SERC66_2018-08_fsun.out",
    "/Users/chenyan/Desktop/Project/SERC/output/SERC66_2018-08_profile.out"
]

with open("/Users/chenyan/Desktop/Project/SERC/output/SERC66_2018-08_flux.out", "r") as f:
    for i in range(5):
        print(f.readline())
        
data = {}
for f in files:
    name = f.split("/")[-1].replace(".out", "")    
    df = pd.read_csv(
        f,
        delim_whitespace=True,
        comment="#",
        header=None,

    skipinitialspace=True
    )
    data[name] = df
    print(name)
    print(df.shape)
    print(df.head())
    print("----------------")

aux = data["SERC66_2018-08_aux"]
aux.columns = [
    "btran_soil",       # soil water stress factor
    "lsc_profile",      # leaf specific conductance
    "psis_soil",        # soil water potential
    "lwp_top",          # top canopy leaf water potential
    "lwp_mid",          # mid canopy leaf water potential
    "fraction_min_LWP"  # fraction minimum LWP
]
flux = data["SERC66_2018-08_flux"]
flux.columns = [
    "canopy_net_radiation",       # 1 canopy net radiation
    "storage_flux",               # 2 storage flux
    "canopy_sensible_heat",       # 3 canopy sensible heat
    "canopy_latent_heat",         # 4 canopy latent heat
    "GPP",                        # 5 gross primary production
    "ustar",                      # 6 friction velocity
    "shortwave_up",               # 7 shortwave radiation upward
    "longwave_up",                # 8 longwave radiation upward
    "air_temperature_canopy",     # 9 air temperature above canopy
    "soil_conductance",           # 10 soil conductance
    "soil_net_radiation",         # 11 soil net radiation
    "soil_sensible_heat",         # 12 soil sensible heat
    "soil_latent_heat"            # 13 soil latent heat
]
fsun = data["SERC66_2018-08_fsun"]
fsun.columns = [
    "solar_zenith_angle",          # 1 solar zenith angle (degree)
    "swsky",                       # 2 incoming shortwave radiation (visible)
    "LAI_SAI",                     # 3 total leaf + stem area index
    "LAI_sun",                     # 4 sunlit leaf area index
    "LAI_sha",                     # 5 shaded leaf area index
    "SWveg",                       # 6 canopy absorbed/available shortwave
    "SWveg_sun",                   # 7 sunlit canopy shortwave
    "SWveg_sha",                   # 8 shaded canopy shortwave
    "GPP_veg",                     # 9 total canopy GPP
    "GPP_sun",                     # 10 sunlit canopy GPP
    "GPP_sha",                     # 11 shaded canopy GPP
    "LH_veg",                      # 12 total canopy latent heat
    "LH_sun",                      # 13 sunlit canopy latent heat
    "LH_sha",                      # 14 shaded canopy latent heat
    "SH_veg",                      # 15 total canopy sensible heat
    "SH_sun",                      # 16 sunlit canopy sensible heat
    "SH_sha",                      # 17 shaded canopy sensible heat
    "Vcmax25_veg",                 # 18 total canopy Vcmax25
    "Vcmax25_sun",                 # 19 sunlit Vcmax25
    "Vcmax25_sha",                 # 20 shaded Vcmax25
    "gs_veg",                      # 21 total canopy stomatal conductance
    "gs_sun",                      # 22 sunlit stomatal conductance
    "gs_sha",                      # 23 shaded stomatal conductance
    "wind_veg",                    # 24 canopy wind speed
    "wind_sun",                    # 25 sunlit wind speed
    "wind_sha",                    # 26 shaded wind speed
    "tl_veg",                      # 27 leaf temperature total canopy
    "tl_sun",                      # 28 sunlit leaf temperature
    "tl_sha",                      # 29 shaded leaf temperature
    "ta_veg",                      # 30 canopy air temperature
    "ta_sun",                      # 31 sunlit canopy air temperature
    "ta_sha"                       # 32 shaded canopy air temperature
]
fsun["solar_zenith_angle"].describe()

profile = data["SERC66_2018-08_profile"]
profile.columns = [
    "curr_calday",          # col 1
    "zs_profile",           # col 2
    "zero_1",               # col 3
    "zero_2",               # col 4
    "zero_3",               # col 5
    "zero_4",               # col 6
    "missing_1",            # col 7
    "missing_2",            # col 8
    "missing_3",            # col 9
    "missing_4",            # col 10
    "missing_5",            # col 11
    "missing_6",            # col 12
    "missing_7",            # col 13
    "missing_8",            # col 14
    "missing_9",            # col 15
    "missing_10",           # col 16
    "missing_11",           # col 17
    "missing_12",           # col 18
    "missing_13",           # col 19
    "missing_14",           # col 20
    "missing_15",           # col 21
    "missing_16",           # col 22
    "missing_17",           # col 23
    "missing_18",           # col 24
    "wind_profile",         # col 25
    "tair",                 # col 26
    "qair"                  # col 27
]
print(flux.columns)

import pandas as pd

import numpy as np

profile["datetime"] = (

    pd.Timestamp("2018-01-01") +

    pd.to_timedelta(profile["curr_calday"] - 1, unit="D")

)

print(profile[["curr_calday", "datetime"]].head())


import matplotlib.pyplot as plt
import numpy as np

# 去掉 missing
profile_clean = profile.replace(-999, np.nan)

profile_clean["tair"] = profile_clean["tair"]-273.15

# 7月平均 vertical profile
profile_mean = (
    profile_clean
    .groupby("zs_profile")[["tair", "qair"]]
    .mean()
    .reset_index()
)

fig, ax1 = plt.subplots(figsize=(5,6))
profile["qair"].describe()
# tair
ax1.plot(
    profile_mean["tair"],
    profile_mean["zs_profile"],
    marker="o",
    color="tab:red",
    label="Tair"
)
ax1.set_xlim(15, 25)
ax1.set_xlabel("Air temperature (C)",color ="tab:red" )
ax1.set_ylabel("Height (m)")

# qair 用第二个x轴
ax2 = ax1.twiny()

ax2.plot(
    profile_mean["qair"],
    profile_mean["zs_profile"],
    marker="s",
    color="tab:blue",
    label="Qair"
)
ax2.set_xlim(15, 25)
ax2.set_xlabel("Specific humidity (g kg$^{-1}$)",color ="tab:blue" )

plt.title("Mean August 2018 canopy profile at SERC")

plt.tight_layout()
plt.show()





import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os


folder = "/Users/chenyan/Desktop/Project/HARV/ML"

files = [
    os.path.join(folder, "HARV66_2021-06_profile.out"),
    os.path.join(folder, "HARV66_2021-07_profile.out"),
    os.path.join(folder, "HARV66_2021-08_profile.out")
]

profiles = []

for f in files:
    
    month = int(f.split("-")[-1].split("_")[0])
    
    df = pd.read_csv(
        f,
        delim_whitespace=True,
        comment="#",
        header=None,
        skipinitialspace=True
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


profile = pd.concat(profiles, ignore_index=True)


# remove missing
profile = profile.replace(-999, np.nan)

# K -> C
profile["tair"] = profile["tair"] - 273.15


colors = {
    6: "tab:blue",
    7: "tab:orange",
    8: "tab:red"
}

labels = {
    6: "June",
    7: "July",
    8: "August"
}


# ==========================
# Temperature
# ==========================

fig, ax = plt.subplots(figsize=(5,6))

for m in [6,7,8]:

    mean_profile = (
        profile[profile["month"] == m]
        .groupby("zs_profile")[["tair"]]
        .mean()
        .reset_index()
    )

    ax.plot(
        mean_profile["tair"],
        mean_profile["zs_profile"],
        marker="o",
        color=colors[m],
        label=labels[m]
    )


ax.set_xlim(10,25)
ax.set_xlabel("Air temperature (°C)")
ax.set_ylabel("Height (m)")
ax.legend()

plt.title("HARV 2021 summer canopy temperature profile")
plt.tight_layout()
plt.show()



# ==========================
# Specific humidity
# ==========================

fig, ax = plt.subplots(figsize=(5,6))

for m in [6,7,8]:

    mean_profile = (
        profile[profile["month"] == m]
        .groupby("zs_profile")[["qair"]]
        .mean()
        .reset_index()
    )

    ax.plot(
        mean_profile["qair"],
        mean_profile["zs_profile"],
        marker="o",
        color=colors[m],
        label=labels[m]
    )

ax.set_xlim(7,20)
ax.set_xlabel("Specific humidity")
ax.set_ylabel("Height (m)")
ax.legend()

plt.title("HARV 2021 summer canopy humidity profile")
plt.tight_layout()
plt.show()