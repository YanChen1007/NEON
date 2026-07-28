#!/usr/bin/env python3
"""Plot monthly mean air-temperature vertical profiles from NEON hourly CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


SITES = ("HARV", "MLBS", "ORNL", "SERC", "TALL")
YEARS = range(2018, 2024)
MONTH_NAMES = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)
PLOT_MONTHS = (6, 7, 8)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate one monthly-mean temperature vertical-profile PNG "
            "per site and year."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("."),
        help="Directory containing SITE_air_temperature_hourly_all_levels.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("neon_vertical_profiles"),
        help="Directory in which PNG files will be saved",
    )
    parser.add_argument(
        "--input-suffix",
        default="_NQF",
        help=(
            "Text appended after 'all_levels' in each input filename "
            "(default: _NQF; use an empty string for the original files)"
        ),
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="PNG resolution (default: 200)",
    )
    return parser.parse_args()


def read_site_csv(csv_path: Path) -> pd.DataFrame:
    required = {"startDateTime", "height", "temperature"}
    df = pd.read_csv(
        csv_path,
        usecols=lambda column: column in required,
        parse_dates=["startDateTime"],
    )
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{csv_path.name} is missing columns: {sorted(missing)}")

    df["height"] = pd.to_numeric(df["height"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df = df.dropna(subset=["startDateTime", "height", "temperature"]).copy()
    df["year"] = df["startDateTime"].dt.year
    df["month"] = df["startDateTime"].dt.month
    return df


def plot_site_year(
    monthly: pd.DataFrame,
    site: str,
    year: int,
    output_path: Path,
    dpi: int,
) -> None:
    year_data = monthly[
        (monthly["year"] == year) & monthly["month"].isin(PLOT_MONTHS)
    ]
    width, height_px = 1440, 1320
    left, right, top, bottom = 165, 90, 105, 150
    plot_w = width - left - right
    plot_h = height_px - top - bottom
    image = Image.new("RGB", (width, height_px), "white")
    draw = ImageDraw.Draw(image)

    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font_path = next((p for p in font_paths if Path(p).exists()), None)
    title_font = ImageFont.truetype(font_path, 34) if font_path else ImageFont.load_default()
    label_font = ImageFont.truetype(font_path, 27) if font_path else ImageFont.load_default()
    tick_font = ImageFont.truetype(font_path, 22) if font_path else ImageFont.load_default()
    legend_font = ImageFont.truetype(font_path, 20) if font_path else ImageFont.load_default()

    colors = {6: "#2e86de", 7: "#28a745", 8: "#f39c12"}
    all_x = year_data["temperature"].dropna()
    all_y = year_data["height"].dropna()
    if all_x.empty or all_y.empty:
        xmin, xmax, ymin, ymax = 0.0, 1.0, 0.0, 1.0
    else:
        xmin, xmax = float(all_x.min()), float(all_x.max())
        ymin, ymax = 0.0, float(all_y.max())
        xpad = max((xmax - xmin) * 0.08, 0.5)
        ypad = max(ymax * 0.05, 0.5)
        xmin, xmax = xmin - xpad, xmax + xpad
        ymax += ypad

    def px_x(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * plot_w

    def px_y(value: float) -> float:
        return top + plot_h - (value - ymin) / (ymax - ymin) * plot_h

    # Grid, tick labels, and axes.
    for i in range(6):
        value = xmin + i * (xmax - xmin) / 5
        x = px_x(value)
        draw.line((x, top, x, top + plot_h), fill="#dddddd", width=2)
        text = f"{value:.1f}"
        box = draw.textbbox((0, 0), text, font=tick_font)
        draw.text((x - (box[2] - box[0]) / 2, top + plot_h + 18), text, fill="black", font=tick_font)
    for i in range(6):
        value = ymin + i * (ymax - ymin) / 5
        y = px_y(value)
        draw.line((left, y, left + plot_w, y), fill="#dddddd", width=2)
        text = f"{value:.1f}"
        box = draw.textbbox((0, 0), text, font=tick_font)
        draw.text((left - 20 - (box[2] - box[0]), y - (box[3] - box[1]) / 2), text, fill="black", font=tick_font)
    draw.rectangle((left, top, left + plot_w, top + plot_h), outline="black", width=3)

    plotted_months = []
    for month in PLOT_MONTHS:
        profile = (
            year_data[year_data["month"] == month]
            .sort_values("height")
        )
        if profile.empty:
            continue
        points = [
            (px_x(float(row.temperature)), px_y(float(row.height)))
            for row in profile.itertuples()
        ]
        color = colors[month]
        if len(points) > 1:
            draw.line(points, fill=color, width=5, joint="curve")
        for x, y in points:
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=color, outline="white", width=2)
        plotted_months.append(month)

    title = f"{site} Monthly Mean Air-Temperature Profiles — {year}"
    title_box = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((width - (title_box[2] - title_box[0])) / 2, 35), title, fill="black", font=title_font)
    xlabel = "Monthly mean air temperature (°C)"
    xlabel_box = draw.textbbox((0, 0), xlabel, font=label_font)
    draw.text(((width - (xlabel_box[2] - xlabel_box[0])) / 2, height_px - 60), xlabel, fill="black", font=label_font)

    ylabel = "Sensor height (m)"
    label_img = Image.new("RGBA", (320, 60), (255, 255, 255, 0))
    label_draw = ImageDraw.Draw(label_img)
    label_draw.text((0, 5), ylabel, fill="black", font=label_font)
    label_img = label_img.rotate(90, expand=True)
    image.paste(label_img, (28, (height_px - label_img.height) // 2), label_img)

    # Compact two-column legend inside the plot.
    legend_x = left + 25
    legend_y = top + 22
    for index, month in enumerate(plotted_months):
        col = index // 6
        row = index % 6
        x = legend_x + col * 120
        y = legend_y + row * 32
        draw.line((x, y + 10, x + 32, y + 10), fill=colors[month], width=5)
        draw.text((x + 42, y), MONTH_NAMES[month - 1], fill="black", font=legend_font)

    image.save(output_path, format="PNG", dpi=(dpi, dpi))


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    for site in SITES:
        csv_path = (
            args.input_dir
            / (
                f"{site}_air_temperature_hourly_all_levels"
                f"{args.input_suffix}.csv"
            )
        )
        if not csv_path.exists():
            raise FileNotFoundError(f"Input file not found: {csv_path}")

        print(f"Reading {csv_path}")
        df = read_site_csv(csv_path)
        monthly = (
            df[df["year"].isin(YEARS) & df["month"].isin(PLOT_MONTHS)]
            .groupby(["year", "month", "height"], as_index=False)
            .agg(
                temperature=("temperature", "mean"),
                hourly_count=("temperature", "count"),
            )
        )

        for year in YEARS:
            output_path = args.output_dir / f"{site}_{year}_monthly_profiles.png"
            plot_site_year(monthly, site, year, output_path, args.dpi)
            generated.append(output_path)
            print(f"Saved {output_path}")

    print(f"Generated {len(generated)} PNG files in {args.output_dir}")


if __name__ == "__main__":
    main()
