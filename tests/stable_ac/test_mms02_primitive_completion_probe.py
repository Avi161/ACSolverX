import json
from pathlib import Path

from experiments.stable_ac.mms02_primitive_completion_probe import (
    ALPHABET, DELTA, LIMIT, PHI_B, RAW_B, candidates, parameters_and_controls,
)


def inverse(word):
    return "".join(letter.swapcase() for letter in reversed(word))


def reduced(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def independent_phi(word, b_image="bbAbaB"):
    images = {"a": "b", "A": "B", "b": b_image, "B": inverse(b_image)}
    return reduced("".join(images[letter] for letter in word))


def independent_scan(word, b_image="bbAbaB"):
    height, result = 0, ""
    for letter in word:
        if letter.lower() == "x":
            height += {"x": 1, "X": -1}[letter]
        else:
            exponent = height + 3
            assert exponent >= 0
            image = "a"
            for _ in range(exponent):
                image = independent_phi(image, b_image)
            result += image if letter == "y" else inverse(image)
    assert height == 0
    return reduced(result)


def test_stage_three_completion_inputs_and_three_controls_are_independent():
    assert (RAW_B, DELTA, PHI_B) == ("XyyXYXyxYYxy", "bAbABaBB", "bbAbaB")
    d_word = independent_phi("b")
    u_word = reduced(d_word + inverse("bAbABaBB"))
    v_word = independent_phi(independent_phi(independent_phi("a")))
    assert independent_scan("XyyXYXyxYYxyx") == u_word
    assert (v_word.count("a") - v_word.count("A"), v_word.count("b") - v_word.count("B")) == (0, 4)
    d_pin, u_pin, v_pin, raw_pin, controls, corrupted = parameters_and_controls()
    assert (d_pin, u_pin, v_pin, raw_pin) == (d_word, u_word, v_word, u_word)
    for control, exponent in zip(controls, (2, 0, -2), strict=True):
        d_power = reduced((d_word if exponent >= 0 else inverse(d_word)) * abs(exponent))
        control_u = reduced("b" + d_power + "A")
        w_word = reduced(inverse(independent_phi("b")) + independent_phi(control_u) + "b")
        target = reduced((v_word if exponent >= 0 else inverse(v_word)) * abs(exponent))
        assert w_word == target
        assert control == {"m": exponent, "N": "b", "u": control_u, "W": w_word, "target": target, "passed": True}
    assert independent_scan("XyyXYXyxYYxyx", "bbAba") == corrupted != u_word


def test_completion_candidates_are_exactly_the_first_thousand_reduced_bfs_words():
    assert ALPHABET == "abAB" and LIMIT == 1000
    level, expected = [""], []
    while len(expected) < 1000:
        expected.extend(level)
        level = [word + letter for word in level for letter in "abAB"
                 if not word or word[-1] != letter.swapcase()]
    expected = expected[:1000]
    actual = candidates()
    assert actual == expected
    assert len(actual) == len(set(actual)) == 1000
    assert actual[0] == ""
    assert all(reduced(word) == word for word in actual)


def test_saved_stage_three_completion_has_independent_full_prefix_replay():
    path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/mms02_primitive_completion_stage3_20260905.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["parameters"] == {
        "alphabet": "abAB", "limit": 1000, "stage": 3,
        "raw_B": "XyyXYXyxYYxy", "phi": {"a": "b", "b": "bbAbaB"}, "delta": "bAbABaBB",
    }
    level, words = [""], []
    while len(words) < 1000:
        words.extend(level)
        level = [word + letter for word in level for letter in "abAB"
                 if not word or word[-1] != letter.swapcase()]
    words = words[:1000]
    assert artifact["tested_N"] == words
    assert len(words) == len(set(words)) == 1000
    assert all(reduced(word) == word for word in words)
    d_word = independent_phi("b")
    u_word = reduced(d_word + inverse("bAbABaBB"))
    v_word = independent_phi(independent_phi(independent_phi("a")))
    assert (artifact["d"], artifact["u"], artifact["V"]) == (d_word, u_word, v_word)
    assert artifact["V_abelianization"] == [0, 4]
    assert artifact["raw_Bx_stage_three"] == independent_scan("XyyXYXyxYYxyx") == u_word
    assert independent_scan("xYxYXyyXYxyXy") == ""
    assert independent_scan("xYxYXyyXYxyXy", "bbAba") != ""
    phi_u, hits = independent_phi(u_word), []
    for n_word in words:
        w_word = reduced(inverse(independent_phi(n_word)) + phi_u + n_word)
        a_exponent = w_word.count("a") - w_word.count("A")
        b_exponent = w_word.count("b") - w_word.count("B")
        if a_exponent == 0 and b_exponent % 4 == 0:
            exponent = b_exponent // 4
            target = reduced((v_word if exponent >= 0 else inverse(v_word)) * abs(exponent))
            if w_word == target:
                hits.append({"N": n_word, "m": exponent, "W": w_word})
    assert artifact["hits"] == hits == []
    expected_controls = []
    for exponent in (2, 0, -2):
        d_power = reduced((d_word if exponent >= 0 else inverse(d_word)) * abs(exponent))
        control_u = reduced("b" + d_power + "A")
        w_word = reduced(inverse(independent_phi("b")) + independent_phi(control_u) + "b")
        target = reduced((v_word if exponent >= 0 else inverse(v_word)) * abs(exponent))
        assert w_word == target
        expected_controls.append({"m": exponent, "N": "b", "u": control_u,
                                  "W": w_word, "target": target, "passed": True})
    assert artifact["controls"] == expected_controls
    wrong_raw = independent_scan("XyyXYXyxYYxyx", "bbAba")
    assert wrong_raw != u_word
    assert artifact["corrupted_phi_control"] == {"b_image": "bbAba", "raw_stage": wrong_raw, "rejected": True}
    assert artifact["status"] == "bounded_stage_three_prefix_only"
