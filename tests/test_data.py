"""Benchmarks and curated data: every shipped file loads and has its expected row count (sources: PROVENANCE.md)."""
import collections
import csv
import gzip
import json
import os
import random

import pytest
from conftest import ROOT

from acx import data
from acx.core.words import Presentation
from acx.search import search
from acx.verify.replay import abs_det

LADDER = "benchmark/ladder"
SPLIT = "benchmark/splits/splits_ac1m_hard_aut.json"

# Nested ladder panels. The 99 / 188 / 268 / 377 sizes are population caps (see LADDER.md).
LADDER_SIZES = {20: 20, 40: 40, 60: 60, 100: 99, 200: 188, 300: 268, 500: 377}
S20HARD_SIZES = {20: 20, 40: 40, 60: 60, 100: 99, 200: 188, 300: 268}


def path(rel):
    return os.path.join(ROOT, rel)


def read_csv(rel):
    with open(path(rel), newline="") as f:
        return list(csv.DictReader(f))


def read_json(rel):
    with open(path(rel)) as f:
        return json.load(f)


@pytest.mark.parametrize("name,n", [("bench10", 10), ("bench20", 20), ("bench40", 40), ("bench60", 60)])
def test_benchmark_subsets(name, n):
    assert len(data.load_csv(name)) == n


@pytest.mark.parametrize("size", sorted(LADDER_SIZES))
def test_ladder_panel(size):
    rows = data.load_csv(f"{LADDER}/ladder_{size}.csv")
    assert len(rows) == LADDER_SIZES[size]
    assert {int(r.meta["level"]) for r in rows} <= set(range(1, 11))


@pytest.mark.parametrize("size", sorted(S20HARD_SIZES))
def test_ladder_s20hard_panel(size):
    assert len(data.load_csv(f"{LADDER}/ladder_{size}_s20hard.csv")) == S20HARD_SIZES[size]


def test_ladder_200_level_counts():
    levels = collections.Counter(int(r["level"]) for r in read_csv(f"{LADDER}/ladder_200.csv"))
    assert [levels[k] for k in range(1, 11)] == [20] * 8 + [19, 9]


def test_ladder_subsets_nest():
    names = [{r["name"] for r in read_csv(f"{LADDER}/ladder_{k}.csv")} for k in sorted(LADDER_SIZES)]
    assert all(a <= b for a, b in zip(names, names[1:]))


@pytest.mark.parametrize("rel,n", [
    (f"{LADDER}/unsolved_124.csv", 124),
    (f"{LADDER}/unsolved_all_forms.csv", 1059),
    (f"{LADDER}/originals_45.csv", 45),
    ("data/ms_unsolved_reps/aca_124_initial.csv", 124),
    ("data/ms_unsolved_reps/aca_124_reduced.csv", 124),
    ("data/ms_unsolved_reps/aca_124_best.csv", 124),
    ("benchmark/difficulty_bins.csv", 640),
])
def test_csv_row_count(rel, n):
    assert len(data.load_csv(rel)) == n


def test_difficulty_bins_cover_ms640():
    rows = data.load_csv("benchmark/difficulty_bins.csv")
    assert {r.id for r in rows} == {str(i) for i in range(640)}


def test_ladder_pairs_table():
    rows = read_csv(f"{LADDER}/ladder_pairs.csv")
    assert len(rows) == 45 and len({r["orig_name"] for r in rows}) == 45


def test_ladder_manifest_pool_size():
    assert read_json(f"{LADDER}/ladder_manifest.json")["rows"] == 73464


def test_certificates_check():
    from acx.aut.equivalence import check, check_side
    assert check(path("data/equivalence_classes/certificates.json")) == dict(
        classes=124, presentations=261, cv=93, ac=44, pure_ac=6)
    edge = next(e for c in read_json("data/equivalence_classes/certificates.json")["classes"]
                for e in c["edges"] if e["side_a"]["steps"])
    bad = dict(edge["side_a"], steps=[dict(edge["side_a"]["steps"][0], phi={"x": "xx", "y": "y"})])
    with pytest.raises(ValueError):
        check_side(bad)


@pytest.mark.parametrize("forge", ["drop_edge", "flip_pure"])
def test_certificates_check_rejects_a_forged_class(tmp_path, forge):
    """A class whose edges do not connect its members, or a wrong ``pure_ac_path`` flag, is rejected."""
    from acx.aut.equivalence import check
    doc = read_json("data/equivalence_classes/certificates.json")
    c = next(c for c in doc["classes"] if c["size"] > 1)
    if forge == "drop_edge":
        c["edges"].pop()
    else:
        c["edges"][0]["pure_ac_path"] = not c["edges"][0].get("pure_ac_path")
    forged = tmp_path / "certificates.json"
    forged.write_text(json.dumps(doc))
    with pytest.raises(ValueError):
        check(str(forged))


def test_ac1m_aut_min_rows():
    rows = data.rows("ac1m_autmin")
    assert len(rows) == 71283 and rows[0].id == "ac1m_0"
    with gzip.open(path("data/AC1M_aut_min.csv.gz"), "rt") as f:
        assert sum(1 for _ in csv.DictReader(f)) == 71283


@pytest.mark.parametrize("name,n", [("ms640", 640), ("bench60", 60), ("ladder20", 20), ("ladder300_s20hard", 268),
                                    ("ac1m_hard_holdout60", 60), ("u124", 124), ("ac19_autmin", 72779)])
def test_rows_by_name(name, n):
    assert len(data.rows(name)) == n


def test_families():
    assert data.AK(3).strs == ("xyxYXY", "xxxYYYY")
    assert data.MS(3, "YXyxy").strs == ("XyyyxYYYY", "XYXyxy")


def test_ac1m_hard_aut_train_and_holdout():
    holdout = data.load_split(SPLIT, "holdout")
    train = data.load_split(SPLIT, "train")
    assert (len(holdout), len(train)) == (60, 120)
    assert not {r.id for r in holdout} & {r.id for r in train}


@pytest.mark.parametrize("part", ["holdout", "train"])
def test_ac1m_hard_aut_rows_match_ac1m_lines(part):
    rows = data.load_split(SPLIT, part)
    lines = data.load("ac1m", ids=[r.id for r in rows])
    assert [r.pres for r in rows] == [r.pres for r in lines]


def test_certificates_summary_edge_types():
    s = read_json("data/equivalence_classes/certificates.json")["summary"]
    assert (s["presentations"], s["classes"], s["edges"]) == (261, 124, 137)
    assert s["cv_edges"] + s["ac_edges"] == s["edges"]


def test_u124_best_is_initial_with_36_shorter_rows():
    total = {k: sum(len(r["r1"]) + len(r["r2"]) for r in read_csv(f"data/ms_unsolved_reps/aca_124_{k}.csv"))
             for k in ("initial", "best")}
    assert (total["initial"], total["best"]) == (2446, 2356)
    reduced = read_csv("data/ms_unsolved_reps/aca_124_reduced.csv")
    assert sum(r["reduced"] == "yes" for r in reduced) == 36


def level_of(g, edge=2253802):
    bands = [1000, 10000, 31623, 100000, 316228, 1000000, edge, 10000001]
    return next(k + 1 for k, hi in enumerate(bands) if g < hi)


@pytest.mark.parametrize("size", sorted(LADDER_SIZES))
def test_ladder_levels_follow_recorded_greedy_nodes(size):
    for r in read_csv(f"{LADDER}/ladder_{size}.csv"):
        if r["greedy_solved"] == "1":
            assert level_of(int(r["greedy_nodes"])) == int(r["level"]), r["name"]
        else:
            assert int(r["level"]) >= 9, r["name"]


def test_ladder_rows_equal_their_source_rows():
    autmin = {r["name"]: (r["r1"], r["r2"]) for r in read_csv("data/AC19_extended_aut_min.csv")}
    ms640 = data.load("ms640")
    for r in read_csv(f"{LADDER}/ladder_500.csv"):
        if r["source"] == "ac19":
            assert autmin[r["name"]] == (r["r1"], r["r2"]), r["name"]
        else:
            assert ms640[int(r["name"].split("_")[1])].pres.strs == (r["r1"], r["r2"]), r["name"]


def test_every_loaded_presentation_is_balanced():
    for rel in ("ladder/ladder_500.csv", "ladder/unsolved_all_forms.csv", "../data/ms_unsolved_reps/aca_124_best.csv"):
        assert all(abs_det(r.pres) == 1 for r in data.load_csv(f"benchmark/{rel}")), rel
    assert all(abs_det(r.pres) == 1 for r in data.load_split(SPLIT, "holdout") + data.load_split(SPLIT, "train"))


def test_search_reproduces_recorded_ladder_pops():
    """The spec backend, at each row's recorded cap, pops exactly the recorded greedy node count."""
    rows = [r for r in read_csv(f"{LADDER}/ladder_60.csv") if r["greedy_solved"] == "1" and int(r["greedy_nodes"]) <= 1000]
    assert len(rows) >= 5
    for r in rows:
        res = search([r["r1"], r["r2"]], cap=int(r["greedy_cap"]), budget=1001)
        assert (res.solved, res.pops) == (True, int(r["greedy_nodes"])), r["name"]


# --- Your own files: LETTERS .txt lines, .csv with r1..rN, .jsonl (the formats are in the acx/data.py docstring) ---

AK2 = Presentation(2, ((1, 1, -2, -2, -2), (1, 2, 1, -2, -1, -2)))             # xxYYY, xyxYXY
AK3 = Presentation(2, ((1, 2, 1, -2, -1, -2), (1, 1, 1, -2, -2, -2, -2)))      # xyxYXY, xxxYYYY
THREE = Presentation(3, ((1, 2), (2, 3), (3,)))                                 # xy, yz, z

LETTERS = """\
# Akbulut-Kirby, n = 2 and 3
xxYYY, xyxYXY

xyxYXY xxxYYYY   # relators split by a space
"""

JSONL = """\
{"id": "AK2", "relators": ["xxYYY", "xyxYXY"], "note": "easy", "levels": [1, 2]}

{"relators": ["xyxYXY", "xxxYYYY"]}
{"id": 7, "relators": ["xy", "yz", "z"]}
"""

SAME_TWO = {"txt": "xxYYY, xyxYXY\nxyxYXY, xxxYYYY\n",
            "csv": "r1,r2\nxxYYY,xyxYXY\nxyxYXY,xxxYYYY\n",
            "jsonl": '{"relators": ["xxYYY", "xyxYXY"]}\n{"relators": ["xyxYXY", "xxxYYYY"]}\n'}


def write(tmp_path, name, text):
    """The file ``name`` holding ``text`` (gzipped if the name ends in .gz); its path as a string."""
    p = tmp_path / name
    if name.endswith(".gz"):
        with gzip.open(p, "wt", newline="") as f:
            f.write(text)
    else:
        p.write_text(text)
    return str(p)


def error_of(path):
    """The message of the ``ValueError`` that reading ``path`` raises."""
    with pytest.raises(ValueError) as e:
        data.rows(path)
    return str(e.value)


@pytest.mark.parametrize("text", ["xxYYY, xyxYXY", "xxYYY,xyxYXY", "xxYYY xyxYXY", "  xxYYY ,\txyxYXY ,  "])
def test_parse_presentation_separators(text):
    assert data.parse_presentation(text) == AK2


def test_parse_presentation_generators_and_inverses():
    assert data.parse_presentation("xy, yz, z") == THREE
    assert data.parse_presentation("XYZ a") == Presentation(4, ((-1, -2, -3), (4,)))     # x y z a b ...; upper case inverts
    assert data.parse_presentation("xyxYXY").n_gen == 2                                  # never fewer than two generators


@pytest.mark.parametrize("text,fragment", [("", "no relators"), (" , ,", "no relators"), ("xy1X", "'1'"),
                                           ("x-y", "'-'"), ("x|y", "'|'"), ("xéy", "'é'"), ("xg0", "'0'"),
                                           ("g5", "'g5' is not a name")])
def test_parse_presentation_rejects_what_is_not_a_presentation(text, fragment):
    with pytest.raises(ValueError) as e:
        data.parse_presentation(text)
    assert fragment in str(e.value)


def test_parse_presentation_reads_generators_past_the_26th():
    """``g27``, ``G27`` (its inverse), ... as ``acx.core.words`` prints them."""
    assert data.parse_presentation("g27x, G27g28") == Presentation(28, ((27, 1), (-27, 28)))


@pytest.mark.parametrize("pres", [AK2, AK3, THREE, data.AK(3), data.MS(3, "YXyxy"),
                                  Presentation(27, ((27, -1), (1,), (-27, 26)))])
def test_parse_presentation_reads_what_strs_prints(pres):
    assert data.parse_presentation(", ".join(pres.strs)) == pres


@pytest.mark.parametrize("line", ["[1, 2, 0, 0, -2, 1, 0, 0]", "(1, 2, 0, 0, -2, 1, 0, 0)", " 1,2,0,0,-2,1,0,0 "])
def test_parse_line_flat_ints_and_letters(line):
    assert data.parse_line(line) == Presentation(2, ((1, 2), (-2, 1)))
    assert data.parse_line("xxYYY, xyxYXY") == AK2


@pytest.mark.parametrize("name,newline", [("mine.txt", "\n"), ("mine.txt.gz", "\n"), ("crlf.txt", "\r\n")])
def test_txt_letters_comments_blank_lines_and_ids(tmp_path, name, newline):
    rows = data.rows(write(tmp_path, name, LETTERS.replace("\n", newline)))
    assert [(r.id, r.pres, r.meta) for r in rows] == [("0", AK2, {}), ("1", AK3, {})]      # ids count presentations


def test_txt_flat_ints_and_letters_can_share_a_file(tmp_path):
    with open(path("data/ms640_solved.txt")) as f:
        flat = f.readline().strip()
    ms0 = data.load("ms640")[0].pres
    rows = data.rows(write(tmp_path, "mixed.txt", f"{flat}\n{', '.join(ms0.strs)}  # the same row, as letters\n"))
    assert [r.pres for r in rows] == [ms0, ms0]


def test_load_ids_pick_presentations_by_position_in_the_requested_order(tmp_path):
    assert [r.id for r in data.load("ms640", ids=[3, 1, 3])] == ["3", "1", "3"]
    assert [r.pres for r in data.load(write(tmp_path, "mine.txt", LETTERS), ids=["1", 0])] == [AK3, AK2]


@pytest.mark.parametrize("line", ["xy1X, y", "x|y", "[1, 7]", "1, 2, 3", "1 2", "[x, y]"])
def test_bad_txt_line_is_a_valueerror_with_its_file_line(tmp_path, line):
    p = write(tmp_path, "bad.txt", f"# header\nxxYYY, xyxYXY\n\n{line}\n")           # the bad line is physical line 4
    assert error_of(p).startswith(f"{p}:4: ")


def test_csv_any_number_of_relator_columns_ids_and_meta(tmp_path):
    p = write(tmp_path, "mine.csv", "id,r1,r2,r3,note\nAK2,xxYYY,xyxYXY,,easy\nthree,xy,yz,z,3 generators\n")
    rows = data.rows(p)
    assert [(r.id, r.pres) for r in rows] == [("AK2", AK2), ("three", THREE)]               # a blank cell is no relator
    assert [r.meta["note"] for r in rows] == ["easy", "3 generators"]
    assert not {"r1", "r2", "r3"} & rows[0].meta.keys()


def test_csv_relator_columns_are_ordered_by_their_number(tmp_path):
    assert data.rows(write(tmp_path, "mine.csv", "r10,r2,r1\nz,yz,xy\n"))[0].pres == THREE


def test_csv_spaces_after_commas_are_ignored(tmp_path):
    rows = data.rows(write(tmp_path, "mine.csv", "id, r1, r2\nAK2, xxYYY, xyxYXY\n"))
    assert [(r.id, r.pres) for r in rows] == [("AK2", AK2)]


@pytest.mark.parametrize("header,row,expected", [
    ("id,name,pres_id,r1,r2", "a,b,c,xx,yy", "a"),
    ("name,pres_id,r1,r2", "b,c,xx,yy", "b"),
    ("pres_id,r1,r2", "c,xx,yy", "c"),
    ("r1,r2", "xx,yy", "0"),
    ("id,r1,r2", ",xx,yy", "0")])
def test_csv_row_id_is_id_then_name_then_pres_id_then_position(tmp_path, header, row, expected):
    assert data.rows(write(tmp_path, "ids.csv", f"{header}\n{row}\n"))[0].id == expected


def test_csv_meta_keeps_every_column_but_the_relators():
    row = data.load_csv("benchmark/ladder/ladder_20.csv")[0]
    assert row.id == row.meta["name"] == "ac19_6582" and "r1" not in row.meta


@pytest.mark.parametrize("name,text,row_id", [("excel.csv", "id,r1,r2\nAK2,xxYYY,xyxYXY\n", "AK2"),
                                              ("notepad.txt", "xxYYY, xyxYXY\n", "0"),
                                              ("notepad.jsonl", '{"id": "AK2", "relators": ["xxYYY", "xyxYXY"]}\n', "AK2")])
def test_a_byte_order_mark_is_ignored(tmp_path, name, text, row_id):
    (tmp_path / name).write_bytes(b"\xef\xbb\xbf" + text.encode())                  # what spreadsheets and Notepad write
    assert [(r.id, r.pres) for r in data.rows(str(tmp_path / name))] == [(row_id, AK2)]


NOT_UTF8 = {
    "latin1.txt": b"xxYYY, xyxYXY  # caf\xe9\n",
    "latin1.csv": b"id,r1,r2\ncaf\xe9,xxYYY,xyxYXY\n",
    "latin1.jsonl": b'{"id": "caf\xe9", "relators": ["xxYYY", "xyxYXY"]}\n',
    "utf16.txt": "xxYYY, xyxYXY\n".encode("utf-16"),                          # what a PowerShell redirect writes
    "latin1.txt.gz": gzip.compress(b"xxYYY, xyxYXY  # caf\xe9\n"),
    "cut.txt": "xxYYY, xyxYXY  # é\n".encode()[:-2],                            # a UTF-8 letter cut in two
    "late.txt": b"xxYYY, xyxYXY\n" * 5000 + b"# caf\xe9\n"}                   # far past the first chunk that is read


@pytest.mark.parametrize("name", NOT_UTF8)
def test_a_file_that_is_not_utf8_is_a_valueerror_naming_it(tmp_path, name):
    (tmp_path / name).write_bytes(NOT_UTF8[name])
    message = error_of(str(tmp_path / name))
    assert message.startswith(f"{tmp_path / name}: ") and "UTF-8" in message


@pytest.mark.parametrize("name,raw", [("fake.txt.gz", b"xxYYY, xyxYXY\n"),                    # plain text, .gz name
                                      ("cut.txt.gz", gzip.compress(b"xxYYY, xyxYXY\n" * 50)[:-12])])   # cut short
def test_a_gz_file_that_is_not_whole_gzip_is_a_valueerror_naming_it(tmp_path, name, raw):
    (tmp_path / name).write_bytes(raw)
    message = error_of(str(tmp_path / name))
    assert message.startswith(f"{tmp_path / name}: ") and "gzip" in message


def test_utf8_beyond_ascii_still_loads(tmp_path):
    (tmp_path / "mine.txt").write_bytes("xxYYY, xyxYXY  # Akbulut–Kirby é\n".encode())
    assert [r.pres for r in data.rows(str(tmp_path / "mine.txt"))] == [AK2]


def test_csv_without_relator_columns_is_a_clear_error(tmp_path):
    for p in (write(tmp_path, "mine.csv", "id,a,b\n1,xx,yy\n"), write(tmp_path, "empty.csv", ""),
              path("benchmark/ladder/ladder_pairs.csv")):                               # a shipped table, not a benchmark
        assert "no relator columns" in error_of(p)


@pytest.mark.parametrize("row", ["bad,xx1,yy", "none,,", "x,xx|y,yy"])
def test_bad_csv_row_is_a_valueerror_with_its_file_line(tmp_path, row):
    p = write(tmp_path, "bad.csv", f"id,r1,r2\nok,xxYYY,xyxYXY\n{row}\n")
    assert error_of(p).startswith(f"{p}:3: ")


@pytest.mark.parametrize("name", ["mine.jsonl", "mine.jsonl.gz"])
def test_jsonl_ids_meta_and_blank_lines(tmp_path, name):
    rows = data.rows(write(tmp_path, name, JSONL))
    assert [(r.id, r.pres) for r in rows] == [("AK2", AK2), ("1", AK3), ("7", THREE)]        # no id: the position
    assert [r.meta for r in rows] == [{"note": "easy", "levels": [1, 2]}, {}, {}]


@pytest.mark.parametrize("line", ['{"relators": ["xx1", "y"]}', '{"id": "a"}', '{"relators": "xxYYY, xyxYXY"}',
                                  '{"relators": []}', '{"relators": ["xx", 5]}', '{"relators": [true, "yy"]}',
                                  '["xx", "y"]', '{"relators": ["xx",', "xxYYY, xyxYXY"])
def test_bad_jsonl_line_is_a_valueerror_with_its_file_line(tmp_path, line):
    p = write(tmp_path, "bad.jsonl", '{"relators": ["xxYYY", "xyxYXY"]}\n' + line + "\n")
    assert error_of(p).startswith(f"{p}:2: ")


@pytest.mark.parametrize("name,text,line,first", [
    ("dup.csv", "id,r1,r2\na,xx,yy\nb,xx,yy\na,xx,yy\n", 4, 2),
    ("dup.jsonl", '{"id": "a", "relators": ["xx"]}\n{"id": "b", "relators": ["xx"]}\n{"id": "a", "relators": ["xx"]}\n', 3, 1),
    ("pos.jsonl", '{"id": "1", "relators": ["xx"]}\n{"relators": ["xx"]}\n', 2, 1)])     # row 1 without an id is "1"
def test_duplicate_row_ids_are_rejected_naming_both_lines(tmp_path, name, text, line, first):
    p = write(tmp_path, name, text)
    message = error_of(p)
    assert message.startswith(f"{p}:{line}: duplicate id") and f"first on line {first}" in message


@pytest.mark.parametrize("kind", sorted(SAME_TWO))
def test_damaged_files_raise_only_a_valueerror_that_names_the_file(tmp_path, kind):
    """Valid files with a few characters replaced: any rows, or a ``ValueError`` starting with the path; nothing else."""
    rng = random.Random(0)
    for i in range(300):
        text = list(SAME_TWO[kind])
        for _ in range(rng.randint(1, 4)):
            text[rng.randrange(len(text))] = rng.choice("xyzXYZ019-,;|[]{}\"' \t#\\é")
        p = write(tmp_path, f"damaged{i}.{kind}", "".join(text))
        try:
            data.rows(p)
        except ValueError as e:
            assert str(e).startswith(p), "".join(text)


@pytest.mark.parametrize("name", ["mine.txt", "mine.txt.gz", "mine.csv", "mine.csv.gz", "mine.jsonl", "mine.jsonl.gz", "MINE.CSV"])
def test_rows_reads_every_format_by_path(tmp_path, name):
    kind = name.lower().removesuffix(".gz").rpartition(".")[2]
    rows = data.rows(write(tmp_path, name, SAME_TWO[kind]))
    assert [(r.id, r.pres) for r in rows] == [("0", AK2), ("1", AK3)]


def test_rows_unknown_name_lists_the_names_and_the_formats():
    with pytest.raises(KeyError) as e:
        data.rows("nope")
    message = e.value.args[0]
    assert "'nope'" in message and all(word in message for word in ("ms640", "bench60", "ac1m_hard_holdout60", ".jsonl"))


def test_rows_accepts_a_path_object(tmp_path):
    write(tmp_path, "mine.txt", LETTERS)
    assert [r.pres for r in data.rows(tmp_path / "mine.txt")] == [AK2, AK3]


@pytest.mark.parametrize("name", ["mine.json", "mine.xlsx", "mine", "mine.txt.bak"])
def test_rows_unsupported_extension(tmp_path, name):
    with pytest.raises(KeyError, match="unknown benchmark"):
        data.rows(write(tmp_path, name, "xx, yy\n"))


@pytest.mark.parametrize("name", ["none.txt", "none.csv", "none.jsonl", "none.txt.gz"])
def test_rows_missing_file_names_the_path(tmp_path, name):
    with pytest.raises(FileNotFoundError, match=name):
        data.rows(str(tmp_path / name))


@pytest.mark.parametrize("name,text", [("empty.txt", ""), ("comments.txt", "# nothing\n\n  # here\n"),
                                       ("blank.jsonl", "\n\n"), ("header.csv", "id,r1,r2\n")])
def test_a_file_without_presentations_has_no_rows(tmp_path, name, text):
    assert data.rows(write(tmp_path, name, text)) == []


def test_relators_are_kept_as_written_and_the_last_line_needs_no_newline(tmp_path):
    rows = data.rows(write(tmp_path, "raw.txt", "xXx, yYy\nxxxYYY yX"))
    assert [r.pres.strs for r in rows] == [("xXx", "yYy"), ("xxxYYY", "yX")]               # not reduced by the loader


def test_relative_paths_start_from_the_current_directory(tmp_path, monkeypatch):
    write(tmp_path, "mine.txt", "xxYYY, xyxYXY\n")
    (tmp_path / "data").mkdir()
    write(tmp_path, "data/ms640_solved.txt", "xy, yz, z\n")                              # a lookalike of a shipped file
    monkeypatch.chdir(tmp_path)
    assert [r.pres for r in data.rows("mine.txt")] == [AK2]
    assert len(data.rows("ms640")) == 640                                                # a name is always the shipped file
    assert len(data.rows("benchmark/subsets/benchmark_subset_10.csv")) == 10            # not here: from the repository root


def test_select_picks_rows_of_a_benchmark_by_slice_or_id():
    """``data.select`` sits beside ``rows``; the runner and the rank-n sweep both use it (``acx.runner.select``)."""
    from acx import runner
    rows = data.rows("bench10")
    assert runner.select is data.select
    assert data.select(rows, "1:7:2") == rows[1:7:2] and data.select(rows, None) == data.select(rows, "") == rows
    ids = [rows[3].id, rows[0].id, rows[3].id]
    assert data.select(rows, ", ".join(ids)) == [rows[3], rows[0]]
