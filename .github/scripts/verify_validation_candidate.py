#!/usr/bin/env python3
"""Verify an immutable canonical-validation candidate artifact."""
from __future__ import annotations
import argparse, hashlib, json, re, tempfile
from pathlib import Path

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
SOURCE_VERSION_RE = re.compile(r"^//\s*@version\s+([^\s]+)", re.MULTILINE)

def fail(message: str) -> None:
    raise AssertionError(message)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def verify(evidence_path: Path, source_path: Path, dist_dir: Path, expected_commit: str,
           expected_ref: str, expected_version: str | None = None) -> dict:
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    manifest_path = dist_dir / "release-manifest.json"
    user_path = dist_dir / "MissionChief_Map_Command_Toolkit.user.js"
    text_path = dist_dir / "MissionChief_Map_Command_Toolkit.txt"
    sums_path = dist_dir / "SHA256SUMS.txt"
    for path in (source_path, manifest_path, user_path, text_path, sums_path):
        if not path.is_file():
            fail(f"Required candidate file is missing: {path}")
    if evidence.get("schemaVersion") != 1:
        fail("Validation evidence schemaVersion must be 1")
    if evidence.get("state") != "validated":
        fail("Validation evidence state must be validated")
    if evidence.get("workflow") != "Validate Canonical Userscript":
        fail("Validation evidence workflow identity changed")
    if evidence.get("sourceCommit") != expected_commit:
        fail("Validation evidence sourceCommit does not match the triggering commit")
    if evidence.get("sourceRef") != expected_ref:
        fail("Validation evidence sourceRef does not match the expected ref")
    if evidence.get("storage") != {
        "type": "workflow-artifact",
        "publicMainChanged": False,
        "releaseDashboardChanged": False,
    }:
        fail("Validation evidence storage contract changed")
    version = str(evidence.get("version") or "")
    if not VERSION_RE.fullmatch(version):
        fail(f"Validation evidence contains an invalid version: {version!r}")
    if expected_version is not None and version != expected_version:
        fail(f"Validation evidence version {version} does not match expected {expected_version}")
    source_text = source_path.read_text(encoding="utf-8")
    source_match = SOURCE_VERSION_RE.search(source_text)
    if not source_match or source_match.group(1).strip() != version:
        fail("Canonical source @version does not match validation evidence")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if str(manifest.get("version") or "") != version:
        fail("Distribution manifest version does not match validation evidence")
    source_hash, user_hash, text_hash = sha256(source_path), sha256(user_path), sha256(text_path)
    manifest_hash, evidence_hash = str(manifest.get("sha256") or ""), str(evidence.get("sha256") or "")
    if len({source_hash, user_hash, text_hash, manifest_hash, evidence_hash}) != 1:
        fail("Canonical source, distribution files, manifest and evidence hashes differ")
    expected_distribution = {
        "userScript": "dist/MissionChief_Map_Command_Toolkit.user.js",
        "text": "dist/MissionChief_Map_Command_Toolkit.txt",
        "checksums": "dist/SHA256SUMS.txt",
        "manifest": "dist/release-manifest.json",
    }
    if evidence.get("distribution") != expected_distribution:
        fail("Validation evidence distribution inventory changed")
    expected_sum_lines = {
        f"{user_hash}  MissionChief_Map_Command_Toolkit.user.js",
        f"{text_hash}  MissionChief_Map_Command_Toolkit.txt",
    }
    if set(sums_path.read_text(encoding="utf-8").splitlines()) != expected_sum_lines:
        fail("Candidate checksum file does not match the validated distribution")
    return {"version": version, "sha256": source_hash, "sourceCommit": expected_commit,
            "sourceRef": expected_ref, "state": "validated"}

def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="mcms-validation-candidate-") as temp_dir:
        root = Path(temp_dir); source = root / "src.user.js"; dist = root / "dist"; dist.mkdir()
        payload = b"// ==UserScript==\n// @version 1.2.3\n// ==/UserScript==\nconsole.log('ok');\n"
        source.write_bytes(payload)
        user = dist / "MissionChief_Map_Command_Toolkit.user.js"
        text = dist / "MissionChief_Map_Command_Toolkit.txt"
        user.write_bytes(payload); text.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        (dist / "SHA256SUMS.txt").write_text(
            f"{digest}  {user.name}\n{digest}  {text.name}\n", encoding="utf-8")
        (dist / "release-manifest.json").write_text(
            json.dumps({"version": "1.2.3", "sha256": digest}) + "\n", encoding="utf-8")
        evidence = root / "validation-candidate.json"
        evidence.write_text(json.dumps({
            "schemaVersion": 1, "state": "validated", "workflow": "Validate Canonical Userscript",
            "sourceCommit": "abc123", "sourceRef": "refs/heads/main", "eventName": "push",
            "version": "1.2.3", "sha256": digest,
            "distribution": {
                "userScript": "dist/MissionChief_Map_Command_Toolkit.user.js",
                "text": "dist/MissionChief_Map_Command_Toolkit.txt",
                "checksums": "dist/SHA256SUMS.txt",
                "manifest": "dist/release-manifest.json"},
            "storage": {"type": "workflow-artifact", "publicMainChanged": False,
                        "releaseDashboardChanged": False}}) + "\n", encoding="utf-8")
        assert verify(evidence, source, dist, "abc123", "refs/heads/main", "1.2.3")["sha256"] == digest
        mutated = json.loads(evidence.read_text()); mutated["sourceCommit"] = "wrong"
        evidence.write_text(json.dumps(mutated))
        try:
            verify(evidence, source, dist, "abc123", "refs/heads/main", "1.2.3")
        except AssertionError:
            pass
        else:
            raise AssertionError("Mutated validation evidence was accepted")
    print("Validation candidate verifier self-tests passed.")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path); parser.add_argument("--source", type=Path)
    parser.add_argument("--dist-dir", type=Path); parser.add_argument("--expected-commit")
    parser.add_argument("--expected-ref"); parser.add_argument("--expected-version")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test(); return 0
    required = {"--evidence": args.evidence, "--source": args.source, "--dist-dir": args.dist_dir,
                "--expected-commit": args.expected_commit, "--expected-ref": args.expected_ref}
    missing = [name for name, value in required.items() if value in (None, "")]
    if missing:
        raise SystemExit("Missing required arguments: " + ", ".join(missing))
    print(json.dumps(verify(args.evidence, args.source, args.dist_dir, args.expected_commit,
                            args.expected_ref, args.expected_version), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
