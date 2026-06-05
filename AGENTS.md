# Agent instructions (OpenCode / Codex / generic)

This repository is a **portable skill** for China map plotting. It is not limited to Cursor.

## Skill: python-cn-maps

**When to use:** User asks for China maps, `contourf`/`pcolormesh`/`quiver` on GeoAxes, administrative boundaries, clipping/masking, South China Sea inset, cnmaps, frykit, or Cartopy China workflows.

**What to do:**

1. Read and follow [`SKILL.md`](SKILL.md) end-to-end for the workflow.
2. Load on demand: [`examples.md`](examples.md), [`reference-cnmaps.md`](reference-cnmaps.md), [`reference-frykit.md`](reference-frykit.md), [`troubleshooting.md`](troubleshooting.md).
3. After changing plotting logic, run smoke tests per [`TESTING.md`](TESTING.md).

**Install paths for other tools:** see [`docs/INSTALL.md`](docs/INSTALL.md).
