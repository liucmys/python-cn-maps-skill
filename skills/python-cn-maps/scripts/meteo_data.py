"""Load common meteorological data files into lon/lat/value grids.

Supported inputs:
- CSV point grids with longitude, latitude, and value columns.
- Station time-series CSV directories joined with a station metadata table.
- NetCDF files readable by xarray.
- GRIB/GRIB2 files readable by xarray with the cfgrib engine.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


LON_CANDIDATES = (
    "lon",
    "lons",
    "longitude",
    "longitudes",
    "x",
)
LAT_CANDIDATES = (
    "lat",
    "lats",
    "latitude",
    "latitudes",
    "y",
)
STATION_ID_CANDIDATES = (
    "obtid",
    "station",
    "station_id",
    "stationid",
    "id",
)
NON_SPATIAL_DIMS = {
    "time",
    "valid_time",
    "step",
    "forecast_time",
    "member",
    "number",
    "level",
    "isobaricinhpa",
    "pressure",
    "height",
    "depth",
    "surface",
}


@dataclass(frozen=True)
class MeteoGrid:
    """A normalized meteorological grid ready for Cartopy plotting."""

    lon: np.ndarray
    lat: np.ndarray
    values: np.ndarray
    variable: str
    units: str | None = None
    source: str | None = None

    def summary(self) -> dict[str, Any]:
        finite = np.isfinite(self.values)
        lat_values = self.lat[finite] if self.lat.shape == self.values.shape else self.lat
        lon_values = self.lon[finite] if self.lon.shape == self.values.shape else self.lon
        vals = self.values[finite]
        if vals.size == 0:
            raise ValueError("No finite values found in selected field")

        return {
            "source": self.source,
            "variable": self.variable,
            "units": self.units,
            "shape": list(self.values.shape),
            "lon_shape": list(self.lon.shape),
            "lat_shape": list(self.lat.shape),
            "lon_min": float(np.nanmin(lon_values)),
            "lon_max": float(np.nanmax(lon_values)),
            "lat_min": float(np.nanmin(lat_values)),
            "lat_max": float(np.nanmax(lat_values)),
            "value_min": float(np.nanmin(vals)),
            "value_max": float(np.nanmax(vals)),
            "value_mean": float(np.nanmean(vals)),
            "value_std": float(np.nanstd(vals)),
            "missing_fraction": float(1.0 - finite.sum() / finite.size),
        }


@dataclass(frozen=True)
class StationPoints:
    """Station-level values joined with longitude/latitude metadata."""

    records: list[dict[str, Any]]
    variable: str
    source: str | None = None
    metadata_source: str | None = None

    def summary(self) -> dict[str, Any]:
        values = np.asarray([row["value"] for row in self.records], dtype=float)
        lon = np.asarray([row["lon"] for row in self.records], dtype=float)
        lat = np.asarray([row["lat"] for row in self.records], dtype=float)
        finite = np.isfinite(values)
        if not finite.any():
            raise ValueError("No finite station values found")
        return {
            "source": self.source,
            "metadata_source": self.metadata_source,
            "variable": self.variable,
            "station_count": len(self.records),
            "finite_station_count": int(finite.sum()),
            "lon_min": float(np.nanmin(lon)),
            "lon_max": float(np.nanmax(lon)),
            "lat_min": float(np.nanmin(lat)),
            "lat_max": float(np.nanmax(lat)),
            "value_min": float(np.nanmin(values[finite])),
            "value_max": float(np.nanmax(values[finite])),
            "value_mean": float(np.nanmean(values[finite])),
            "value_std": float(np.nanstd(values[finite])),
            "missing_fraction": float(1.0 - finite.sum() / finite.size),
        }


def load_meteo_grid(
    path: str | Path,
    variable: str | None = None,
    *,
    lon_name: str | None = None,
    lat_name: str | None = None,
    value_column: str | None = None,
    csv_sep: str = ",",
    grib_filter_by_keys: dict[str, Any] | None = None,
) -> MeteoGrid:
    """Load CSV, NetCDF, or GRIB into a normalized grid."""

    data_path = Path(path)
    suffix = data_path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        return _load_csv_grid(
            data_path,
            variable=variable,
            lon_name=lon_name,
            lat_name=lat_name,
            value_column=value_column,
            sep=csv_sep,
        )
    if suffix in {".nc", ".nc4", ".cdf", ".netcdf"}:
        return _load_xarray_grid(
            data_path,
            variable=variable,
            lon_name=lon_name,
            lat_name=lat_name,
            engine=None,
        )
    if suffix in {".grib", ".grb", ".grib2", ".grb2"}:
        return _load_xarray_grid(
            data_path,
            variable=variable,
            lon_name=lon_name,
            lat_name=lat_name,
            engine="cfgrib",
            backend_kwargs={"filter_by_keys": grib_filter_by_keys}
            if grib_filter_by_keys
            else None,
        )

    raise ValueError(
        f"Unsupported file extension {suffix!r}; expected CSV, NetCDF, or GRIB."
    )


def load_station_points(
    station_csv_dir: str | Path,
    metadata_csv: str | Path,
    variable: str,
    *,
    station_id_name: str | None = None,
    metadata_station_id_name: str | None = None,
    lon_name: str | None = None,
    lat_name: str | None = None,
    filename_station_part: int = 0,
    filename_separator: str = "_",
    csv_sep: str = ",",
) -> StationPoints:
    """Aggregate station time-series files and join them with lon/lat metadata."""

    pd = _import_pandas()
    station_dir = Path(station_csv_dir)
    meta_path = Path(metadata_csv)
    if not station_dir.is_dir():
        raise ValueError(f"Station CSV path is not a directory: {station_dir}")

    metadata = pd.read_csv(meta_path, sep=csv_sep)
    meta_id_col = metadata_station_id_name or _pick_name(
        metadata.columns, STATION_ID_CANDIDATES, "metadata station id"
    )
    lon_col = lon_name or _pick_name(metadata.columns, LON_CANDIDATES, "longitude")
    lat_col = lat_name or _pick_name(metadata.columns, LAT_CANDIDATES, "latitude")
    metadata = metadata[[meta_id_col, lon_col, lat_col]].copy()
    metadata[meta_id_col] = metadata[meta_id_col].astype(str)
    metadata[lon_col] = _to_numeric(metadata[lon_col])
    metadata[lat_col] = _to_numeric(metadata[lat_col])
    metadata = metadata.dropna(subset=[meta_id_col, lon_col, lat_col])

    records: list[dict[str, Any]] = []
    for csv_path in sorted(station_dir.glob("*.csv")):
        df = pd.read_csv(csv_path, sep=csv_sep)
        if df.empty or variable not in df.columns:
            continue
        if station_id_name and station_id_name in df.columns:
            station_id = str(df[station_id_name].dropna().astype(str).iloc[0])
        elif "obtid" in {str(name).lower() for name in df.columns}:
            station_col = _pick_name(df.columns, ("obtid",), "station id")
            station_id = str(df[station_col].dropna().astype(str).iloc[0])
        else:
            parts = csv_path.stem.split(filename_separator)
            try:
                station_id = parts[filename_station_part]
            except IndexError as exc:
                raise ValueError(f"Cannot infer station id from filename: {csv_path.name}") from exc

        value = _to_numeric(df[variable]).replace(
            [-999, -999.0, -999.9, -9999, 999999],
            np.nan,
        ).mean()
        records.append({"station_id": station_id, "value": float(value)})

    if not records:
        raise ValueError(f"No station CSV files with variable {variable!r} found in {station_dir}")

    values = pd.DataFrame.from_records(records)
    joined = values.merge(metadata, left_on="station_id", right_on=meta_id_col, how="inner")
    if joined.empty:
        raise ValueError("No station values matched station metadata")

    station_records = [
        {
            "station_id": str(row["station_id"]),
            "lon": float(row[lon_col]),
            "lat": float(row[lat_col]),
            "value": float(row["value"]),
        }
        for _, row in joined.iterrows()
    ]
    return StationPoints(
        records=station_records,
        variable=variable,
        source=str(station_dir),
        metadata_source=str(meta_path),
    )


def _load_csv_grid(
    path: Path,
    *,
    variable: str | None,
    lon_name: str | None,
    lat_name: str | None,
    value_column: str | None,
    sep: str,
) -> MeteoGrid:
    pd = _import_pandas()
    df = pd.read_csv(path, sep=sep)
    if df.empty:
        raise ValueError(f"CSV has no rows: {path}")

    lon_col = lon_name or _pick_name(df.columns, LON_CANDIDATES, "longitude")
    lat_col = lat_name or _pick_name(df.columns, LAT_CANDIDATES, "latitude")
    val_col = value_column or variable or _pick_value_column(df.columns, lon_col, lat_col)

    missing = [name for name in (lon_col, lat_col, val_col) if name not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required column(s): {', '.join(missing)}")

    work = df[[lon_col, lat_col, val_col]].dropna(subset=[lon_col, lat_col])
    if work.empty:
        raise ValueError("CSV has no rows with both longitude and latitude")

    grouped = work.groupby([lat_col, lon_col], as_index=False)[val_col].mean()
    table = grouped.pivot(index=lat_col, columns=lon_col, values=val_col)
    table = table.sort_index().sort_index(axis=1)

    lon_1d = table.columns.to_numpy(dtype=float)
    lat_1d = table.index.to_numpy(dtype=float)
    lon, lat = np.meshgrid(lon_1d, lat_1d)
    values = table.to_numpy(dtype=float)
    return MeteoGrid(
        lon=lon,
        lat=lat,
        values=values,
        variable=str(val_col),
        source=str(path),
    )


def _load_xarray_grid(
    path: Path,
    *,
    variable: str | None,
    lon_name: str | None,
    lat_name: str | None,
    engine: str | None,
    backend_kwargs: dict[str, Any] | None = None,
) -> MeteoGrid:
    xr = _import_xarray()
    open_kwargs: dict[str, Any] = {}
    if engine:
        open_kwargs["engine"] = engine
    if backend_kwargs:
        open_kwargs["backend_kwargs"] = backend_kwargs

    with xr.open_dataset(path, **open_kwargs) as ds:
        var_name = variable or _pick_data_variable(ds)
        if var_name not in ds:
            raise ValueError(
                f"Variable {var_name!r} not found. Available variables: "
                f"{', '.join(ds.data_vars)}"
            )

        data = ds[var_name]
        lon_coord_name = lon_name or _find_coord_name(ds, data, LON_CANDIDATES, "longitude")
        lat_coord_name = lat_name or _find_coord_name(ds, data, LAT_CANDIDATES, "latitude")
        data = _select_first_non_spatial(data, lon_coord_name, lat_coord_name)

        lon = ds[lon_coord_name]
        lat = ds[lat_coord_name]
        values = np.asarray(data.load().values, dtype=float)
        lon_array, lat_array = _broadcast_lon_lat(lon, lat, values.shape)
        units = data.attrs.get("units")

    return MeteoGrid(
        lon=lon_array,
        lat=lat_array,
        values=values,
        variable=var_name,
        units=str(units) if units else None,
        source=str(path),
    )


def _select_first_non_spatial(data: Any, lon_name: str, lat_name: str) -> Any:
    keep = set()
    keep.update(_coord_dims(data, lon_name))
    keep.update(_coord_dims(data, lat_name))
    keep.add(lon_name)
    keep.add(lat_name)

    indexers: dict[str, int] = {}
    for dim in data.dims:
        if dim in keep:
            continue
        dim_key = dim.lower()
        if dim_key in NON_SPATIAL_DIMS or data.sizes[dim] == 1:
            indexers[dim] = 0
        else:
            raise ValueError(
                f"Cannot reduce non-spatial dimension {dim!r}; select it before plotting."
            )
    if indexers:
        data = data.isel(indexers)
    return data.squeeze(drop=True)


def _broadcast_lon_lat(lon: Any, lat: Any, data_shape: tuple[int, ...]) -> tuple[np.ndarray, np.ndarray]:
    lon_values = np.asarray(lon.values, dtype=float)
    lat_values = np.asarray(lat.values, dtype=float)
    if lon_values.ndim == 1 and lat_values.ndim == 1:
        if data_shape != (lat_values.size, lon_values.size):
            if data_shape == (lon_values.size, lat_values.size):
                raise ValueError(
                    "Data shape appears transposed relative to latitude/longitude."
                )
            raise ValueError(
                f"Data shape {data_shape} does not match lat/lon sizes "
                f"{lat_values.size}/{lon_values.size}."
            )
        return np.meshgrid(lon_values, lat_values)

    if lon_values.shape == data_shape and lat_values.shape == data_shape:
        return lon_values, lat_values

    raise ValueError(
        f"Unsupported lon/lat shapes {lon_values.shape}/{lat_values.shape} "
        f"for data shape {data_shape}."
    )


def _pick_name(names: Any, candidates: tuple[str, ...], label: str) -> str:
    by_lower = {str(name).lower(): str(name) for name in names}
    for candidate in candidates:
        if candidate in by_lower:
            return by_lower[candidate]
    raise ValueError(f"Could not identify {label} name from: {', '.join(map(str, names))}")


def _pick_value_column(names: Any, lon_col: str, lat_col: str) -> str:
    excluded = {lon_col, lat_col}
    excluded_lower = {name.lower() for name in excluded}
    candidates = [
        str(name)
        for name in names
        if str(name).lower() not in excluded_lower
        and not str(name).lower().startswith(("time", "date", "station"))
    ]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ValueError("Could not find a value column in CSV")
    raise ValueError(
        "Multiple possible value columns; pass --variable or --value-column. "
        f"Candidates: {', '.join(candidates)}"
    )


def _to_numeric(values: Any) -> Any:
    pd = _import_pandas()
    return pd.to_numeric(values, errors="coerce")


def _pick_data_variable(ds: Any) -> str:
    candidates = [name for name, var in ds.data_vars.items() if var.ndim >= 2]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ValueError("Dataset has no 2D-or-higher data variables")
    raise ValueError(
        "Multiple data variables; pass --variable. "
        f"Candidates: {', '.join(candidates)}"
    )


def _find_coord_name(ds: Any, data: Any, candidates: tuple[str, ...], label: str) -> str:
    search_names = list(data.coords) + list(data.dims) + list(ds.coords) + list(ds.variables)
    return _pick_name(search_names, candidates, label)


def _coord_dims(data: Any, coord_name: str) -> tuple[str, ...]:
    if coord_name in data.coords:
        return tuple(data.coords[coord_name].dims)
    if coord_name in data.dims:
        return (coord_name,)
    return ()


def _import_pandas() -> Any:
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("Missing pandas. Run `uv sync` in the skill directory.") from exc
    return pd


def _import_xarray() -> Any:
    try:
        import xarray as xr
    except ImportError as exc:
        raise SystemExit("Missing xarray. Run `uv sync` in the skill directory.") from exc
    return xr


def _parse_filter_by_keys(text: str | None) -> dict[str, Any] | None:
    if not text:
        return None
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--filter-by-keys must be JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("--filter-by-keys must decode to a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV, NetCDF, GRIB, or GRIB2 input file")
    parser.add_argument("--variable", help="Variable or CSV value column to read")
    parser.add_argument(
        "--station-metadata",
        type=Path,
        help="Station metadata CSV with station id, lon, and lat columns",
    )
    parser.add_argument("--station-id", help="Station id column name in station CSV files")
    parser.add_argument(
        "--metadata-station-id",
        help="Station id column name in station metadata CSV",
    )
    parser.add_argument("--lon", dest="lon_name", help="Longitude coordinate/column name")
    parser.add_argument("--lat", dest="lat_name", help="Latitude coordinate/column name")
    parser.add_argument("--value-column", help="CSV value column name")
    parser.add_argument("--csv-sep", default=",", help="CSV delimiter, default comma")
    parser.add_argument(
        "--filter-by-keys",
        help='GRIB cfgrib filter_by_keys JSON, e.g. {"typeOfLevel":"surface"}',
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Summary output format",
    )
    args = parser.parse_args(argv)

    if args.station_metadata:
        if not args.variable:
            raise SystemExit("--variable is required with --station-metadata")
        points = load_station_points(
            args.input,
            args.station_metadata,
            args.variable,
            station_id_name=args.station_id,
            metadata_station_id_name=args.metadata_station_id,
            lon_name=args.lon_name,
            lat_name=args.lat_name,
            csv_sep=args.csv_sep,
        )
        summary = points.summary()
        if args.format == "json":
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            for key, value in summary.items():
                print(f"{key}: {value}")
        return 0

    grid = load_meteo_grid(
        args.input,
        variable=args.variable,
        lon_name=args.lon_name,
        lat_name=args.lat_name,
        value_column=args.value_column,
        csv_sep=args.csv_sep,
        grib_filter_by_keys=_parse_filter_by_keys(args.filter_by_keys),
    )
    summary = grid.summary()
    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        for key, value in summary.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
