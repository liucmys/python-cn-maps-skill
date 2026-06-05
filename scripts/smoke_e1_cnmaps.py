"""Smoke test: national contourf + border clip (examples.md E1)."""

from __future__ import annotations

import os
from pathlib import Path

import cartopy.crs as ccrs
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cnmaps import clip_contours_by_map, draw_map, get_adm_maps
from cnmaps.sample import load_temp

SKILL_ROOT = Path(__file__).resolve().parents[1]
OUT = SKILL_ROOT / "artifacts" / "e1_smoke.png"
MIN_BYTES = 10_000

data_crs = ccrs.PlateCarree()
lons, lats, temp = load_temp()
china = get_adm_maps(country="中国", level="国", record="first", only_polygon=True)

fig, ax = plt.subplots(subplot_kw={"projection": data_crs}, figsize=(10, 8))
cs = ax.contourf(lons, lats, temp, levels=20, cmap="coolwarm", transform=data_crs)
clip_contours_by_map(cs, china, ax=ax)
draw_map(china, ax=ax, color="k", linewidth=0.8)
ax.set_extent(china.get_extent(buffer=1), crs=data_crs)
OUT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT, dpi=150, bbox_inches="tight")
plt.close(fig)

size = OUT.stat().st_size
print(f"Wrote {OUT} ({size} bytes)")
if size < MIN_BYTES:
    raise SystemExit(f"Output too small (< {MIN_BYTES} bytes)")
