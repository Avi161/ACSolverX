from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


CHECKER_PATH = Path(__file__).parents[2] / ".scratch" / "depth4_provenance_check.py"
SPEC = spec_from_file_location("depth4_provenance_check", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def test_all_depth_four_low_minority_classes_are_closed() -> None:
    records = CHECKER.low_minority_certificate_records()
    assert len(records) == 24
    assert not any(record.found_target for record in records)
