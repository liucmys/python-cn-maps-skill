# python-cn-maps-skill

**Portable agent skill** for plotting scientific fields on China maps with **matplotlib**, **Cartopy**, **cnmaps**, and **frykit**.

Works with **Cursor**, **Claude Code**, **OpenAI Codex**, **GitHub Copilot**, **Gemini CLI**, **OpenCode**, **Windsurf** (via rules), and any agent that can read `SKILL.md`.

## Quick install

```bash
git clone https://github.com/liucmys/python-cn-maps-skill.git
cd python-cn-maps-skill
```

**Windows:** `.\scripts\install.ps1 -Target cursor -Scope project`  
**macOS/Linux:** `chmod +x scripts/install.sh && ./scripts/install.sh --target claude --scope project`

| Tool | Project path | Global path |
|------|----------------|-------------|
| Cursor | `.cursor/skills/python-cn-maps` | `~/.cursor/skills/python-cn-maps` |
| Claude Code | `.claude/skills/python-cn-maps` | `~/.claude/skills/python-cn-maps` |
| Codex | `.codex/skills/python-cn-maps` | `~/.codex/skills/python-cn-maps` |
| GitHub Copilot | `.github/skills/python-cn-maps` | — |
| Gemini / agents | `.gemini/skills/...` or `.agents/skills/...` | `~/.gemini/skills/...` |
| OpenCode | `skills/python-cn-maps` | — |

Full matrix and manual copy steps: **[docs/INSTALL.md](docs/INSTALL.md)**.

Install all common project paths at once:

```powershell
.\scripts\install.ps1 -Target all-project -Scope project
```

## Smoke tests

Requires [uv](https://docs.astral.sh/uv/):

```bash
uv sync
./scripts/run_smoke.ps1          # Windows
# ./scripts/install.sh not required for tests when run from repo root
```

See [TESTING.md](TESTING.md).

## Repository layout

| File | Purpose |
|------|---------|
| `SKILL.md` | Main instructions (tool-agnostic) |
| `AGENTS.md` | Entry point for Codex / OpenCode / generic agents |
| `docs/INSTALL.md` | Per-platform installation |
| `examples.md` | E1–E8 templates |
| `reference-*.md` / `troubleshooting.md` | Deep reference |
| `scripts/` | Smoke tests + `install.ps1` / `install.sh` |

## License

MIT — see [LICENSE](LICENSE).
