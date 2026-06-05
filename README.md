# python-cn-maps-skill

Cursor Agent Skill for plotting scientific fields on China maps with **matplotlib**, **Cartopy**, **cnmaps**, and **frykit**.

## Install

### Project skill (recommended)

```bash
git clone https://github.com/liucmys/python-cn-maps-skill.git
mkdir -p .cursor/skills/python-cn-maps
cp -r python-cn-maps-skill/* .cursor/skills/python-cn-maps/
```

Windows PowerShell:

```powershell
git clone https://github.com/liucmys/python-cn-maps-skill.git
New-Item -ItemType Directory -Force -Path .cursor\skills\python-cn-maps
Copy-Item -Recurse python-cn-maps-skill\* .cursor\skills\python-cn-maps\
```

### Global skill

```bash
git clone https://github.com/liucmys/python-cn-maps-skill.git ~/.cursor/skills/python-cn-maps
```

## Smoke tests

Requires [uv](https://docs.astral.sh/uv/):

```bash
cd .cursor/skills/python-cn-maps   # or cloned repo root
uv sync
./scripts/run_smoke.ps1            # Windows
# or: uv run python scripts/check_deps.py && ...
```

See [TESTING.md](TESTING.md).

## Contents

| File | Purpose |
|------|---------|
| `SKILL.md` | Main agent instructions |
| `examples.md` | E1–E8 copy-paste templates |
| `reference-cnmaps.md` / `reference-frykit.md` | API quick reference |
| `troubleshooting.md` | Common fixes |
| `scripts/` | `uv` smoke tests |

## License

MIT (see repository license file if present).
