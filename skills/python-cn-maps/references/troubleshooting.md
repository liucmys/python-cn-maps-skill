# 排错与性能

## 数据错位 / 条带 / 不在陆上

**原因**：未传 `transform=ccrs.PlateCarree()`（或数据真实 CRS）。

**修复**：所有地理数据绘制统一 `transform=data_crs`；`set_extent` 的 `crs` 与数据一致。

## 多子图 clip 后仅最后一幅有填色

**原因**：`clip_contours_by_map` 未绑定目标轴（[cnmaps#138](https://github.com/cnmetlab/cnmaps/issues/138)）。

**修复**：

```python
clip_contours_by_map(cfl[i], boundary, ax=axs[row, col])
```

循环中每个 artist 显式传 `ax=`。官方多面板示例用 `extent=` + `set_extent=True` 时亦建议显式 `ax=`。

## clip 后填色溢出地图外框

**原因**：在 `GeoAxes` 上二次 `set_clip_path` 破坏 `GeoAxes.patch` 裁剪（[博客说明](https://zhajiman.github.io/post/cartopy_clip_outside/)）。

**修复**：

- 优先 `fplt.clip_by_cn_border(artist)`（国界 ∩ 地图边界）
- 或 `col.set_clip_box(ax.bbox)`（仅矩形地图边界）
- 勿对手写 clip 省略与地图边界的求交

## 查询不到行政区

- 名称须**全称**：`北京市`、`内蒙古自治区`
- `level` 与筛选一致：查市用 `level='市'` 或传 `city=`
- 用 `get_adm_names(...)` 核对可用名称
- frykit 重名区县用 `adcode`

## `level='国'` 画出全球或不对

`level='国'` 为所有国家；仅中国须 `country='中国'`。

## 海岛/国界多条记录

`record='all'` 返回多条；单国裁剪用 `record='first', only_polygon=True`。

## EPS/PS 导出后文件损坏

```python
china = get_adm_maps(..., simplify=True, only_polygon=True)
```

## frykit 省界扭曲 / 锯齿

```python
fplt.add_cn_province(ax, fast_transform=False)
# 或 frykit.config.fast_transform = False
```

## frykit 画图慢

- `frykit.config.data_source = 'tianditu'`
- 用 `add_cn_province` 代替 `add_geometries`
- 缩小 `set_extent` 范围（Cartopy 0.23+ 仍投影范围外几何）

## 南海/九段线缺失

- cnmaps：确保国界 `country='中国'`
- frykit：主图与小图均 `fplt.add_cn_line(ax)`

## Cartopy 中国边界政治不正确

勿用 `cartopy.feature` 的 Natural Earth 中国边界；用 cnmaps / frykit 数据。

## shapefile 乱码

`.dbf` 常为 GBK：`shapereader.Reader(path, encoding='gbk')`。

## 环境

- frykit 需 Python 3.10+；与 cnmaps 3.9+ 同环境时注意版本
- 无数据：`pip install cnmaps`、`pip install "frykit[data]"`

## 调试检查清单

1. `ax.name` 是否为 `geoaxes`（若用 Cartopy）
2. `cs.transform` / artist 是否带投影
3. `boundary` 是否为 `MapPolygon` 且与范围相交
4. 多子图是否每个 `ax=` 独立 clip
5. colorbar 是否绑定正确的 mappable
