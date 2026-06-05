# 多平台安装指南

本仓库是**通用 Agent Skill**（标准 `SKILL.md` + 参考文档 + 脚本），不绑定单一 IDE。任选下列方式之一；内容相同，仅安装路径不同。

## 一键安装（推荐）

克隆后，在仓库根目录执行：

**Windows (PowerShell):**

```powershell
git clone https://github.com/liucmys/python-cn-maps-skill.git
cd python-cn-maps-skill
.\scripts\install.ps1 -Target cursor -Scope project   # 当前项目
.\scripts\install.ps1 -Target claude -Scope global    # 用户级 Claude Code
.\scripts\install.ps1 -Target all-project             # 写入本项目全部常见路径
```

**macOS / Linux:**

```bash
git clone https://github.com/liucmys/python-cn-maps-skill.git
cd python-cn-maps-skill
./scripts/install.sh --target cursor --scope project
./scripts/install.sh --target codex --scope global
```

| `-Target` | 安装目录（`Scope=project` 时相对当前项目根） |
|-----------|---------------------------------------------|
| `cursor` | `.cursor/skills/python-cn-maps` |
| `claude` | `.claude/skills/python-cn-maps` |
| `github` | `.github/skills/python-cn-maps` |
| `agents` | `.agents/skills/python-cn-maps` |
| `gemini` | `.gemini/skills/python-cn-maps` |
| `codex` | `.codex/skills/python-cn-maps`（`global` → `~/.codex/skills/...`） |
| `opencode` | `skills/python-cn-maps` |
| `all-project` | 以上所有**项目级**路径各一份 |

`Scope=global` 时写入用户主目录下对应路径（如 `~/.cursor/skills/python-cn-maps`）。

---

## 各平台说明

### Cursor

- **项目**：`.cursor/skills/python-cn-maps/`
- **全局**：`~/.cursor/skills/python-cn-maps/`（Windows：`%USERPROFILE%\.cursor\skills\python-cn-maps`）
- 自动发现 `SKILL.md`；对话中可手动附加 skill。

### Claude Code

- **项目**：`.claude/skills/python-cn-maps/`
- **全局**：`~/.claude/skills/python-cn-maps/`
- 与 [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) 目录约定一致；也可在 `CLAUDE.md` 中写：「绑中国地图时阅读并遵循 `python-cn-maps` skill」。

### OpenAI Codex CLI

- **用户级**：`~/.codex/skills/python-cn-maps/`（与 Cursor 全局 skill 布局类似）
- **项目级**：`.codex/skills/python-cn-maps/`（若你的 Codex 版本支持项目 skills）
- 或在项目 `AGENTS.md` / 说明里注明 skill 路径，任务涉及中国地图时 `@` 引用 `SKILL.md`。

### GitHub Copilot（VS Code / coding agent）

- **项目**：`.github/skills/python-cn-maps/` 或 `.claude/skills/python-cn-maps/`
- 见 [Creating agent skills for Copilot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills)。

### Gemini CLI

- **工作区**：`.gemini/skills/python-cn-maps/` 或 `.agents/skills/python-cn-maps/`
- 若支持：`gemini skills install https://github.com/liucmys/python-cn-maps-skill.git`（以你本机 Gemini CLI 版本文档为准）。

### OpenCode / 通用 `AGENTS.md`

- 将本仓库拷到 `skills/python-cn-maps/`，并在根目录 `AGENTS.md` 增加：

```markdown
## Skills
- **python-cn-maps**: 中国地图绑图（cnmaps/frykit）。触发：中国地图、contourf 裁剪、行政边界。完整流程见 `skills/python-cn-maps/SKILL.md`。
```

### Windsurf / 其他仅支持 Rules 的工具

无原生 `skills/` 时，将 `SKILL.md` 核心章节粘贴进 `.windsurfrules` 或项目 rules；或会话中粘贴 `SKILL.md` 链接/路径。

### 任意 Agent（最低兼容）

1. 克隆本仓库。
2. 在提示词中写：**「遵循附件/路径下的 `SKILL.md`（python-cn-maps）完成中国地图绑图。」**
3. 用 `@SKILL.md`、文件上传或 `Read` 工具加载全文。

---

## cnmaps 官方 skill（可选）

cnmaps 自带安装器（可能仅部分平台）：

```bash
cnmaps install-skill cursor --mode global --force
cnmaps install-skill codex --mode global --force   # 若你的 cnmaps 版本支持
```

本仓库在官方 cnmaps skill 基础上合并了 **frykit**、冒烟测试与多平台安装说明，二者可并存；以本仓库 `SKILL.md` 为完整工作流为准。

---

## 验证安装

进入**安装后的目录**（或本仓库根目录）：

```bash
uv sync
./scripts/run_smoke.ps1    # Windows
# 或 uv run python scripts/check_deps.py && ...
```

见 [TESTING.md](../TESTING.md)。
