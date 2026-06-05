# 示例模板

完整可运行片段；数据除注明外用 cnmaps 样例或 frykit 测试数据。

---

## E1 全国 contourf + 国界裁剪（cnmaps）

```python
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cnmaps import clip_contours_by_map, draw_map, get_adm_maps
from cnmaps.sample import load_temp

data_crs = ccrs.PlateCarree()
lons, lats, temp = load_temp()
china = get_adm_maps(country="中国", level="国", record="first", only_polygon=True)

fig, ax = plt.subplots(subplot_kw={"projection": data_crs}, figsize=(10, 8))
cs = ax.contourf(lons, lats, temp, levels=20, cmap="coolwarm", transform=data_crs)
clip_contours_by_map(cs, china, ax=ax)
draw_map(china, ax=ax, color="k", linewidth=0.8)
ax.set_extent(china.get_extent(buffer=1), crs=data_crs)
plt.colorbar(cs, ax=ax, orientation="horizontal", pad=0.05)
plt.savefig("e1_contourf_china.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## E2 区域高亮：省底 + 市界 + 市高亮（cnmaps）

```python
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cnmaps import draw_maps, get_adm_maps

data_crs = ccrs.PlateCarree()
province = get_adm_maps(province="河南省", record="first", only_polygon=True)
city = get_adm_maps(city="南阳市", record="first", only_polygon=True)

fig, ax = plt.subplots(subplot_kw={"projection": data_crs}, figsize=(8, 8))
ax.add_geometries(province, crs=data_crs, edgecolor="grey", facecolor="grey")
ax.add_geometries(city, crs=data_crs, edgecolor="crimson", facecolor="crimson")
draw_maps(get_adm_maps(province="河南省", level="市"), ax=ax, color="w", linewidth=0.8)
ax.set_extent(province.get_extent(buffer=0.5), crs=data_crs)
plt.savefig("e2_henan_highlight.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## E3 气温填色 + 风场 + 裁剪（frykit）

参考 [frykit/example/quiver.py](https://github.com/ZhaJiMan/frykit/blob/main/example/quiver.py)。

```python
import matplotlib.pyplot as plt
import numpy as np
import frykit.plot as fplt

data_crs = fplt.PLATE_CARREE
data = fplt.load_test_data()
X, Y = np.meshgrid(data.lon, data.lat)
t2m = data.t2m - 273.15
u, v = data.u10, data.v10

fig, ax = plt.subplots(subplot_kw={"projection": fplt.CN_AZIMUTHAL_EQUIDISTANT}, figsize=(8, 5))
ax.set_extent((78, 128, 15, 55), crs=data_crs)
fplt.add_cn_province(ax, lw=0.4)

cf = ax.contourf(X, Y, t2m, levels=np.linspace(-10, 35, 10),
                 cmap="plasma", extend="both", transform=data_crs, transform_first=True)
Q = ax.quiver(X, Y, u, v, scale=40, scale_units="inches",
              regrid_shape=35, transform=data_crs)
fplt.add_quiver_legend(Q, U=10, height=0.12)
fplt.clip_by_cn_border(cf)
fplt.clip_by_cn_border(Q)
plt.colorbar(cf, ax=ax, label="Temperature (℃)")
plt.savefig("e3_temp_wind.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## E4 南海小图 + 指北针 + 比例尺（frykit）

参考 [frykit/example/contourf.py](https://github.com/ZhaJiMan/frykit/blob/main/example/contourf.py)。

```python
import matplotlib.pyplot as plt
import numpy as np
from cartopy.feature import LAND
import frykit.plot as fplt

data_crs = fplt.PLATE_CARREE
data = fplt.load_test_data()
X, Y = np.meshgrid(data.lon, data.lat)
Z = data.t2m - 273.15

fig = plt.figure(figsize=(10, 6))
main_ax = fig.add_subplot(projection=fplt.CN_AZIMUTHAL_EQUIDISTANT)
fplt.set_map_ticks(main_ax, (74, 136, 13, 57), dx=10, dy=10)

mini_ax = fplt.add_mini_axes(main_ax)
mini_ax.set_extent((105, 122, 2, 25), crs=data_crs)

for ax in (main_ax, mini_ax):
    ax.set_facecolor("skyblue")
    ax.add_feature(LAND, fc="floralwhite", ec="k", lw=0.5)
    fplt.add_cn_province(ax, lw=0.3)
    fplt.add_cn_line(ax, lw=0.5)
    cf = ax.contourf(X, Y, Z, levels=np.linspace(0, 32, 30),
                     cmap="turbo", transform=data_crs, transform_first=True)
    fplt.clip_by_cn_border(cf)

fplt.add_compass(main_ax, 0.92, 0.85, size=15)
sb = fplt.add_scale_bar(main_ax, 0.05, 0.1, length=1000)
sb.set_xticks([0, 500, 1000])
plt.colorbar(cf, ax=main_ax, orientation="horizontal", pad=0.08)
plt.savefig("e4_scs_inset.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## E5 多子图循环 + 显式 ax 裁剪（cnmaps）

```python
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from cnmaps import clip_contours_by_map, draw_map, get_adm_maps
from cnmaps.sample import load_temp

data_crs = ccrs.PlateCarree()
lons, lats, temp = load_temp()
boundary = get_adm_maps(province="四川省", record="first", only_polygon=True)
extent = boundary.get_extent(buffer=0.2)

fig, axes = plt.subplots(1, 3, figsize=(12, 4),
                         subplot_kw={"projection": data_crs})
levels = np.linspace(temp.min(), temp.max(), 15)

for i, ax in enumerate(axes):
  offset = i * 2.0
  cs = ax.contourf(lons, lats, temp + offset, levels=levels,
                   cmap="viridis", transform=data_crs)
  clip_contours_by_map(cs, boundary, ax=ax, extent=extent, set_extent=True)
  draw_map(boundary, ax=ax, color="k", linewidth=0.8)
  ax.set_title(f"Panel {i+1}")

plt.tight_layout()
plt.savefig("e5_multi_panel.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## E6 绘前掩膜 + pcolormesh（cnmaps）

```python
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cnmaps import draw_map, get_adm_maps
from cnmaps.sample import load_dem

data_crs = ccrs.PlateCarree()
lons, lats, dem = load_dem()
china = get_adm_maps(country="中国", level="国", record="first", only_polygon=True)
dem_masked = china.maskout(lons, lats, dem)

fig, ax = plt.subplots(subplot_kw={"projection": data_crs}, figsize=(10, 8))
mesh = ax.pcolormesh(lons, lats, dem_masked, cmap="terrain",
                     vmin=-2800, transform=data_crs)
draw_map(china, ax=ax, color="k", linewidth=0.6)
ax.set_extent(china.get_extent(), crs=data_crs)
plt.colorbar(mesh, ax=ax)
plt.savefig("e6_masked_dem.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## E7 普通 Axes 经纬度地图（frykit，无 GeoAxes）

参考 [frykit/example/axes.py](https://github.com/ZhaJiMan/frykit/blob/main/example/axes.py)。

```python
import matplotlib.pyplot as plt
import frykit.plot as fplt

fig, ax = plt.subplots(figsize=(8, 6))
ax.set_aspect(1)
ax.set_facecolor("#c4e7fa")
fplt.add_countries(ax, fc="#e7e4e2")
fplt.add_cn_province(ax, fc="#fcfeff")
fplt.add_cn_line(ax)
fplt.set_map_ticks(ax, (70, 140, 0, 60), dx=10, dy=10)
fplt.add_frame(ax)
ax.grid(ls="--", c="gray")
plt.savefig("e7_plain_axes.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## E8 DEM 地形线 + 气温场 2.5D（cnmaps）

```python
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from cnmaps import clip_contours_by_map, draw_map, get_adm_maps
from cnmaps.sample import load_dem, load_temp

data_crs = ccrs.PlateCarree()
lon_d, lat_d, dem = load_dem()
lon_t, lat_t, temp = load_temp()
china = get_adm_maps(country="中国", level="国", record="first", only_polygon=True)

fig, ax = plt.subplots(subplot_kw={"projection": data_crs}, figsize=(10, 8))
# 地形等高线（高度维）
terrain = ax.contour(lon_d, lat_d, dem, levels=np.arange(0, 4000, 500),
                     colors="saddlebrown", linewidths=0.6, transform=data_crs)
# 气温填色（2D 场）
cs = ax.contourf(lon_t, lat_t, temp, levels=20, cmap="RdYlBu_r",
                 alpha=0.85, transform=data_crs)
clip_contours_by_map(cs, china, ax=ax)
draw_map(china, ax=ax, color="k", linewidth=0.8)
ax.set_extent(china.get_extent(buffer=1), crs=data_crs)
plt.colorbar(cs, ax=ax, label="Temperature")
plt.savefig("e8_dem_temp.png", dpi=300, bbox_inches="tight")
plt.show()
```

---

## 官方 cnmaps 示例索引

仓库 [cnmaps-python-assistant/examples](https://github.com/cnmetlab/cnmaps/tree/main/cnmaps/_bundled_skills/shared/cnmaps-python-assistant/examples)：

- `plot-boundary-example.py` — 国界
- `mask-raster-example.py` — maskout
- `clip-pcolormesh-example.py` / `clip-quiver-example.py` / `clip-clabels-example.py`
- `province-selection-example.py` / `multi-region-selection-example.py`
- `vector-export-example.py`

Codex 版 [plotting-patterns.md](https://github.com/cnmetlab/cnmaps/blob/main/cnmaps/_bundled_skills/platforms/codex/cnmaps-python-assistant/references/plotting-patterns.md) 含更完整片段。
