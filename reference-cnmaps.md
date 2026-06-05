# cnmaps 参考

基于 [cnmaps API](https://cnmaps.readthedocs.io/zh-cn/latest/content/api-ref.html) 与 [官方 bundled skill](https://github.com/cnmetlab/cnmaps/tree/main/cnmaps/_bundled_skills/shared/cnmaps-python-assistant)。

## 安装

```bash
pip install -U cnmaps          # 默认含 cnmaps-data
cnmaps install-skill cursor --mode global --force   # 可选：仅 cnmaps 官方 Skill
```

Python ≥3.9。conda-forge 可能停留在 1.x，2.x 请用 pip。

## 能力边界

| cnmaps 负责 | cnmaps 不负责 |
|-------------|---------------|
| `get_adm_maps` / `get_adm_names` | Cartopy 投影、海岸线、gridlines |
| `draw_map` / `draw_maps` | 色标、子图版式、统计计算 |
| `clip_*_by_map` | xarray 重采样（用户自备） |
| `make_mask_array` / `maskout` | 完整 GIS 工作流 |
| `load_dem` / `load_temp` / `load_wind` 样例 | Natural Earth 中国边界 |
| `read_boundary_file` / `validate_boundary_file` | — |

## 核心 API

### 查询边界

```python
from cnmaps import get_adm_maps, get_adm_names

# 中国国界（单多边形）
china = get_adm_maps(country="中国", level="国", record="first", only_polygon=True)

# 省界列表
provinces = get_adm_maps(level="省")  # list[MapRecord] 或 MapPolygon 列表

# 单省
henan = get_adm_maps(province="河南省", record="first", only_polygon=True)

# 批量
jjj = get_adm_maps(province=["北京市", "天津市", "河北省"], level="省", only_polygon=True)

# 全球国界（非仅中国）
world = get_adm_maps(level="国", only_polygon=True)
japan = get_adm_maps(country="JPN", level="国", record="first")

# 名称列表（解析简称前）
names = get_adm_names(province="河南省", level="市")
```

**参数要点**：

- `level`：`'国'` `'省'` `'市'` `'区县'`（一次查询一个等级）
- `record='first'`：单条；`'all'`：含海岛等多条
- `only_polygon=True`：只要 `MapPolygon`
- `engine='geopandas'`：返回 GeoDataFrame
- `simplify=True`：简化几何以兼容 EPS/PS 导出
- `source`：仅用户明确要求时加（如 `source='世界银行'`）
- `provider`：数据包名，默认 `cnmaps-data`

### MapPolygon

```python
extent = polygon.get_extent(buffer=2)          # → ax.set_extent(extent, crs=...)
mask = polygon.make_mask_array(lons, lats)     # True = 界外
masked = polygon.maskout(lons, lats, data)     # numpy.ma.MaskedArray
polygon.to_file("./out.geojson")
beijing + hebei                                # 合并
```

`drop_inner_duplicate()`：合并后去内含重复多边形。

### 预设区域

```python
from cnmaps.regions import region_polygons
jjj = region_polygons["京津冀"]  # 东北、华北、长三角、川渝 等
```

### 绘制

```python
from cnmaps import draw_map, draw_maps

draw_maps(get_adm_maps(level="省"), ax=ax, linewidth=0.8, color="k")
draw_map(china, ax=ax, color="k")
```

### 裁剪（先画 artist，再 clip，再画边界）

| 函数 | 对象 |
|------|------|
| `clip_contours_by_map` | `contour` / `contourf` |
| `clip_pcolormesh_by_map` | `pcolormesh` |
| `clip_quiver_by_map` | `quiver` |
| `clip_scatter_by_map` | `scatter` |
| `clip_clabels_by_map` | `clabel` 返回值 |
| `clip_imshow_by_map` | `imshow`（hillshade） |
| `clip_streamplot_by_map` | `streamplot` |

```python
clip_contours_by_map(cs, china, ax=ax,
                     extent=[70, 140, 15, 55],  # 可选：与矩形范围求交
                     set_extent=False)
```

`map_polygon` 可为单个 `MapPolygon`、列表或 GeoDataFrame。

### 样例数据

```python
from cnmaps.sample import load_dem, load_temp, load_wind

lons, lats, dem = load_dem()
lons, lats, temp = load_temp()
lons, lats, u, v = load_wind()
```

### 自定义边界

```bash
cnmaps check-boundary ./my.geojson
cnmaps export ./out.geojson --province 河南省 --level 省
```

```python
from cnmaps import read_boundary_file
boundary = read_boundary_file("./my.geojson")
```

## 官方工作流摘要

1. **画行政界**：`get_adm_maps` → `draw_maps`
2. **选区域**：`record='first'` 或 `get_adm_names` 解析全称
3. **叠在已有图上**：传正确 `ax`，标注用 `transform=ccrs.PlateCarree()`
4. **栅格掩膜**：`make_mask_array` 或 `maskout`
5. **Artist 裁剪**：创建 artist → `clip_*` → `draw_map` 描边
6. **导出矢量**：`only_polygon=True` → `to_file`
7. **中心标注**：`MapRecord.longitude` / `latitude`

## 返回类型

| 参数组合 | 返回 |
|----------|------|
| `only_polygon=True` | `MapPolygon` 或 list |
| `only_polygon=False`, `engine=None` | `MapRecord`（含 geometry、经纬度元数据） |
| `engine='geopandas'` | `GeoDataFrame` |

标注、散点：保留 `MapRecord`（`only_polygon=False`）。纯几何运算：用 `only_polygon=True`。

## 常见误区（官方 common-pitfalls）

- `level='国'` ≠ 仅中国
- 勿默认加 `source='高德'` / `'世界银行'`
- 勿把边界对象当栅格数组
- 勿对已有 `longitude`/`latitude` 重算质心
