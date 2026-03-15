#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_INDEX_TEMPLATE = """# Project Documents Index (Auto-generated for Codex)

This file lists the locations of key project definition and rule documents. The Codex system should discover and read the files within these directories for context.

---

### Core Guideline
- **Path:** `{core_guideline}`

### Project Rules
- **Path:** All `.md` files within `./.claude/rules/`

### Interview Documents (Requirements)
- **Path:** All `.md` files within `./docs/interview/`

### Plan Documents (Implementation Plans)
- **Path:** All `.md` files within `./docs/plan/`
"""


def is_wsl() -> bool:
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False


def is_wsl_windows_mount(path: Path) -> bool:
    """Checks if a path is on a Windows drive mounted inside WSL (e.g., /mnt/c)."""
    if not is_wsl():
        return False
    resolved = str(path.resolve())
    # Standard WSL mount point is /mnt/<drive-letter>/...
    return (
        resolved.startswith("/mnt/")
        and len(resolved) >= 7
        and resolved[5].isalpha()
        and resolved[6] == "/"
    )


def find_powershell_exe() -> str | None:
    ps = shutil.which("powershell.exe")
    if ps:
        return ps
    wsl_ps = Path("/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
    if wsl_ps.exists():
        return str(wsl_ps)
    return None


def to_windows_path(path: Path, *, resolve: bool) -> str:
    """Converts a POSIX path (potentially from WSL) to its Windows equivalent."""
    concrete = path.resolve() if resolve else path.absolute()
    if os.name == "nt":
        return str(concrete)

    # Handle WSL /mnt/c/... paths manually for speed
    raw = str(concrete)
    if (
        raw.startswith("/mnt/")
        and len(raw) >= 7
        and raw[5].isalpha()
        and raw[6] == "/"
    ):
        drive = raw[5].upper()
        tail = raw[7:].replace("/", "\\")
        return f"{drive}:\\{tail}"

    # Fallback to wslpath for other cases
    output = subprocess.check_output(
        ["wslpath", "-w", raw],
        text=True,
        stderr=subprocess.STDOUT,
    )
    return output.strip()


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def recreate_posix_symlink(link: Path, target: Path) -> None:
    remove_path(link)
    rel_target = os.path.relpath(target.resolve(), start=link.parent.resolve())
    link.symlink_to(rel_target, target_is_directory=True)
    print(f"    -> Symlink created: {link}")


def recreate_windows_junction(powershell_exe: str, link: Path, target: Path) -> None:
    link_win = to_windows_path(link, resolve=False)
    target_win = to_windows_path(target, resolve=True)
    link_ps = link_win.replace("'", "''")
    target_ps = target_win.replace("'", "''")

    if link.is_symlink() or link.is_file():
        link.unlink()

    script = (
        "$ErrorActionPreference='Stop'; "
        f"$link='{link_ps}'; "
        f"$target='{target_ps}'; "
        "if (Test-Path -LiteralPath $link) { "
        "  Remove-Item -LiteralPath $link -Recurse -Force "
        "}; "
        "New-Item -ItemType Junction -Path $link -Target $target | Out-Null"
    )
    create = subprocess.run(
        [
            powershell_exe,
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if create.returncode != 0:
        details = (create.stdout + "\n" + create.stderr).strip()
        raise RuntimeError(f"Failed to create junction {link_win} -> {target_win}. {details}")
    print(f"    -> Junction created: {link_win}")


def validate_link_targets(codex_dir: Path, pairs: tuple[tuple[Path, Path], ...]) -> None:
    allowed = {
        (codex_dir / "agents").absolute(),
        (codex_dir / "skills").absolute(),
        (codex_dir / "rules").absolute(),
    }
    for link, _ in pairs:
        concrete_link = link.absolute()
        if concrete_link not in allowed:
            raise RuntimeError(f"Refusing to modify unexpected path: {concrete_link}")


def generate_agents_md(repo_root: Path) -> None:
    core_guideline = "./CLAUDE.md"
    if not (repo_root / "CLAUDE.md").exists() and (repo_root / "CLA.md").exists():
        core_guideline = "./CLA.md"
    content = PROJECT_INDEX_TEMPLATE.format(core_guideline=core_guideline)
    (repo_root / "AGENTS.md").write_text(content, encoding="utf-8")
    print("    -> AGENTS.md generated.")


def main() -> int:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[4]
    os.chdir(repo_root)

    claude_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".claude")
    codex_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".codex")
    claude_dir = (repo_root / claude_dir).resolve()
    codex_dir = (repo_root / codex_dir).resolve()

    print("--- Starting Codex Sync Process ---")
    # --- Phase 1: Setup and Validation ---
    print(f"[1/4] Ensuring required {claude_dir.relative_to(repo_root)} directories exist...")
    (claude_dir / "agents").mkdir(parents=True, exist_ok=True)
    (claude_dir / "skills").mkdir(parents=True, exist_ok=True)
    (claude_dir / "rules").mkdir(parents=True, exist_ok=True)
    print("    -> Ensured '.claude/agents', '.claude/skills', and '.claude/rules'.")

    print(f"[2/4] Ensuring {codex_dir.relative_to(repo_root)} directory exists...")
    codex_dir.mkdir(parents=True, exist_ok=True)
    print("    -> .codex is ready.")

    pairs = (
        (codex_dir / "agents", claude_dir / "agents"),
        (codex_dir / "skills", claude_dir / "skills"),
        (codex_dir / "rules", claude_dir / "rules"),
    )
    validate_link_targets(codex_dir, pairs)

    # --- Phase 2: Link Creation ---
    print("[3/4] Rebuilding agents/skills link targets...")
    # Use Windows Junctions if running on Windows or on a Windows mount in WSL.
    # Junctions are more robust than symlinks in these environments.
    use_windows_junction = os.name == "nt" or is_wsl_windows_mount(repo_root)
    powershell_exe = find_powershell_exe() if use_windows_junction else None
    if use_windows_junction and not powershell_exe:
        raise RuntimeError("Windows link mode selected, but powershell.exe was not found.")

    for link, target in pairs:
        if use_windows_junction and powershell_exe:
            recreate_windows_junction(powershell_exe, link, target)
        else:
            recreate_posix_symlink(link, target)

    # --- Phase 3: Index Generation ---
    print("[4/4] Generating AGENTS.md as a high-level index...")
    generate_agents_md(repo_root)
    print("--- Codex Sync Process Finished Successfully ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
