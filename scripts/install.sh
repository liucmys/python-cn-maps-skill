#!/usr/bin/env bash
# Install python-cn-maps skill to agent-specific directories.
set -euo pipefail

TARGET="${1:-cursor}"
SCOPE="${2:-project}"
PROJECT_ROOT="${3:-$(pwd)}"
SKILL_NAME="python-cn-maps"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

declare -A REL_PATHS=(
  [cursor]=".cursor/skills/${SKILL_NAME}"
  [claude]=".claude/skills/${SKILL_NAME}"
  [github]=".github/skills/${SKILL_NAME}"
  [agents]=".agents/skills/${SKILL_NAME}"
  [gemini]=".gemini/skills/${SKILL_NAME}"
  [codex]=".codex/skills/${SKILL_NAME}"
  [opencode]="skills/${SKILL_NAME}"
)

exclude=(.git .venv __pycache__ artifacts)

dest_root() {
  local rel="$1"
  if [[ "$SCOPE" == "global" ]]; then
    case "$rel" in
      .cursor/*) echo "${HOME}/.cursor/skills/${SKILL_NAME}" ;;
      .claude/*) echo "${HOME}/.claude/skills/${SKILL_NAME}" ;;
      .codex/*)  echo "${HOME}/.codex/skills/${SKILL_NAME}" ;;
      .gemini/*) echo "${HOME}/.gemini/skills/${SKILL_NAME}" ;;
      .agents/*) echo "${HOME}/.agents/skills/${SKILL_NAME}" ;;
      *) echo "Global scope not defined for: $rel" >&2; exit 1 ;;
    esac
  else
    echo "${PROJECT_ROOT}/${rel}"
  fi
}

install_to() {
  local dest="$1"
  rm -rf "$dest"
  mkdir -p "$dest"
  shopt -s dotglob
  for item in "$REPO_ROOT"/*; do
    base="$(basename "$item")"
    skip=0
    for ex in "${exclude[@]}"; do [[ "$base" == "$ex" ]] && skip=1 && break; done
    [[ $skip -eq 1 ]] && continue
    cp -a "$item" "$dest/"
  done
  mkdir -p "$dest/artifacts"
  touch "$dest/artifacts/.gitkeep"
  echo "Installed -> $dest"
}

run_target() {
  local t="$1"
  local rel="${REL_PATHS[$t]:-}"
  [[ -z "$rel" ]] && echo "Unknown target: $t" >&2 && exit 1
  install_to "$(dest_root "$rel")"
}

usage() {
  echo "Usage: $0 --target <cursor|claude|github|agents|gemini|codex|opencode|all-project> [--scope project|global] [--project-root PATH]"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --scope) SCOPE="$2"; shift 2 ;;
    --project-root) PROJECT_ROOT="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) TARGET="$1"; shift ;;
  esac
done

if [[ "$TARGET" == "all-project" ]]; then
  for t in cursor claude github agents gemini codex opencode; do
    run_target "$t"
  done
else
  run_target "$TARGET"
fi

echo "Done. target=$TARGET scope=$SCOPE"
