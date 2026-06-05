"""Smoke test: temperature fill + wind quiver + clip (examples.md E3)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import frykit.plot as fplt

SKILL_ROOT = Path(__file__).resolve().parents[1]
OUT = SKILL_ROOT / "artifacts" / "e3_smoke.png"
MIN_BYTES = 10_000

data_crs = fplt.PLATE_CARREE
data = fplt.load_test_data()
X, Y = np.meshgrid(data.lon, data.lat)
t2m = data.t2m - 273.15
u, v = data.u10, data.v10

fig, ax = plt.subplots(subplot_kw={"projection": fplt.CN_AZIMUTHAL_EQUIDISTANT}, figsize=(8, 5))
ax.set_extent((78, 128, 15, 55), crs=data_crs)
fplt.add_cn_province(ax, lw=0.4)

cf = ax.contourf(
    X,
    Y,
    t2m,
    levels=np.linspace(-10, 35, 10),
    cmap="plasma",
    extend="both",
    transform=data_crs,
    transform_first=True,
)
Q = ax.quiver(
    X, Y, u, v, scale=40, scale_units="inches", regrid_shape=35, transform=data_crs
)
fplt.add_quiver_legend(Q, U=10, height=0.12)
fplt.clip_by_cn_border(cf)
fplt.clip_by_cn_border(Q)
OUT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT, dpi=150, bbox_inches="tight")
plt.close(fig)

size = OUT.stat().st_size
print(f"Wrote {OUT} ({size} bytes)")
if size < MIN_BYTES:
    raise SystemExit(f"Output too small (< {MIN_BYTES} bytes)")
