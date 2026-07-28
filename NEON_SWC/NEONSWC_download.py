import os
import requests
from datetime import datetime

PRODUCT = "DP1.00094.001"
SITE = "RMNP"
START = "2020-01"
END   = "2020-01"
OUTDIR = "/glade/derecho/scratch/yanc/NEON_SWC/RMNP202001"

os.makedirs(OUTDIR, exist_ok=True)

def month_range(start, end):
    start_dt = datetime.strptime(start, "%Y-%m")
    end_dt   = datetime.strptime(end, "%Y-%m")
    months = []
    cur = start_dt
    while cur <= end_dt:
        months.append(cur.strftime("%Y-%m"))
        if cur.month == 12:
            cur = cur.replace(year=cur.year + 1, month=1)
        else:
            cur = cur.replace(month=cur.month + 1)
    return months

months = month_range(START, END)

for ym in months:
    print(f"\nQuerying {ym}")
    url = f"https://data.neonscience.org/api/v0/data/{PRODUCT}/{SITE}/{ym}"

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("  Request failed → skip")
        continue

    files = data.get("data", {}).get("files", [])

    if len(files) == 0:
        print("  No data → skip")
        continue

    print(f"  Found {len(files)} files")

    for f in files:
        fname = f.get("name", "")
        furl  = f.get("url", "")

        if fname == "" or furl == "":
            continue

        outpath = os.path.join(OUTDIR, fname)

        if os.path.exists(outpath):
            print(f"  Exists → skip {fname}")
            continue

        print(f"  Downloading {fname}")
        try:
            with requests.get(furl, stream=True, timeout=120) as rr:
                rr.raise_for_status()
                with open(outpath, "wb") as fp:
                    for chunk in rr.iter_content(chunk_size=8192):
                        if chunk:
                            fp.write(chunk)
        except Exception as e:
            print(f"  Failed {fname}")

