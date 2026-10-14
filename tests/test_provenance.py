"""Research runs cannot silently mix implementations; old evidence is not retroactively attributed."""
import json

import pytest

from acx.runner import run
from acx.runner import provenance


def config(path, method="greedy"):
    return dict(name="experiment", method=method, benchmark=str(path), rows="0:1",
                search=dict(backend="spec", budget=1), **({"rankn": {"max_len": 1}} if method == "rankn" else {}))


@pytest.mark.parametrize("method", ["greedy", "rankn"])
def test_run_provenance_guards_resume_and_fresh_replaces_history(tmp_path, monkeypatch, method):
    data = tmp_path / "input.txt"
    data.write_text("x, y\nx, y\n")
    cfg = config(data, method)
    run(cfg, tmp_path, log=lambda *_: None)
    folder = tmp_path / "experiment"
    path = folder / "provenance.json"
    first = json.loads(path.read_text())
    assert first["schema"] == 1 and not first["prior_results_untracked"]
    assert len(first["identity"]["source_sha256"]) == 64
    assert first["identity"]["dependencies"]["numpy"]
    assert first["invocations"][0]["rows"] == "0:1"
    assert first["invocations"][0]["backend"] == "spec"
    run({**cfg, "rows": "1:2"}, tmp_path, log=lambda *_: None)
    assert len(json.loads(path.read_text())["invocations"]) == 2

    original = provenance.snapshot

    def changed(method):
        value = original(method)
        value["identity"]["source_sha256"] = "changed"
        return value

    monkeypatch.setattr(provenance, "snapshot", changed)
    before = {p: p.read_bytes() for p in folder.rglob("*") if p.is_file()}
    with pytest.raises(ValueError, match="another source or runtime"):
        run(cfg, tmp_path, log=lambda *_: None)
    assert {p: p.read_bytes() for p in before} == before
    run(cfg, tmp_path, fresh=True, log=lambda *_: None)
    reset = json.loads(path.read_text())
    assert reset["identity"]["source_sha256"] == "changed" and len(reset["invocations"]) == 1
    assert not reset["prior_results_untracked"]


def test_legacy_resume_records_missing_history(tmp_path):
    data = tmp_path / "input.txt"
    data.write_text("x, y\n")
    cfg = config(data)
    run(cfg, tmp_path, log=lambda *_: None)
    path = tmp_path / "experiment" / "provenance.json"
    path.unlink()                      # a run from before provenance was recorded
    run(cfg, tmp_path, log=lambda *_: None)
    assert json.loads(path.read_text())["prior_results_untracked"]


def test_source_hash_changes_with_contents_not_git_metadata(tmp_path):
    path = tmp_path / "solver.py"
    path.write_text("result = 1\n")
    before = provenance._digest([path], tmp_path)
    path.write_text("result = 2\n")
    assert provenance._digest([path], tmp_path) != before


def test_optional_git_metadata_and_only_relevant_dependencies(monkeypatch):
    monkeypatch.setattr(provenance, "_git", lambda *args: None)
    ordinary, rl = provenance.snapshot("greedy"), provenance.snapshot("rl")
    assert ordinary["source"] == {"git_commit": None, "dirty": None}
    assert "torch" not in ordinary["identity"]["dependencies"]
    assert "torch" in rl["identity"]["dependencies"]


def test_provenance_symlink_is_refused_before_writing(tmp_path):
    target = tmp_path / "target.json"
    target.write_text("preserve me")
    folder = tmp_path / "experiment"
    folder.mkdir()
    (folder / "provenance.json").symlink_to(target)
    with pytest.raises(ValueError, match="symlink"):
        provenance.prepare_provenance(folder, config(tmp_path / "input.txt"), fresh=True)
    assert target.read_text() == "preserve me"
