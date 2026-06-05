"""Verify smoke-test dependencies and minimum versions."""

from __future__ import annotations

import sys
from importlib.metadata import version


def _parse_ver(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in v.split(".")[:3]:
        digits = "".join(c for c in piece if c.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _require(pkg: str, min_ver: str | None = None) -> None:
    try:
        v = version(pkg)
    except Exception as exc:
        raise SystemExit(
            f"Missing package: {pkg}\n"
            f"  Run from skill dir: uv sync\n"
            f"  ({exc})"
        ) from exc
    if min_ver and _parse_ver(v) < _parse_ver(min_ver):
        raise SystemExit(f"{pkg} {v} < required {min_ver}")
    print(f"  {pkg} {v}")


def main() -> None:
    print(f"Python {sys.version.split()[0]} ({sys.executable})")
    for name in ("cartopy", "cnmaps", "matplotlib", "numpy", "frykit"):
        min_v = {"cnmaps": "2.1.0", "frykit": "0.7.0"}.get(name)
        _require(name, min_v)
    print("All dependencies OK.")


if __name__ == "__main__":
    main()
