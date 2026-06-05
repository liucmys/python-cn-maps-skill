# python-cn-maps 冒烟测试

Skill 目录内用 [uv](https://docs.astral.sh/uv/) 管理独立 `.venv`，与项目其余代码隔离。

## 前置

- 已安装 **uv**（本机曾测 0.8.x）
- Windows x64、Python **3.12**（`uv` 会自动下载）

## 一键运行

```powershell
cd path\to\python-cn-maps   # repo root or .cursor/skills/python-cn-maps
.\scripts\run_smoke.ps1
```

## 分步

```powershell
cd .cursor\skills\python-cn-maps
uv sync
$env:MPLBACKEND = "Agg"
uv run python scripts/check_deps.py
uv run python scripts/smoke_e1_cnmaps.py
uv run python scripts/smoke_e3_frykit.py
```

## 成功标准

- `uv sync` 无错误
- `check_deps.py` 退出码 0
- `artifacts/e1_smoke.png`、`artifacts/e3_smoke.png` 各 > 10KB

## 依赖（pyproject.toml）

| 包 | 约束 |
|----|------|
| cartopy | >=0.22 |
| cnmaps | >=2.1 |
| matplotlib, numpy | — |
| frykit[data] | >=0.7 |

## Windows / cartopy 排错

1. 确认 **64 位** Python 3.12：`uv run python -c "import struct; print(struct.calcsize('P')*8)"`
2. 升级 uv 后重试：`uv sync --reinstall-package cartopy`
3. 若 `cartopy` 仍无法安装（缺 wheel）：在 conda 中 `conda install -c conda-forge cartopy`，再于本目录 `uv pip install -e .` 仅装其余依赖（高级，一般不推荐混用）

## 修改 skill 后

改 `SKILL.md` 或示例后，在 skill 目录重新跑 `.\scripts\run_smoke.ps1` 确认绑图链路仍通。
