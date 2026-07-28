#!/usr/bin/env python3
"""Compare NEON observations with multilayer-model monthly temperature profiles."""

from __future__ import annotations

import argparse
import calendar
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


SITES = ("HARV", "MLBS", "ORNL", "SERC", "TALL")
YEARS = range(2018, 2024)
MONTHS = (6, 7, 8)
MONTH_NAMES = {6: "Jun", 7: "Jul", 8: "Aug"}
COLORS = {6: "#2e86de", 7: "#28a745", 8: "#f39c12"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("."),
        help=(
            "Directory containing SITE_air_temperature_hourly_all_levels_NQF.csv "
            "and SITE/ml/"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("neon_observation_model_profiles"),
    )
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument(
        "--variable",
        choices=("temperature", "wind"),
        default="temperature",
        help="Variable to compare (default: temperature)",
    )
    return parser.parse_args()


def load_observations(path: Path, value_column: str) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        usecols=["startDateTime", "height", value_column],
        parse_dates=["startDateTime"],
    )
    df["height"] = pd.to_numeric(df["height"], errors="coerce")
    df["value"] = pd.to_numeric(df[value_column], errors="coerce")
    df = df.dropna(subset=["startDateTime", "height", "value"]).copy()
    df["year"] = df["startDateTime"].dt.year
    df["month"] = df["startDateTime"].dt.month
    return (
        df[df["year"].isin(YEARS) & df["month"].isin(MONTHS)]
        .groupby(["year", "month", "height"], as_index=False)
        .agg(value=("value", "mean"))
    )


def load_model_profile(
    path: Path,
    expected_hours: int,
    model_value_column: int,
    kelvin_to_celsius: bool,
) -> tuple[pd.DataFrame | None, str | None]:
    # profile.out is whitespace-delimited. Column 2 is height (m).
    # The requested model value column is selected by the caller.
    df = pd.read_csv(
        path,
        sep=r"\s+",
        header=None,
        usecols=[0, 1, model_value_column],
        names=["model_time", "height", "model_value"],
        on_bad_lines="skip",
    )
    valid_times = pd.to_numeric(df["model_time"], errors="coerce").nunique()
    if valid_times != expected_hours:
        return (
            None,
            f"incomplete ({valid_times}/{expected_hours} hourly time steps)",
        )
    df["height"] = pd.to_numeric(df["height"], errors="coerce")
    df["model_value"] = pd.to_numeric(df["model_value"], errors="coerce")
    df = df[
        df["height"].notna()
        & df["model_value"].notna()
        & (df["model_value"] > -900)
    ].copy()
    df["value"] = (
        df["model_value"] - 273.15
        if kelvin_to_celsius
        else df["model_value"]
    )
    profile = (
        df.groupby("height", as_index=False)
        .agg(value=("value", "mean"))
        .sort_values("height")
    )
    if profile.empty:
        return None, "no valid temperature values"
    return profile, None


def draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    fill: str,
    width: int = 7,
    dash: float = 30,
    gap: float = 20,
) -> None:
    import math

    for (x1, y1), (x2, y2) in zip(points[:-1], points[1:]):
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        ux, uy = dx / length, dy / length
        position = 0.0
        while position < length:
            end = min(position + dash, length)
            draw.line(
                (
                    x1 + ux * position,
                    y1 + uy * position,
                    x1 + ux * end,
                    y1 + uy * end,
                ),
                fill=fill,
                width=width,
            )
            position += dash + gap


def draw_dotted_line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    fill: str,
    radius: float = 4.5,
    spacing: float = 34,
) -> None:
    """Draw separated circular dots along a polyline."""
    import math

    for (x1, y1), (x2, y2) in zip(points[:-1], points[1:]):
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        ux, uy = dx / length, dy / length
        position = 0.0
        while position < length:
            x = x1 + ux * position
            y = y1 + uy * position
            draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                fill=fill,
            )
            position += spacing


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    path = next((p for p in candidates if Path(p).exists()), None)
    return ImageFont.truetype(path, size) if path else ImageFont.load_default()


def plot_comparison(
    site: str,
    year: int,
    obs: pd.DataFrame,
    models: dict[int, pd.DataFrame],
    unavailable_models: dict[int, str],
    output_path: Path,
    dpi: int,
    variable_label: str,
    x_label: str,
    clamp_x_to_zero: bool,
) -> None:
    width, height_px = 1440, 1320
    left, right, top, bottom = 165, 90, 105, 150
    plot_w = width - left - right
    plot_h = height_px - top - bottom
    image = Image.new("RGB", (width, height_px), "white")
    draw = ImageDraw.Draw(image)
    title_font, label_font = font(34), font(27)
    tick_font, legend_font, note_font = font(22), font(20), font(18)

    obs_year = obs[obs["year"] == year]
    x_values = [obs_year["value"]]
    y_values = [obs_year["height"]]
    for profile in models.values():
        if not profile.empty:
            x_values.append(profile["value"])
            y_values.append(profile["height"])
    all_x = pd.concat(x_values).dropna()
    all_y = pd.concat(y_values).dropna()
    if all_x.empty or all_y.empty:
        xmin, xmax, ymin, ymax = 0.0, 1.0, 0.0, 1.0
    else:
        xmin, xmax = float(all_x.min()), float(all_x.max())
        ymin, ymax = 0.0, float(all_y.max())
        xpad = max((xmax - xmin) * 0.08, 0.5)
        ypad = max(ymax * 0.04, 0.5)
        xmin, xmax, ymax = xmin - xpad, xmax + xpad, ymax + ypad
        if clamp_x_to_zero:
            xmin = 0.0

    def px_x(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * plot_w

    def px_y(value: float) -> float:
        return top + plot_h - (value - ymin) / (ymax - ymin) * plot_h

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

    for month in MONTHS:
        color = COLORS[month]
        observed = obs_year[obs_year["month"] == month].sort_values("height")
        obs_points = [
            (px_x(float(row.value)), px_y(float(row.height)))
            for row in observed.itertuples()
        ]
        if len(obs_points) > 1:
            draw.line(obs_points, fill=color, width=6, joint="curve")
        for x, y in obs_points:
            draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=color, outline="white", width=2)

        model = models.get(month)
        if model is not None and not model.empty:
            model_points = [
                (px_x(float(row.value)), px_y(float(row.height)))
                for row in model.itertuples()
            ]
            draw_dotted_line(
                draw,
                model_points,
                color,
                radius=4.5,
                spacing=34,
            )

    title = f"{site} Observed vs Model {variable_label} Profiles — {year}"
    box = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((width - (box[2] - box[0])) / 2, 35), title, fill="black", font=title_font)
    xlabel = x_label
    box = draw.textbbox((0, 0), xlabel, font=label_font)
    draw.text(((width - (box[2] - box[0])) / 2, height_px - 60), xlabel, fill="black", font=label_font)

    ylabel = "Height (m)"
    label_img = Image.new("RGBA", (190, 60), (255, 255, 255, 0))
    ImageDraw.Draw(label_img).text((0, 5), ylabel, fill="black", font=label_font)
    label_img = label_img.rotate(90, expand=True)
    image.paste(label_img, (28, (height_px - label_img.height) // 2), label_img)

    # Month legend.
    lx, ly = left + 25, top + 20
    for index, month in enumerate(MONTHS):
        y = ly + index * 34
        draw.line((lx, y + 10, lx + 34, y + 10), fill=COLORS[month], width=6)
        draw.text((lx + 44, y), MONTH_NAMES[month], fill="black", font=legend_font)

    # Line-style legend.
    sx, sy = lx + 130, ly
    draw.line((sx, sy + 10, sx + 42, sy + 10), fill="#444444", width=6)
    draw.ellipse((sx + 15, sy + 3, sx + 29, sy + 17), fill="#444444", outline="white", width=2)
    draw.text((sx + 52, sy), "Observed", fill="black", font=legend_font)
    draw_dotted_line(
        draw,
        [(sx, sy + 46), (sx + 54, sy + 46)],
        "#444444",
        radius=4.5,
        spacing=18,
    )
    draw.text((sx + 68, sy + 36), "Model", fill="black", font=legend_font)

    if unavailable_models:
        names = ", ".join(
            f"{MONTH_NAMES[m]} ({reason})"
            for m, reason in unavailable_models.items()
        )
        note = f"Model unavailable: {names}"
        draw.text((left + 25, top + plot_h - 35), note, fill="#555555", font=note_font)

    image.save(output_path, format="PNG", dpi=(dpi, dpi))


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    generated = []
    missing_summary = []

    for site in SITES:
        if args.variable == "temperature":
            obs_path = (
                args.project_dir
                / f"{site}_air_temperature_hourly_all_levels_NQF.csv"
            )
            value_column = "temperature"
            model_value_column = 25
            kelvin_to_celsius = True
            variable_label = "Air-Temperature"
            x_label = "Monthly mean air temperature (°C)"
            clamp_x_to_zero = False
        else:
            obs_path = (
                args.project_dir
                / "NEON_windspeed"
                / f"{site}_wind_hourly_all_levels.csv"
            )
            value_column = "windSpeedMean"
            model_value_column = 24
            kelvin_to_celsius = False
            variable_label = "Wind-Speed"
            x_label = "Monthly mean wind speed (m/s)"
            clamp_x_to_zero = True

        obs = load_observations(obs_path, value_column)
        model_dir = args.project_dir / site / "ml"

        for year in YEARS:
            models = {}
            unavailable = {}
            for month in MONTHS:
                model_path = model_dir / f"{site}66_{year}-{month:02d}_profile.out"
                if model_path.exists():
                    expected_hours = calendar.monthrange(year, month)[1] * 24
                    profile, problem = load_model_profile(
                        model_path,
                        expected_hours,
                        model_value_column,
                        kelvin_to_celsius,
                    )
                    if problem is None:
                        models[month] = profile
                    else:
                        unavailable[month] = problem
                        missing_summary.append(
                            f"{site} {year}-{month:02d}: {problem}"
                        )
                else:
                    unavailable[month] = "file missing"
                    missing_summary.append(
                        f"{site} {year}-{month:02d}: file missing"
                    )

            output_path = (
                args.output_dir
                / f"{site}_{year}_{args.variable}_observed_vs_model.png"
            )
            plot_comparison(
                site,
                year,
                obs,
                models,
                unavailable,
                output_path,
                args.dpi,
                variable_label,
                x_label,
                clamp_x_to_zero,
            )
            generated.append(output_path)
            print(f"Saved {output_path}")

    print(f"Generated {len(generated)} PNG files")
    if missing_summary:
        print("Missing model profiles:")
        for item in missing_summary:
            print(f"  {item}")


if __name__ == "__main__":
    main()
