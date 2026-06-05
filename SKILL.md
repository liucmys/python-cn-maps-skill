---
name: python-cn-maps
description: Portable agent skill (Cursor, Claude Code, Codex, Copilot, Gemini, OpenCode). Guides 2D fields on China maps with matplotlib, Cartopy, cnmaps, frykit—contourf, pcolormesh, quiver, clip, mask, South China Sea inset. Use when drawing China maps, meteorological/geographic plots, admin boundaries, or cartopy/cnmaps/frykit workflows. 中国地图绑图、裁剪、掩膜、南海小图时使用。
---

# Python 中国地图绑图

## Overview

在 **Cartopy GeoAxes** 上叠加经纬度（及可选高度）科学变量；边界与裁剪优先 **cnmaps**（查询/掩膜/`clip_*_by_map`）与 **frykit**（快速画界、南海小图、防出界 clip、装饰）。整合 [cnmaps 官方 skill](https://github.com/cnmetlab/cnmaps/tree/main/cnmaps/_bundled_skills/shared/cnmaps-python-assistant)；API 以 [cnmaps 文档](https://cnmaps.readthedocs.io/zh-cn/latest/content/api-ref.html) 为准。

本文件为**通用 Agent Skill**（标准 `SKILL.md`），不限于 Cursor。安装路径见 [docs/INSTALL.md](docs/INSTALL.md)（`.cursor/skills`、`.claude/skills`、`~/.codex/skills`、`.github/skills` 等）。OpenCode/Codex 项目可读根目录 [AGENTS.md](AGENTS.md)。

## When to Use

- 中国或省级/市级区域上的 `contourf` / `pcolormesh` / `quiver` / `scatter`
- 行政边界绘制、绘后白化裁剪、绘前掩膜、南海小图/九段线/指北针
- 选择 cnmaps vs frykit、或两库组合（cnmaps 取 `MapPolygon`，frykit 画界）

**不适用：**

- 仅需全球图且不需中国专用边界数据
- 在 `GeoAxes` 上叠加 `Axes3D` / `plot_surface`（不兼容；地图与 3D 分图）

## Workflow（2D 标量场）

```
- [ ] 1. 准备 lon/lat（1D 或 2D）与 data (ny, nx)
- [ ] 2. 建 GeoAxes + projection；set_extent(..., crs=data_crs)
- [ ] 3. 画变量层（必须 transform=data_crs）
- [ ] 4. 画边界（draw_maps / add_cn_*）
- [ ] 5. 裁剪或掩膜（见下）
- [ ] 6. 装饰（colorbar、南海小图、指北针等）
- [ ] 7. savefig(dpi=300, bbox_inches='tight')
```

**`transform`**：所有 `contourf`/`pcolormesh`/`quiver`/`scatter` 须 `transform=ccrs.PlateCarree()`（或数据真实 CRS）；边界用 `draw_maps` 或 `add_geometries(..., crs=data_crs)`。

| 方式 | 做法 |
|------|------|
| 绘前掩膜 | `polygon.maskout(lon, lat, data)` 或 `fshp.polygon_mask` → 再画 |
| 绘后裁剪 | 先画，再 `clip_contours_by_map(cs, polygon, ax=ax)` 或 `fplt.clip_by_cn_border(cf)` |
| 组合 | 先 `maskout` 再 `clip` 边界更干净 |

## Tool choice

| 需求 | 优先 |
|------|------|
| 查边界、合并区域、掩膜、`clip_*_by_map` 全系列 | **cnmaps** |
| 快速省/市/县界、九段线、南海小图、指北针、比例尺 | **frykit** |
| 非 PlateCarree 投影 clip 不出界 | **frykit** `clip_by_cn_border` |
| 全球国界 + 中国高亮 | **cnmaps** `level='国'` + `country='中国'` |
| 普通 `Axes` 经纬度图（无 Cartopy） | **frykit** `set_map_ticks` + `add_cn_*` |

详情：[reference-cnmaps.md](reference-cnmaps.md) · [reference-frykit.md](reference-frykit.md)

## 依赖

| 包 | 要求 |
|----|------|
| Python | ≥3.10（frykit）；推荐 3.12 |
| cartopy | ≥0.22 |
| cnmaps | ≥2.1（含 cnmaps-data） |
| frykit | ≥0.7，`pip install "frykit[data]"` |
| matplotlib, numpy | — |

冒烟测试见 [TESTING.md](TESTING.md)（`uv sync` + `scripts/run_smoke.ps1`）。多平台安装：`scripts/install.ps1` / `scripts/install.sh`，详见 [docs/INSTALL.md](docs/INSTALL.md)。

## Quick start（cnmaps）

```python
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cnmaps import clip_contours_by_map, draw_map, get_adm_maps
from cnmaps.sample import load_temp

data_crs = ccrs.PlateCarree()
lons, lats, data = load_temp()
china = get_adm_maps(country="中国", level="国", record="first", only_polygon=True)

fig, ax = plt.subplots(subplot_kw={"projection": data_crs}, figsize=(8, 6))
cs = ax.contourf(lons, lats, data, transform=data_crs)
clip_contours_by_map(cs, china, ax=ax)
draw_map(china, ax=ax, color="k", linewidth=1.0)
ax.set_extent(china.get_extent(buffer=1), crs=data_crs)
plt.savefig("out.png", dpi=300, bbox_inches="tight")
```

**frykit + 装饰**：见 [examples.md](examples.md) **E3**（风场+裁剪）、**E4**（南海小图）。

## cnmaps 要点

- `get_adm_maps(province=..., city=..., level='国'|'省'|'市'|'区县', country='中国', record='first', only_polygon=True)`
- 名称**全称**：`河北省` 非 `河北`；仅中国国界：`country='中国', level='国'`（`level='国'`  alone = 全球）
- 合并：`beijing + tianjin`；预设：`region_polygons['京津冀']`
- clip：`clip_contours_by_map`, `clip_pcolormesh_by_map`, `clip_quiver_by_map`, …；多子图每个 artist 传 `ax=axs[i,j]`

## frykit 要点

- `pip install "frykit[data]"`；可选 `frykit.config.data_source = 'tianditu'`
- `add_cn_border/province/city`, `add_cn_line`, `clip_by_cn_border/polygon`
- 装饰：`add_mini_axes`, `add_compass`, `add_scale_bar`；色标：`CenteredBoundaryNorm`

## 2D 叠加模式

| 模式 | 要点 | 完整示例 |
|------|------|----------|
| contourf | `transform=data_crs` → cnmaps `clip_contours_by_map` 或 frykit `clip_by_cn_border` | E1 |
| pcolormesh | `clip_pcolormesh_by_map(mesh, boundary, ax=ax)` | examples |
| quiver+场 | 场与矢量分别 clip；`add_quiver_legend` 可选 | E3 |
| contour+clabel | 先 clip contour，再 `clip_clabels_by_map` | reference-cnmaps |
| imshow/hillshade | `clip_imshow_by_map` | examples |

## 经纬度 + 高度（2.5D）

**禁止** GeoAxes + Axes3D 同轴。

| 模式 | 做法 |
|------|------|
| 地形+场 | `contourf` 场 + `contour` 地形；统一 clip |
| 多层高度 | 多子图，每层独立 `ax=` clip |
| 垂直剖面 | GeoAxes + 普通 `Axes` 子图 |
| 真 3D | `plot_surface` 单独子图 |

## 色标

离散 `BoundaryNorm`；过零 `frykit.plot.CenteredBoundaryNorm`；对数 `LogNorm`；科研色标可选 [`cmaps`](https://github.com/liaochongjun/cmaps)。

## Common Rationalizations

| 借口 | 事实 |
|------|------|
| 省略 `transform` 也能出图 | 条带/错位/不在陆上；必须 `transform=data_crs` |
| `河北` 简称即可 | cnmaps 须全称 `河北省`；用 `get_adm_names` 核对 |
| `level='国'` = 中国 | 为全球国界；仅中国加 `country='中国'` |
| 多子图 clip 一次就够 | 须每个 artist `ax=axs[i,j]`，否则仅最后一幅有填色 |
| Natural Earth 中国边界够用 | 政治边界不准确；用 cnmaps/frykit 数据 |

## Red Flags

- 地理 artist 无 `transform`
- `clip_*` 未传 `ax=`（多子图）
- `GeoAxes` 上叠 `Axes3D`
- 省市区名称非全称
- 手写 `set_clip_path` 导致填色溢出（优先 `clip_by_cn_border`）

## Verification

改 skill 或绑图逻辑后，在 skill 目录：

- [ ] `uv sync` 成功
- [ ] `.\scripts\run_smoke.ps1` 或等价 `uv run` check + e1 + e3 通过
- [ ] `artifacts/e1_smoke.png`、`e3_smoke.png` 存在且 > 10KB
- [ ] 用户脚本含 `transform=data_crs`；中国国界含 `country="中国", level="国"`
- [ ] 多子图每个 clip 显式 `ax=`

## Agent 行为准则

1. 先判断：查边界 / 画图 / 掩膜 / clip / 标注 / 装饰。
2. 输出**可运行**完整脚本（含 `projection`、`transform`、`ax`）。
3. 不臆造 API；不确定时读 reference / examples。
4. cnmaps 非纯 CLI；`export`/`check-boundary` 仅导出/校验边界。
5. 中国国界示例写 `country="中国", level="国"`。
6. 多库：cnmaps 取 `MapPolygon`，frykit 画界与防出界 clip。
7. 修改本 skill 后运行 [TESTING.md](TESTING.md) 冒烟。

## 延伸阅读

- [examples.md](examples.md) — E1–E8
- [troubleshooting.md](troubleshooting.md) — 出界、多子图、性能
- [TESTING.md](TESTING.md) — uv 冒烟
- [docs/INSTALL.md](docs/INSTALL.md) — Cursor / Claude / Codex / Copilot / Gemini 等安装
- [AGENTS.md](AGENTS.md) — Codex、OpenCode 入口
- 外部：[cnmaps 指南](https://cnmaps.readthedocs.io/zh-cn/latest/index.html) · [frykit](https://github.com/ZhaJiMan/frykit)
