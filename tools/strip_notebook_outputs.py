import json
import subprocess
from pathlib import Path


def staged_notebooks() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        check=True,
        capture_output=True,
        text=True,
    )
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [Path(f) for f in files if f.lower().endswith(".ipynb") and Path(f).exists()]


def strip_outputs(nb_path: Path) -> bool:
    raw = nb_path.read_text(encoding="utf-8")
    nb = json.loads(raw)
    changed = False

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        outputs = cell.get("outputs", [])
        if outputs:
            cell["outputs"] = []
            changed = True

        if cell.get("execution_count") is not None:
            cell["execution_count"] = None
            changed = True

    if changed:
        nb_path.write_text(
            json.dumps(nb, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )

    return changed


def main() -> int:
    notebooks = staged_notebooks()
    if not notebooks:
        return 0

    changed_files = []
    for nb_path in notebooks:
        if strip_outputs(nb_path):
            changed_files.append(str(nb_path))

    if changed_files:
        subprocess.run(["git", "add", "--", *changed_files], check=True)
        print("Stripped outputs:", ", ".join(changed_files))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
