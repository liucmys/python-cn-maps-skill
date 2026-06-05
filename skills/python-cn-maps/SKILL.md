---
name: python-cn-maps
description: Use for Python China map plotting and meteorological data work: parse/analyze external CSV, NetCDF, GRIB/GRIB2 files; normalize lon/lat/value grids; draw with matplotlib, Cartopy, cnmaps, and frykit; contourf, pcolormesh, quiver, clipping, masking, administrative boundaries, and South China Sea inset.
---

# python-cn-maps

This skill helps agents turn external meteorological data into China-focused maps.

## Core Workflow

1. Confirm the data path, format, variable name, units, lon/lat coordinate names, time/level selection, and target region.
2. Read external data in place. Do not copy CSV, NetCDF, GRIB, or GRIB2 files into this skill.
3. Before plotting, print a summary: shape, lon/lat range, value range, mean, units, missing fraction, and selected time/level.
4. Normalize the field to `lon`, `lat`, and a 2D `values` array.
5. Create a Cartopy `GeoAxes`; use `ccrs.PlateCarree()` unless the data says otherwise.
6. Plot data with `transform=data_crs` on every `contourf`, `pcolormesh`, `quiver`, `scatter`, or similar geographic artist.
7. Add China or administrative boundaries with cnmaps or frykit.
8. Clip or mask to the requested boundary.
9. Save the figure with `dpi=300` and `bbox_inches="tight"`.

## External Data

Use [scripts/meteo_data.py](scripts/meteo_data.py) when a deterministic data summary is useful.

```bash
python scripts/meteo_data.py data/era5_t2m.nc --variable t2m --format json
python scripts/meteo_data.py data/grid_points.csv --variable t2m_c
python scripts/meteo_data.py data/station_daily --station-metadata data/station_info.csv --variable maxt --metadata-station-id OBTID
python scripts/meteo_data.py data/gfs.grib2 --variable t2m --filter-by-keys '{"typeOfLevel":"surface"}'
```

- CSV: requires longitude and latitude columns (`lon`, `longitude`, `lat`, `latitude`, etc.) plus a value column. Station time-series CSV without lon/lat metadata is not directly plottable as a grid.
- Station time-series CSV: if a separate metadata table exists, join by station id first. Common pattern: daily files contain `obtid`; metadata contains `OBTID, lat, lon, height`; aggregate a variable such as `maxt` or `hourrf` by station, then plot as `scatter(..., transform=data_crs)`.
- NetCDF: read with `xarray.open_dataset`; explicitly select the variable and reduce non-spatial dimensions such as `time`, `valid_time`, `level`, `step`, or `member`.
- GRIB/GRIB2: read with xarray `engine="cfgrib"`; use `filter_by_keys` when a file mixes levels, steps, or message types.
- Common missing sentinels such as `-999`, `-999.9`, and `999999` should be converted to missing values before statistics or plotting when they appear in the data.

## Mapping Rules

- For the China national boundary with cnmaps, use `get_adm_maps(country="中国", level="国", record="first", only_polygon=True)`.
- For national China maps, add the nine-dash line with frykit `add_cn_line(ax)` when the map includes South China Sea context.
- Use full administrative names such as `河南省`, `南阳市`, `广东省`, and `广州市`.
- Prefer cnmaps for querying/combining administrative polygons and `clip_*_by_map`.
- Prefer frykit for quick China boundaries, South China Sea inset, compass, scale bar, and robust China-border clipping.
- In multi-panel figures, pass the correct `ax=` to every draw and clip call.
- Do not mix `Axes3D` into a Cartopy `GeoAxes`; use separate subplots for 3D or vertical sections.

## References

Load only what is needed:

- [references/examples.md](references/examples.md): runnable plotting templates.
- [references/cnmaps.md](references/cnmaps.md): cnmaps API notes.
- [references/frykit.md](references/frykit.md): frykit API notes.
- [references/troubleshooting.md](references/troubleshooting.md): common plotting and clipping problems.
