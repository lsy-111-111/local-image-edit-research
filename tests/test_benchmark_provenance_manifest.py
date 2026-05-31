from __future__ import annotations

from pathlib import Path

from scripts.common import read_csv_rows
from scripts.validate_benchmark_cases import referenced_asset_paths, validate_provenance_manifest


def test_repo_provenance_manifest_covers_benchmark_assets() -> None:
    cases = read_csv_rows(Path("data/benchmark/benchmark_cases.csv"))
    errors = validate_provenance_manifest(
        Path("data/benchmark/provenance_manifest.csv"),
        required_assets=referenced_asset_paths(cases),
    )

    assert errors == []

def test_unknown_provenance_copyright_status_is_rejected(tmp_path: Path) -> None:
    asset = tmp_path / "asset.png"
    asset.write_bytes(b"asset")
    manifest = tmp_path / "provenance.csv"
    manifest.write_text(
        "asset_path,asset_type,copyright_status,generation_method,generated_by,created_at,sha256,license_notes\n"
        f"{asset.as_posix()},source_image,unknown,synthetic,Codex,2026-05-31,bad,notes\n",
        encoding="utf-8",
    )

    errors = validate_provenance_manifest(manifest)

    assert any("copyright_status=unknown" in error for error in errors)

