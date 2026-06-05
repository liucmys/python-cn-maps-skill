# frykit 参考

基于 [frykit README](https://github.com/ZhaJiMan/frykit) 与 [官方示例](https://github.com/ZhaJiMan/frykit/tree/main/example)。

## 安装

```bash
pip install "frykit[data]"    # 0.7+ 数据与本体分离
# Python >= 3.10, cartopy >= 0.22, shapely >= 2
```

## 配置

```python
import frykit

# 推荐日常：天地图（更快、无飞地）
frykit.config.data_source = "tianditu"

# 临时切换
with frykit.config.context(data_source="amap"):
    cities = fshp.get_cn_city()

# 投影变换质量
frykit.config.fast_transform = False  # 慢但更准
```

| 数据源 | 特点 |
|--------|------|
| `amap`（默认） | 更精细；有飞地 |
| `tianditu` | 更快；含台湾区县；审图号语境 |

## 模块

```python
import frykit.shp as fshp   # 读几何、掩膜
import frykit.plot as fplt  # 画、裁、装饰
```

### 投影常量

`fplt.PLATE_CARREE`、`fplt.CN_AZIMUTHAL_EQUIDISTANT`、`fplt.WEB_MERCATOR`（均为 `ccrs` 实例）

## shp：读取几何

| 函数 | 说明 |
|------|------|
| `get_cn_border()` | 国界 |
| `get_cn_line()` | 九段线等 |
| `get_cn_province(name?)` | 省 |
| `get_cn_city(name?, province=?)` | 市 |
| `get_cn_district(name?, city=?, province=?)` | 县 |

支持名称、`adcode`（区县重名时用 adcode）、列表批量。

```python
import frykit.shp as fshp

border = fshp.get_cn_border()
fshp.get_cn_province(["安徽省", "江苏省"])
fshp.get_cn_city(province="安徽省")
fshp.get_cn_district(110105)  # 朝阳区 adcode
```

`get_cn_*_properties`：仅元数据 dict。安装 geopandas 后有 `get_cn_*_geodataframe`。

### 掩膜（数据处理阶段）

```python
mask = fshp.polygon_mask(border, lon2d, lat2d)
data[~mask] = np.nan

# 规则网格优化
mask = fshp.polygon_mask2(border, lon1d, lat1d)
```

与 **clip** 区别：mask 改数组；clip 改显示。

## plot：绘制

| 函数 | 说明 |
|------|------|
| `add_cn_border` | 国界 |
| `add_cn_line` | 九段线 |
| `add_cn_province/city/district` | 各级界 |
| `label_cn_province/city/district` | 标注 |
| `add_countries` / `add_land` / `add_ocean` | 粗糙世界底图 |
| `add_geometries(ax, geoms, ...)` | 任意 Shapely 几何 |

风格：`fplt.add_xxx(ax, **kwargs)`，首参恒为 `ax`。

**普通 Axes**：`ax.set_aspect(1)` + `set_map_ticks` + `add_cn_*`（无需 Cartopy GeoAxes）。

## plot：裁剪

| 函数 | 说明 |
|------|------|
| `clip_by_cn_border(artist)` | 国界（防 GeoAxes 出界） |
| `clip_by_cn_province/city/district` | 按行政区 |
| `clip_by_polygon(artist, polygon)` | 任意多边形 |

```python
cf = ax.contourf(..., transform=fplt.PLATE_CARREE, transform_first=True)
fplt.clip_by_cn_border(cf)
```

非 PlateCarree 投影时优先 frykit clip，而非手写 `set_clip_path`。

## plot：地图范围与装饰

```python
fplt.set_map_ticks(ax, (70, 140, 0, 60), dx=10, dy=10)
# 或显式 xticks=..., yticks=...

mini_ax = fplt.add_mini_axes(ax)           # 南海小图，自动角落定位
mini_ax.set_extent((105, 122, 2, 25), crs=fplt.PLATE_CARREE)

fplt.add_compass(ax, 0.95, 0.8, size=15)
scale_bar = fplt.add_scale_bar(ax, 0.36, 0.8, length=1000)

fplt.add_quiver_legend(Q, U=10, width=0.15, height=0.12)
fplt.add_frame(ax)   # GMT 风格边框；仅 PlateCarree / Mercator

fplt.savefig("out.png")  # 封装保存
```

## plot：色标辅助

```python
cmap, norm, ticks = fplt.make_qualitative_palette(["red", "orange", "yellow"])
norm = fplt.CenteredBoundaryNorm([-10, -5, 0, 5, 10])
cbar = fplt.plot_colormap(cmap, norm)
```

## 测试数据

```python
data = fplt.load_test_data()  # lon, lat, t2m, u10, v10 等
```

## 与 cnmaps 协作

| 任务 | 建议 |
|------|------|
| 复杂边界查询、全球国界、maskout | cnmaps |
| 快速中国界、南海小图、防出界 clip | frykit |
| 合并多省界做 clip | cnmaps `get_adm_maps` + frykit `clip_by_polygon` |

frykit 作者推荐综合任务用 [cnmaps](https://github.com/cnmetlab/cnmaps)；本 Skill 二者并用。

## 性能提示

- 用 `add_cn_*` 代替 `ax.add_geometries(fshp.get_cn_city(), ...)`
- 南方小范围地图时 frykit 优势更明显（Cartopy 仍投影范围外几何）
- 市/县级全国图优先 `tianditu` 数据
