# Prompt 验收（Phase 4）

附加本 skill 后，agent 输出应满足：

## Prompt 1：全国气温填色 + 国界裁剪

**用户：** 用 cnmaps 画全国气温填色，国界裁剪，输出 `out.png`

**必须出现：**

- `transform=data_crs`（或 `transform=ccrs.PlateCarree()`）
- `get_adm_maps(country="中国", level="国", ...)`
- `clip_contours_by_map(..., ax=ax)`

**参考：** `SKILL.md` Quick start；`scripts/smoke_e1_cnmaps.py`；examples E1

## Prompt 2：河南省南阳市区域高亮

**用户：** 河南省南阳市区域高亮

**必须出现：**

- 全称 `河南省`、`南阳市`（非 `河南`、`南阳`）
- `get_adm_maps(province="河南省", ...)` 与 `city="南阳市"` 或等价 level 筛选

**参考：** examples E2

## 自检（2026-06-05）

| 检查项 | 位置 |
|--------|------|
| `country="中国", level="国"` | SKILL.md Quick start；smoke_e1 |
| `transform=data_crs` | SKILL.md Workflow；smoke_e1 |
| `clip_contours_by_map(..., ax=ax)` | SKILL.md；smoke_e1 |
| `河南省` / `南阳市` | examples E2；SKILL Common Rationalizations |
