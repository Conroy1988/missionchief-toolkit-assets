#!/usr/bin/env python3
"""Compare production shadows with production main while validating candidate policy code."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github" / "scripts" / "verify_shadow_branch_parity.py"
WORKFLOW = ROOT / ".github" / "workflows" / "verify-shadow-branch-parity.yml"
TEST = ROOT / ".github" / "scripts" / "test_shadow_branch_parity.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0 and new in text:
        return text
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    script = SCRIPT.read_text(encoding="utf-8")
    script = replace_once(
        script,
        "Mirrored paths must remain byte-identical to the current checkout. Operational\npaths may differ, but must satisfy their reviewed schemas and cross-file\nconsistency rules.",
        "Mirrored paths must remain byte-identical to the selected production authority ref.\nOperational paths may differ, but must satisfy their reviewed schemas and cross-file\nconsistency rules.",
        "verifier description",
    )
    script = replace_once(
        script,
        "def compare_branch(branch: str, policy: dict) -> dict:\n",
        "def compare_branch(branch: str, policy: dict, mirror_source: str) -> dict:\n",
        "compare signature",
    )
    script = replace_once(
        script,
        "        local_path = ROOT / path\n        try:\n            remote = branch_file(branch, path)\n",
        "        local_path = ROOT / path\n        try:\n            remote = branch_file(branch, path)\n",
        "remote read anchor",
    )
    old_local = "        local = local_path.read_bytes() if local_path.is_file() else None\n        equal = local == remote if local is not None else False\n\n        if path in mirrored:\n"
    new_local = "        if path in mirrored:\n            try:\n                local = git(\"show\", f\"{mirror_source}:{path}\", binary=True)\n            except subprocess.CalledProcessError:\n                local = None\n        else:\n            local = local_path.read_bytes() if local_path.is_file() else None\n        equal = local == remote if local is not None else False\n\n        if path in mirrored:\n"
    script = replace_once(script, old_local, new_local, "mirror source read")
    script = replace_once(
        script,
        "    parser.add_argument(\"--self-test\", action=\"store_true\")\n",
        "    parser.add_argument(\"--self-test\", action=\"store_true\")\n    parser.add_argument(\"--mirror-source\", default=\"HEAD\")\n",
        "mirror source argument",
    )
    script = replace_once(
        script,
        "        compare_branch(branch, branch_policy)\n",
        "        compare_branch(branch, branch_policy, args.mirror_source)\n",
        "compare invocation",
    )
    script = replace_once(
        script,
        '        "sourceCommit": str(git("rev-parse", "HEAD")).strip(),\n',
        '        "sourceCommit": str(git("rev-parse", "HEAD")).strip(),\n        "mirrorSource": args.mirror_source,\n',
        "report source",
    )
    script = replace_once(
        script,
        '        f"- Source commit: `{report[\'sourceCommit\']}`",\n',
        '        f"- Source commit: `{report[\'sourceCommit\']}`",\n        f"- Mirror authority: `{report.get(\'mirrorSource\', \'HEAD\')}`",\n',
        "markdown authority",
    )
    SCRIPT.write_text(script, encoding="utf-8")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    workflow = replace_once(
        workflow,
        "      - name: Fetch shadow branch refs read-only\n",
        "      - name: Fetch production authority and shadow branch refs read-only\n",
        "fetch step name",
    )
    workflow = replace_once(
        workflow,
        "          git fetch --no-tags origin \\\n            +refs/heads/release-state:refs/remotes/origin/release-state \\\n            +refs/heads/distribution:refs/remotes/origin/distribution\n",
        "          git fetch --no-tags origin \\\n            +refs/heads/main:refs/remotes/origin/main \\\n            +refs/heads/release-state:refs/remotes/origin/release-state \\\n            +refs/heads/distribution:refs/remotes/origin/distribution\n",
        "fetch refs",
    )
    workflow = replace_once(
        workflow,
        "            --json-output shadow-branch-evidence/shadow-branch-parity.json \\\n            --markdown-output shadow-branch-evidence/shadow-branch-parity.md \\\n",
        "            --json-output shadow-branch-evidence/shadow-branch-parity.json \\\n            --markdown-output shadow-branch-evidence/shadow-branch-parity.md \\\n            --mirror-source refs/remotes/origin/main \\\n",
        "workflow mirror source",
    )
    WORKFLOW.write_text(workflow, encoding="utf-8")

    test = TEST.read_text(encoding="utf-8")
    test = replace_once(
        test,
        '            "Mirrored paths must remain byte-identical",\n',
        '            "Mirrored paths must remain byte-identical",\n            "--mirror-source",\n            "mirrorSource",\n',
        "script test markers",
    )
    test = replace_once(
        test,
        '            "Fetch shadow branch refs read-only",\n',
        '            "Fetch production authority and shadow branch refs read-only",\n            "+refs/heads/main:refs/remotes/origin/main",\n',
        "workflow test markers",
    )
    test = replace_once(
        test,
        '            "+refs/heads/distribution:refs/remotes/origin/distribution",\n',
        '            "+refs/heads/distribution:refs/remotes/origin/distribution",\n            "--mirror-source refs/remotes/origin/main",\n',
        "workflow argument marker",
    )
    TEST.write_text(test, encoding="utf-8")
    print("v6 candidate-aware shadow parity contract reconciled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
